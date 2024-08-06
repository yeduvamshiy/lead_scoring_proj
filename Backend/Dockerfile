FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt
RUN python -m spacy download en_core_web_md

COPY . .

# Copy the data files into the Docker image
COPY data/icp1.csv /app/data/icp1.csv
COPY data/icp2.csv /app/data/icp2.csv
COPY data/blacklisted.csv /app/data/blacklisted.csv

CMD ["python", "app.py"]
