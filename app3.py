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

        table_name = 'message_logs'

        # Fetch rows with 'http_status' and 'message_content' columns
        query = f"SELECT id, http_status, message_content FROM {table_name};"
        cursor.execute(query)
        rows = cursor.fetchall()
        
        
        # Initialize parsed_data within the function scope
        parsed_data = []
        compared_data = []
        
        for row in rows:
            id, http_status, message_content_dict = row
            try:
                # Access specific keys in the dictionary
                response_code = message_content_dict.get('responseCode')
                response_message = message_content_dict.get('responseMessage')

                # Append parsed data to the list
                parsed_data.append({
                    'http_status': http_status,
                    'response_code': response_code,
                    'response_message': response_message,
                })

            except Exception as e:
                print(f"Error processing data for http_status {http_status}: {e}")
        
        schema_table_name = 'schema'

        # Fetch rows in schema table
        schema_query = f"SELECT id, scenario, service, http_status, error_message, schema, error_code FROM {schema_table_name};"
        cursor.execute(schema_query)
        schemas = cursor.fetchall()

        #quey again for compare json schema
        table_name = 'message_logs'

        # Fetch rows with 'http_status' and 'message_content' columns
        log_query = f"SELECT message_content FROM {table_name};"
        cursor.execute(log_query)
        logs = cursor.fetchall()
        

        schema_table_name = 'schema'

        # Fetch rows in schema table
        schema_query = f"SELECT schema FROM {schema_table_name};"
        cursor.execute(schema_query)
        schemaz = cursor.fetchall()

        for log in logs:
            message_content = log

            try:
                for scheme in schemaz:
                    schema = scheme
                
                validation = validate(instance=message_content[0], schema=schema[0])
                print("Success")

            except jsonschema.ValidationError as e:
                error = e.schema.get(f"error_msg \n", e.message)
                pass
            print(error)
        
        for data_dict in parsed_data:
            # Accessing key-value pairs in the dictionary
            http_status = data_dict.get('http_status')
            error_message = data_dict.get('response_message')
            rc = data_dict.get('response_code')
            found_match = False  # Flag to check if a match is found for the current data_dict
            # service = None
            # error_code = None
            
            for schema in schemas:
                schema_http_status = schema[3]
                scenario = schema[1]
                service = schema[2]
                error_code = schema[6]
                schema_column_dict = schema[5].get('properties')['responseMessage']['const']

                if http_status == schema_http_status and error_message == schema_column_dict and rc == error_code:
                    compared_data.append({
                        'http_status': http_status,
                        'scenario': scenario,
                        'service': service,
                        'error_code': error_code,
                        'error_message': error_message,
                        'validation' : validation,
                        "passed": True
                    })
                    found_match = True
                    break  # Exit the inner loop once a match is found

            if not found_match:
                compared_data.append({
                    'http_status': http_status,
                    'scenario': "not found",
                    'service': service,
                    'error_code': rc,
                    'error_message': error_message,
                    'validation' : error,
                    "passed": False
         
               })
        print(type(logs))
        # print(type(compared_data))
        # Close the connection  
        connection.close()

        # Render the template with parsed data
        return render_template('index.html', compared_data=compared_data)

    except Exception as e:
        print(f"Error connecting to the database: {e}")
        return "Error connecting to the database"

if __name__ == '__main__':
    app.run(debug=True)
