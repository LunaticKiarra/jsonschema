from flask import Flask, render_template, request, jsonify
from jsonschema import Draft202012Validator
import psycopg2
import psycopg2.extras
import json

app = Flask(__name__)

#List main function
def connect():
    conn = None
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="test",
            user="postgres",
            password="12345678",
            port="5432"
        )
        return conn
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)

#List all required function for Compare feature
def get_schemas_compare():
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT scenario, schema FROM schema")
    schemas_compare = cur.fetchall()
    conn.close()
    return dict(schemas_compare)

#List all required function for Bulk Validator feature
def get_data_schema():
    conn = connect()
    cur = conn.cursor()
    query = f"SELECT id as schema_id, http_status, schema, scenario FROM schema;"
    cur.execute(query)
    data_schema = cur.fetchall()
    conn.close()
    return (data_schema)

def get_data_emails():
    conn = connect()
    cur = conn.cursor()
    query = f"SELECT DISTINCT email FROM message_logs;"
    cur.execute(query)
    data_emails = [row[0] for row in cur.fetchall()]
    conn.close()
    return (data_emails)

#List all required function for Log Checker feature
def get_log_emails():
    conn = connect()
    cur = conn.cursor()
    query = f"SELECT DISTINCT email FROM message_logs;"
    cur.execute(query)
    log_emails = [row[0] for row in cur.fetchall()]
    return jsonify(log_emails)

#List of all routes
@app.route("/", methods=['GET'])
def index():
    return render_template('index.html')

#List of Compare feature routes
@app.route("/compare/get_schema", methods=['GET'])
def get_schema():
    scenario = request.args.get('scenario')
    schemas_compare = get_schemas_compare()
    return jsonify(json.dumps(schemas_compare.get(scenario, "", indent=4)))

@app.route("/compare", methods=['GET', 'POST'])
def compare():
    errors = []
    schemas_compare = get_schemas_compare()
    data = ""
    schema = ""
    if request.method == 'POST':
        data = request.form.get('data')
        schema = schemas_compare[request.form.get('scenario')]
        v = Draft202012Validator(schema)
        errors = [error.message for error in v.iter.errors(json.loads(data))]
        if not errors:
            errors = ["Validation Successful."]
    return render_template('compare1.html', errors=errors, data=data, schemas_compare=schemas_compare, schema=json.dumps(schema, indent=4))

#List of Bulk Validator feature routes
@app.route("/bulk_validator", methods=['GET', 'POST'])
def display_data():
    try:
        logs_data = []
        for email in get_data_emails():
            conn = connect()
            cur = conn.cursor()
            query = f"SELECT id as message_id, http_status, message_content, email FROM message_logs WHERE email = '{email}';"
            cur.execute(query)
            rows = cur.fetchall()

            for row in rows:
                message_id,logs_http_status,message_content_dict,email_row = row
                try:
                    logs_response_code = message_content_dict.get('response_code')
                    logs_response_message = message_content_dict.get('response_message')

                    logs_data.append({
                        'message_id' : message_id,
                        'http_status': logs_http_status,
                        'responseCode': logs_response_code,
                        'responseMessage': logs_response_message,
                        'email': email_row
                    })
                except Exception as e:
                    print(f"Error processing logs data for : {e}")  

        compared_data = []
        for schema in get_data_schema():
            schema_id = schema[0]
            http_status_schema = schema[1]
            scenario_schema = schema[3]
            response_code_schema = schema[2].get('properties')['responseCode']['const']
            response_message_schema = schema[2].get('properties')['responseMessage']['const']

            for logs_data_dict in logs_data:
                validation_result = []
                message_id_logs = logs_data_dict.get('message_id')
                http_status_logs = logs_data_dict.get('http_status')
                response_code_logs = logs_data_dict.get('responseCode')
                response_message_logs = logs_data_dict.get('responseMessage')

                validator = Draft202012Validator(schema[2])
                errors = list(validator.iter_errors(logs_data_dict))

                if errors:
                    for error in errors:
                        validation_result.append(error.message)
                else:
                    validation_result.append("Validation Successful.")
                
                if http_status_schema == http_status_logs and response_code_schema == response_code_logs and response_message_schema == response_message_logs:
                    compared_data.append({
                        'message_id': message_id_logs,
                        'http_status': http_status_logs,
                        'scenario': scenario_schema,
                        'responseCode': response_code_logs,
                        'responseMessage': response_message_logs,
                        'validation': validation_result,
                        'schema_id': schema_id,
                        "Schema" : json.dumps(schema[2], indent=4),
                        "Response" : json.dumps(logs_data_dict, indent=4),
                        'email' : logs_data_dict.get('email')
                    })
                    break

        # Fetch all the emails again before rendering the template
        conn = connect()
        cur = conn.cursor()
        query = f"SELECT DISTINCT email FROM message_logs;"
        cur.execute(query)
        emails = [row[0] for row in cur.fetchall()]
        conn.close()

        return render_template('schema1.html', compared_data=compared_data, emails=emails)
    
    except Exception as e:
        print(f"Error connecting to database : {e}")
        return "Error connecting to the database"
    
@app.route("/bulk_validator/validate", methods=['GET'])
def validate_email():
    email = request.args.get('email')

    try:

        conn = connect()
        cur = conn.cursor()
        query = f"SELECT id as message_id, http_status, message_content, email FROM message_logs WHERE email = '{email}';"
        cur.execute(query)
        rows = cur.fetchall()

        logs_data = []
        for row in rows:
            message_id,logs_http_status,message_content_dict,email_row = row
            try:
                logs_response_code = message_content_dict.get('response_code')
                logs_response_message = message_content_dict.get('response_message')

                logs_data.append({
                    'message_id' : message_id,
                    'http_status': logs_http_status,
                    'responseCode': logs_response_code,
                    'responseMessage': logs_response_message,
                    'email': email_row
                })
            except Exception as e:
                print(f"Error processing logs data for : {e}")

        compared_data = []
        for schema in get_data_schema():
            schema_id = schema[0]
            http_status_schema = schema[1]
            scenario_schema = schema[3]
            response_code_schema = schema[2].get('properties')['responseCode']['const']
            response_message_schema = schema[2].get('properties')['responseMessage']['const']

            for logs_data_dict in logs_data:
                validation_result = []
                message_id_logs = logs_data_dict.get('message_id')
                http_status_logs = logs_data_dict.get('http_status')
                response_code_logs = logs_data_dict.get('responseCode')
                response_message_logs = logs_data_dict.get('responseMessage')

                validator = Draft202012Validator(schema[2])
                errors = list(validator.iter_errors(logs_data_dict))

                if errors:
                    for error in errors:
                        validation_result.append(error.message)
                else:
                    validation_result.append("Validation Successful.")
                
                if http_status_schema == http_status_logs and response_code_schema == response_code_logs and response_message_schema == response_message_logs:
                    compared_data.append({
                        'message_id': message_id_logs,
                        'http_status': http_status_logs,
                        'scenario': scenario_schema,
                        'responseCode': response_code_schema,
                        'responseMessage': response_message_schema,
                        'validation': validation_result,
                        'schema_id': schema_id,
                        "Schema" : json.dumps(schema[2], indent=4),
                        "Response" : json.dumps(logs_data_dict, indent=4),
                        'email' : logs_data_dict.get('email')
                    })
                    break

        query = f"SELECT DISTINCT email FROM message_logs;"
        cur.execute(query)
        emails = [row[0] for row in cur.fetchall()]

        conn.close()

        return render_template('schema1.html', compared_data=compared_data, emails=emails)

    except Exception as e:
        print(f"Error connecting to database : {e}")
        return "Error connecting to the database"
    
#List of Log Checker feature routes
@app.route("/emails", methods=['GET'])
def get_emails():
    return get_log_emails()

@app.route("/logs/<email>", methods=['GET'])
def get_logs(email):
    conn = connect()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT * FROM message_logs WHERE email = %s", (email,))
    logs = [dict(row) for row in cur.fetchall()]

    return render_template('validator1.html', logs=jsonify(logs))
    
if __name__ == '__main__':
    app.run(debug=True)
