JSON Schema Validator
Overview
This program is designed to assist the QA team in validating JSON Schemas for various scenarios. It provides three main features:

Manual JSON Schema Validation: - Allows users to validate a JSON Schema against a provided JSON data input. - Displays the validation result, indicating whether the response is true or false. - Shows detailed error messages if any issues are detected.

Bulk Partner Log Validation: - Enables the validation of a bulk set of partner logs against their corresponding JSON Schemas. - Identifies the scenario that best suits each partner log.

Partner Log Filtering: - Filters partner logs based on a designated partner, making it easier to focus on specific data.

Getting Started
Prerequisites
Make sure you have the following dependencies installed:

Flask
SQLAlchemy
psycopg2
jsonschema
json
Running the Program
Clone the repository:
bash git clone https://ichwanulhakim@bitbucket.org/bridce/automate_partnership.git cd automate-partnership

Install dependencies:
bash pip install -r requirements.txt

Run the main.py file:
bash python main.py

Usage
Manual JSON Schema Validation
Input the JSON Schema and corresponding JSON data manually.
Execute the validation.
Review the result and any error messages displayed.
Bulk Partner Log Validation
Provide a bulk set of partner logs.
Initiate the validation process.
Identify the scenarios that best match each partner log.
Partner Log Filtering
Specify the partner for which you want to filter logs.
Run the filtering process to display logs associated with the designated partner.
