## Lead Scoring Project

This project provides a lead scoring system that allows users to upload a CSV file containing lead data, adjust weights for various factors, and download a scored CSV file.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
  - [Backend Setup](#backend-setup)
  - [Frontend Setup](#frontend-setup)
  - [Docker Setup (Optional)](#docker-setup-optional)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)

## Overview

The Lead Scoring Project aims to simplify the process of scoring leads based on various parameters such as designations, employee count, and engagement. The system is built with a Flask backend and a React frontend, providing an interactive interface for users to manage and score their leads.

This system leverages Sentence-BERT (SBERT), a state-of-the-art model for semantic similarity, to classify designations into predefined categories. This allows for a more accurate and efficient lead scoring process.

## Features

**Advanced Designation Classification**: Utilizes SBERT to accurately classify job titles into predefined categories.

**Customizable Scoring**: Adjust weights for different designations, employee count, and engagement levels.

**CSV Upload and Download**: Easily upload your leads in CSV format and download the scored results.

**Docker Support**: Simplified deployment with Docker.

## Installation

### Backend Setup

1. **Clone the repository:**

```bash
git clone https://github.com/yeduvamshiy/lead_scoring_proj.git
cd lead_scoring_proj
```

2. **Set up a virtual environment:**

```bash
python -m venv venv
source venv/bin/activate  # On Windows use venv\Scripts\activate
```

3. **Install backend dependencies:**

```bash
pip install -r requirements.txt
```

### Frontend Setup

1. **Navigate to the frontend directory and install dependencies:**

```bash
cd lead-scoring-frontend
npm install
```

### Docker Setup (Optional)

1. **Build and run the Docker containers:**

```bash
docker-compose up --build
```

## Usage

1. **Start the backend server:**

```bash
cd Backend
flask run
```

2. **Start the frontend development server:**

```bash
cd ../lead-scoring-frontend
npm start
```

3. **Access the application:**

   Navigate to `http://localhost:3000` in your browser.

4. **Use the application:**

   - Upload a CSV file with lead data.
   - Adjust the weights for different designations and factors.
   - Download the scored CSV file.

## API Endpoints

### GET /routes

List all available endpoints.

### POST /update_weights

Update weights for scoring.

#### Request Body:

```json
{
  "ICP1": {
    "range_50_200": 1.0,
    "range_200_500": 1.2,
    "range_500_100000": 1.5
  },
  "ICP2": {
    "range_50_200": 0.5,
    "range_200_500": 0.6,
    "range_500_100000": 0.75
  },
  "designation_scores": {
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
  },
  "engagement_scores": {
    "yes": 1.0,
    "no": 0.0
  }
}
```

### POST /score

Upload a CSV file and get a scored CSV file.

#### Request:

- Multipart/form-data with the file parameter containing the CSV file.

#### Response:

- CSV file with scores.
