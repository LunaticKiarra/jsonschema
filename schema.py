# app5.py
from flask import Flask, render_template, request
import psycopg2
import json
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
        query = f"SELECT http_status, schema, scenario FROM {table_name1};"
        cursor.execute(query)
        schemas = cursor.fetchall()

        table_name2 = 'message_logs'
        query = f"SELECT DISTINCT email FROM {table_name2};"
        cursor.execute(query)
        emails = [row[0] for row in cursor.fetchall()]

        # query = f"SELECT http_status, message_content, email FROM {table_name2} WHERE email = '{email}';"
        # cursor.execute(query)
        # rows = cursor.fetchall()

        logs_data = []
        for email in emails:
            query = f"SELECT http_status, message_content, email FROM {table_name2} WHERE email = '{email}';"
            cursor.execute(query)
            rows = cursor.fetchall()

            for row in rows:
                logs_http_status, message_content_dict, email_row = row
                try:
                    logs_response_code = message_content_dict.get('responseCode')
                    logs_response_message = message_content_dict.get('responseMessage')

                    logs_data.append({
                        'http_status': logs_http_status,
                        'responseCode': logs_response_code,
                        'responseMessage': logs_response_message,
                        'email': email_row
                    })
                except Exception as e:
                    print(f"Error processing logs data for : {e}")

        compared_data = []
        for schema in schemas:
            http_status_schema = schema[0]
            scenario_schema = schema[2]
            response_code_schema = schema[1].get('properties')['responseCode']['const']
            response_message_schema = schema[1].get('properties')['responseMessage']['const']

            for logs_data_dict in logs_data:
                validation_result = []

                http_status_logs = logs_data_dict.get('http_status')
                response_code_logs = logs_data_dict.get('responseCode')
                response_message_logs = logs_data_dict.get('responseMessage')

                validator = Draft202012Validator(schema[1])
                errors = list(validator.iter_errors(logs_data_dict))

                if errors:  
                     for error in errors:
                        validation_result.append(error.message)
                else:
                    validation_result.append("Validation successful.")

                if http_status_schema == http_status_logs and response_code_schema == response_code_logs and response_message_schema == response_message_logs:
                    compared_data.append({
                        'http_status' : http_status_schema,
                        'scenario' : scenario_schema,
                        'response_code' : response_code_schema,
                        'response_message' : response_message_schema,
                        "Validation" : validation_result,
                        "Schema" : json.dumps(schema[1], indent=4),
                        "Response" : json.dumps(logs_data_dict, indent=4),
                        'email': logs_data_dict.get('email')
                    })
                    break 
       
        # Fetch all the emails again before rendering the template
        query = f"SELECT DISTINCT email FROM {table_name2};"
        cursor.execute(query)
        emails = [row[0] for row in cursor.fetchall()]

        connection.close()

        return render_template('schema.html', compared_data=compared_data, emails=emails)
    
    except Exception as e:
        print(f"Error connecting to database : {e}")
        return "Error connecting to the database"

@app.route('/validate', methods=['GET'])
def validate_email():
    email = request.args.get('email')

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
        query = f"SELECT http_status, schema, scenario FROM {table_name1};"
        cursor.execute(query)
        schemas = cursor.fetchall()

        table_name2 = 'message_logs'
        query = f"SELECT http_status, message_content, email FROM {table_name2} WHERE email = '{email}';"
        cursor.execute(query)
        rows = cursor.fetchall()

        logs_data = []
        for row in rows:
            logs_http_status, message_content_dict, email = row
            try:
                logs_response_code = message_content_dict.get('responseCode')
                logs_response_message = message_content_dict.get('responseMessage')

                logs_data.append({
                    'http_status': logs_http_status,
                    'responseCode': logs_response_code,
                    'responseMessage': logs_response_message,
                    'email': email
                })
            except Exception as e:
                print(f"Error processing logs data for : {e}")

        compared_data = []
        for schema in schemas:
            http_status_schema = schema[0]
            scenario_schema = schema[2]
            response_code_schema = schema[1].get('properties')['responseCode']['const']
            response_message_schema = schema[1].get('properties')['responseMessage']['const']

            for logs_data_dict in logs_data:
                validation_result = []

                http_status_logs = logs_data_dict.get('http_status')
                response_code_logs = logs_data_dict.get('responseCode')
                response_message_logs = logs_data_dict.get('responseMessage')

                validator = Draft202012Validator(schema[1])
                errors = list(validator.iter_errors(logs_data_dict))

                if errors:  
                    for error in errors:
                        validation_result.append(error.message)
                else:
                    validation_result.append("Validation successful.")

                if http_status_schema == http_status_logs and response_code_schema == response_code_logs and response_message_schema == response_message_logs:
                    compared_data.append({
                        'http_status' : http_status_schema,
                        'scenario' : scenario_schema,
                        'response_code' : response_code_schema,
                        'response_message' : response_message_schema,
                        "Validation" : validation_result,
                        "Schema" : json.dumps(schema[1], indent=4),
                        "Response" : json.dumps(logs_data_dict, indent=4),
                        'email': logs_data_dict.get('email')
                    })
                    break 

        query = f"SELECT DISTINCT email FROM {table_name2};"
        cursor.execute(query)
        emails = [row[0] for row in cursor.fetchall()]

        connection.close()

        return render_template('schema.html', compared_data=compared_data, emails=emails)
    
    except Exception as e:
        print(f"Error connecting to database : {e}")
        return "Error connecting to the database"

if __name__ == '__main__':
    app.run(debug=True)