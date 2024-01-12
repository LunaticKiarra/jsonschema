from flask import Flask, render_template
import psycopg2
import json
import jsonschema
from jsonschema import validate
from jsonschema.exceptions import ValidationError
from jsonschema import Draft3Validator
from jsonschema import Draft202012Validator

app = Flask(__name__)

@app.route('/')
def display_data():
    try:
        # Connect to the database
        database = "test"
        user = "postgres"
        password = "12345678"
        host = "localhost"
        port = "5432"

        connection = psycopg2.connect(
        database=database,
        user=user,
        password=password,
        host=host,
        port=port
        )
        cursor = connection.cursor()

        table_name1 = 'schema'
        # Fetch rows with 'http_status' and 'message_content' columns
        query = f"SELECT http_status, schema, scenario FROM {table_name1};"
        cursor.execute(query)
        schemas = cursor.fetchall()

        table_name2 = 'message_logs'
         # Fetch rows with 'http_status' and 'message_content' columns
        query = f"SELECT http_status, message_content FROM {table_name2};"
        cursor.execute(query)
        rows = cursor.fetchall()

        logs_data = []
        for row in rows:
            logs_http_status, message_content_dict = row
            try:
                logs_response_code = message_content_dict.get('responseCode')
                logs_response_message = message_content_dict.get('responseMessage')

                logs_data.append({
                    'http_status': logs_http_status,
                    'response_code': logs_response_code,
                    'response_message': logs_response_message
                })
            except Exception as e:
                print(f"Error processing logs data for : {e}")

        compared_data = []
        for schema in schemas:
            http_status_schema = schema[0]
            scenario_schema = schema[2]
            response_code_schema = schema[1].get('properties')['responseCode']['const']
            response_message_schema = schema[1].get('properties')['responseMessage']['const']
            found_match = False

            for logs_data_dict in logs_data:
                http_status_logs = logs_data_dict.get('http_status')
                response_code_logs = logs_data_dict.get('response_code')
                response_message_logs = logs_data_dict.get('response_message')

                if http_status_schema == http_status_logs and response_code_schema == response_code_logs and response_message_schema == response_message_logs:
                    compared_data.append({
                        'http_status' : http_status_schema,
                        'scenario' : scenario_schema,
                        'response_code' : response_code_schema,
                        'response_message' : response_message_schema,
                        "Passed" : True
                    })
                    found_match = True
                    break

            if not found_match:
                compared_data.append({
                    'http_status' : http_status_schema,
                    'scenario' : scenario_schema,
                    'response_code' : response_code_schema,
                    'response_message' : response_message_schema,
                    "Passed" : False
                })
        connection.close()

        return render_template('index5.html', compared_data=compared_data)
    
    except Exception as e:
        print(f"Error connecting to database : {e}")
        return "Error connecting to the database"

if __name__ == '__main__':
    app.run(debug=True)

