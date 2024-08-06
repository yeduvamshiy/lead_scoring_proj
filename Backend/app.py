import os
from flask import Flask, request, send_file, jsonify, send_from_directory
from flask_cors import CORS
from flask_compress import Compress
import pandas as pd
from openai import OpenAI
import io
from concurrent.futures import ThreadPoolExecutor
import logging
import time
from openai import APIConnectionError, RateLimitError, APIError, BadRequestError

app = Flask(__name__, static_folder='../lead-scoring-frontend/build', static_url_path='/')
CORS(app)  # Enable CORS for all routes
Compress(app)  # Enable compression

# Enable logging
logging.basicConfig(level=logging.DEBUG)

# Instantiate the OpenAI client
api_key = os.getenv('OPENAI_API_KEY', 'sk-proj-AcrRJhLeM9l0DBll5oNtT3BlbkFJxvmv6go6dPAypF46sOtY')  # Replace with your API key if needed
client = OpenAI(api_key=api_key)

# Define core designations and their corresponding scores
core_designations = {
    "C-Level Executives": 1.5,
    "Vice Presidents of Support or Customer Success": 1.5,
    "Other Vice Presidents": 1.5,
    "Directors of Support or Customer Success": 1.5,
    "Other Directors": 1.2,
    "Managers of Support or Customer Success": 0.8,
    "Other Managers": 0.3,
    "Sales Roles": 0,
    "Other Roles": 0.1,
    "Vice President of Product": 1.2,
    "Vice President of Engineering": 1.2,
    "Head of Product": 1.2,
    "Head of Engineering": 1.2,
    "Engineering Manager": 0.5,
    "Product Manager": 0.5,
    "Founder/Co-founder": 1.5
}

# Define a mapping from core designations to detailed designations
core_to_detailed = {
    "C-Level Executives": ["Chief Executive Officer", "CEO", "Chief Operating Officer", "COO",
                           "Chief Financial Officer", "CFO", "Chief Technology Officer", "CTO",
                           "Chief Marketing Officer", "CMO", "Chief Information Officer", "CIO"],
    "Vice Presidents of Support or Customer Success": ["VP of Support", "VP of Customer Success"],
    "Other Vice Presidents": ["Vice President of Sales", "VP of Sales", "Vice President of Marketing",
                              "VP of Marketing", "Vice President of Operations", "VP of Operations"],
    "Directors of Support or Customer Success": ["Director of Support", "Director of Customer Success"],
    "Other Directors": ["Director of Sales", "Sales Director", "Director of Marketing",
                        "Marketing Director", "Director of Operations", "Operations Director"],
    "Managers of Support or Customer Success": ["Support Manager", "Customer Success Manager"],
    "Other Managers": ["Manager of Sales", "Sales Manager", "Manager of Marketing", "Marketing Manager",
                       "Manager of Operations", "Operations Manager"],
    "Sales Roles": ["Sales Representative", "Sales Executive", "Sales Associate", "Sales Consultant", "Other Sales Roles"],
    "Other Roles": ["Customer Service Representative", "Customer Service Executive", "Customer Service Associate",
                    "Customer Support Representative", "Customer Support Executive", "Customer Support Associate"],
    "Vice President of Product": ["VP of Product"],
    "Vice President of Engineering": ["VP of Engineering"],
    "Head of Product": ["Product Head"],
    "Head of Engineering": ["Engineering Head"],
    "Engineering Manager": ["Engineering Manager"],
    "Product Manager": ["Product Manager"],
    "Founder/Co-founder": ["Founder", "Co-founder"]
}

# Expand core designations to detailed designations
roles_scores = {detail: core_designations[core] for core, details in core_to_detailed.items() for detail in details}
roles_scores.update(core_designations)

ICP1 = []
ICP2 = []
blacklisted_companies = []
employee_count_scores = {
    'ICP1': {range(50, 201): 1, range(200, 501): 1.2, range(500, 100001): 1.5},
    'ICP2': {range(50, 201): 0.5, range(200, 501): 0.6, range(500, 100001): 0.75}
}

engagement_scores = {"yes": 1.0, "no": 0.0}

# Function to get the most similar designation using GPT-4
def get_similar_designation(designation):
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Classify job titles into predefined categories."},
                {"role": "user", "content": f"Classify the following job title into one of these categories: {list(roles_scores.keys())}.\n\nJob title: {designation}"}
            ],
            max_tokens=10
        )
        most_similar_designation = response.choices[0].message['content'].strip()
        return most_similar_designation if most_similar_designation in roles_scores else "Other Roles"
    except RateLimitError:
        time.sleep(1)
        return get_similar_designation(designation)
    except APIError as e:
        logging.error(f"Error in GPT-4 API: {str(e)}")
        return "Other Roles"

# Function to process a single row
def process_row(row):
    designation = row['Designation']
    company = row['Company']
    employee_count = row.get('Employee Count', 0)
    engagement = row.get('Engagement', 'no').strip().lower()
    
    if not isinstance(designation, str):
        designation = str(designation)
    similar_designation = get_similar_designation(designation)
    designation_score = roles_scores.get(similar_designation, 0)
    engagement_score = engagement_scores.get(engagement, 0)
    
    # Calculate ICP and employee count score
    if company in ICP1:
        icp_key = 'ICP1'
    elif company in ICP2:
        icp_key = 'ICP2'
    else:
        return {'Company': company, 'Designation': designation, 'Engagement': engagement, 'Score': 0}

    employee_score = 0
    for range_key, weight in employee_count_scores[icp_key].items():
        if employee_count in range_key:
            employee_score = weight
            break
    
    final_score = designation_score + employee_score + engagement_score
    return {'Company': company, 'Designation': designation, 'Engagement': engagement, 'Score': final_score}

# Endpoint to update weights
@app.route('/update_weights', methods=['POST'])
def update_weights():
    global roles_scores, employee_count_scores, engagement_scores
    updated_weights = request.json
    logging.debug(f"Received updated weights: {updated_weights}")
    
    # Update employee count scores for ICP1 and ICP2
    employee_count_scores['ICP1'][range(50, 201)] = float(updated_weights["ICP1"]["range_50_200"])
    employee_count_scores['ICP1'][range(200, 501)] = float(updated_weights["ICP1"]["range_200_500"])
    employee_count_scores['ICP1'][range(500, 100001)] = float(updated_weights["ICP1"]["range_500_100000"])
    employee_count_scores['ICP2'][range(50, 201)] = float(updated_weights["ICP2"]["range_50_200"])
    employee_count_scores['ICP2'][range(200, 501)] = float(updated_weights["ICP2"]["range_200_500"])
    employee_count_scores['ICP2'][range(500, 100001)] = float(updated_weights["ICP2"]["range_500_100000"])
    
    # Update designation scores
    for core_designation, weight in updated_weights.get("designation_scores", {}).items():
        for detailed_designation in core_to_detailed.get(core_designation, [core_designation]):
            roles_scores[detailed_designation] = float(weight)
    
    logging.debug(f"Updated roles_scores: {roles_scores}")
    
    # Update engagement scores
    engagement_scores['yes'] = float(updated_weights["engagement_scores"]["yes"])
    engagement_scores['no'] = float(updated_weights["engagement_scores"]["no"])
    
    logging.debug(f"Updated engagement_scores: {engagement_scores}")
    return jsonify({"message": "Weights updated successfully"}), 200

# Function to load ICP and blacklist data
def load_icp_and_blacklist_data():
    global ICP1, ICP2, blacklisted_companies
    base_path = os.path.dirname(os.path.abspath(__file__))
    logging.debug(f"Loading ICP and blacklist data from {base_path}")
    try:
        ICP1 = pd.read_csv(os.path.join(base_path, 'data', 'icp1.csv'))['Company name '].tolist()
        ICP2 = pd.read_csv(os.path.join(base_path, 'data', 'icp2.csv'))['Company name '].tolist()
        blacklisted_companies = pd.read_csv(os.path.join(base_path, 'data', 'blacklisted.csv'))['Company name'].tolist()
        logging.debug("ICP and blacklist data loaded successfully")
    except Exception as e:
        logging.error(f"Error loading ICP and blacklist data: {str(e)}")
        raise

# Route to handle scoring
@app.route('/score', methods=['POST'])
def score():
    try:
        file = request.files['file']
        df = pd.read_csv(file)
        logging.debug(f"File loaded with {len(df)} rows.")
        
        # Load ICP and blacklist data
        load_icp_and_blacklist_data()
        
        # Process the DataFrame and calculate scores using ThreadPoolExecutor for parallel processing
        with ThreadPoolExecutor() as executor:
            results = list(executor.map(process_row, [row for _, row in df.iterrows()]))
        
        logging.debug("Completed processing rows.")
        result_df = pd.DataFrame(results)
        
        # Create CSV output
        output = io.StringIO()
        result_df.to_csv(output, index=False)
        output.seek(0)
        
        logging.debug("CSV created and ready for download.")
        return send_file(io.BytesIO(output.getvalue().encode()), mimetype='text/csv', as_attachment=True, download_name='scoring_results.csv')
    
    except Exception as e:
        logging.error(f"Error during processing: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Route to list all available endpoints
@app.route('/routes', methods=['GET'])
def list_routes():
    import urllib
    output = []
    for rule in app.url_map.iter_rules():
        methods = ','.join(rule.methods)
        line = urllib.parse.unquote(f"{rule.endpoint:50s} {methods:20s} {rule}")
        output.append(line)
    return jsonify(output)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react_app(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
