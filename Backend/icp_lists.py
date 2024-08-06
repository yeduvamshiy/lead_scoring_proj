import pandas as pd

# Load the CSV files from the 'data' folder using raw strings
ICP1 = pd.read_csv(r'C:\Users\Devrev\Documents\lead_scoring_proj\Backend\data\icp1.csv')['Company name '].tolist()
ICP2 = pd.read_csv(r'C:\Users\Devrev\Documents\lead_scoring_proj\Backend\data\icp2.csv')['Company name '].tolist()
blacklisted_companies = pd.read_csv(r'C:\Users\Devrev\Documents\lead_scoring_proj\Backend\data\blacklisted.csv')['Company name'].tolist()

employee_count_scores_ICP1 = {range(50, 201): 1, range(200, 501): 1.2, range(500, 100001): 1.5}
employee_count_scores_ICP2 = {range(50, 201): 0.5, range(200, 501): 0.6, range(500, 100001): 0.75}
designation_scores = {
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
