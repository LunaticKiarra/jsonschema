from flask import Flask, request, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
import psycopg2
import psycopg2.extras
from jsonschema import Draft202012Validator
import json
from datetime import datetime

app =Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:12345678@localhost/test'  # Use your actual database URI
db = SQLAlchemy(app)

@app.route("/", methods=['GET'])
def home():
    return render_template('index.html')

def get_db_connection():
    conn = psycopg2.connect(database="test", user="postgres", password="12345678", host="localhost", port="5432")
    return conn

# def get_posts(page, per_page):
#     conn = get_db_connection()
#     cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
#     offset = (page - 1) * per_page
#     cur.execute("SELECT * FROM posts ORDER BY id DESC LIMIT %s OFFSET %s;", (per_page, offset))
#     posts = cur.fetchall()
#     conn.close()
#     return posts

# This is the basic validator code
def get_schemas():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT scenario, schema FROM schema")
    schemas = cur.fetchall()
    conn.close()
    return dict(schemas)

@app.route('/get_schema', methods=['GET'])
def get_schema():
    scenario = request.args.get('scenario')
    schemas = get_schemas()
    return jsonify(json.dumps(schemas.get(scenario, ""), indent=4))

@app.route('/validator', methods=['GET', 'POST'])
def index():
    errors = []
    schemas = get_schemas()
    data = ""
    schema = ""
    if request.method == 'POST':
        scenario = request.form.get('scenario')
        data = request.form.get('data')
        if not scenario:
            errors.append("Please select a scenario")
        if not data:
            errors.append("Please insert data JSON to validate")
        if scenario and data:
            schema = schemas[request.form.get('scenario')]
            v = Draft202012Validator(schema)
            errors = [error.message for error in v.iter_errors(json.loads(data))]
            if not errors:
                errors = ["Validation Successful."]
    return render_template('compare.html', errors=errors, schemas=schemas, data=data, schema=json.dumps(schema, indent=4))

# This is the code for bulk validator
def get_schemaz():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id as schema_id, http_status, schema, scenario FROM schema;")
    schemaz = cur.fetchall()
    return schemaz

def get_emails():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT email FROM message_logs;")
    emails = [row[0] for row in cur.fetchall()]
    return emails
    
@app.route('/validate', methods=['GET'])
def validate_email():
    email = request.args.get('email')
    date_range = request.args.get('date_range')

    # Check if date_range is None
    if date_range is None:
        # Set start_date and end_date to default values
        start_date = '2000-01-01 00:00:00'
        end_date = '2099-12-31 23:59:59'
    else:
        # Split the date_range into a start date and an end date
        start_date, end_date = date_range.split(' - ')
        # Parse the dates and format them in the way PostgreSQL expects
        start_date = datetime.strptime(start_date.strip(), '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')
        end_date = datetime.strptime(end_date.strip(), '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')
    
    # print(f"Start Date: {start_date}, End Date: {end_date}") 

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        query = f"""
        SELECT id as message_id, created_at, http_status, message_content, email 
        FROM message_logs 
        WHERE email = %s 
        AND created_at >= %s::timestamptz
        AND created_at < %s::timestamptz;
        """
        cur.execute(query, (email, start_date, end_date))
        rows = cur.fetchall()

        logs_data = []
        for row in rows:
            message_id,created_at,logs_http_status, message_content_dict, email_row = row
            try:
                    logs_response_code = message_content_dict.get('responseCode')
                    logs_response_message = message_content_dict.get('responseMessage')
                    timestamp = created_at.strftime("%Y-%m-%d %H:%M:%S")
                    message_content = json.dumps(message_content_dict, indent=4)
                    message_content_validator = message_content_dict

                    logs_data.append({
                        'message_id': message_id,
                        'message_content_validator' : message_content_validator,
                        'message_content': message_content,
                        'http_status': logs_http_status,
                        'responseCode': logs_response_code,
                        'responseMessage': logs_response_message,
                        'timestamp': timestamp
                        # 'email': email_row
                    })
            except Exception as e:
                    print(f"Error processing logs data for : {e}")

        compared_data = []
        for schema in get_schemaz():
            schema_id = schema[0]
            schema_http_status = schema[1]
            schema_scenario = schema[3]
            schema_response_code = schema[2].get('properties')['responseCode']['const']
            schema_response_message = schema[2].get('properties')['responseMessage']['const']

            for logs_data_dict in logs_data:
                validation_result = []

                message_id_logs = logs_data_dict.get('message_id')
                http_status_logs = logs_data_dict.get('http_status')
                response_code_logs = logs_data_dict.get('responseCode')
                response_message_logs = logs_data_dict.get('responseMessage')

                validator = Draft202012Validator(schema[2])
                errors = list(validator.iter_errors(logs_data_dict.get('message_content_validator')))

                if errors:
                    for error in errors:
                        validation_result.append(error.message)
                else:
                    validation_result.append("Validation successful.")

                if schema_http_status == http_status_logs and schema_response_code == response_code_logs and schema_response_message == response_message_logs:
                        compared_data.append({
                            'message_id' : message_id_logs,
                            'timestamp' : logs_data_dict.get('timestamp'),
                            'http_status' : schema_http_status,
                            'scenario' : schema_scenario,
                            'response_code' : schema_response_code,
                            'response_message' : schema_response_message,
                            "Validation" : validation_result,
                            "Schema" : json.dumps(schema[2], indent=4),
                            "Response" : logs_data_dict.get('message_content'),
                            # 'email': logs_data_dict.get('email')
                            'email': email_row
                        })
                        break
        
        query = f"SELECT DISTINCT email FROM message_logs;"
        cur.execute(query)
        emails = [row[0] for row in cur.fetchall()]
        
        conn.close()

        return render_template('schema.html', compared_data=compared_data, emails=emails)

    except Exception as e:
        print(f"Error connecting to database : {e}")
        return "Error connecting to the database"
    
# This is the code for checking parter's logs
@app.route('/emails', methods=['GET'])
def emails():
    emails = get_emails()
    return jsonify(emails)

@app.route('/logs/<email>', methods=['GET'])
def get_logs(email):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute(f"SELECT * FROM message_logs WHERE email = %s", (email,))
    logs = [dict(row) for row in cur.fetchall()]
    return jsonify(logs)

@app.route('/check', methods=['GET', 'POST'])
def checking():
    return render_template('validator.html')
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000)
