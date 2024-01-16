# main.py
from flask import Flask, render_template
from schema import display_data, validate_email
from compare import get_schema, index as compare_index, get_schemas
from validator import get_db_connection, get_emails, get_logs, index as validator_index

app = Flask(__name__)

@app.route('/')
def main_page():
    return render_template('main.html')

@app.route('/schema/display_data')
def schema_display_data():
    return display_data()

@app.route('/schema/validate_email')
def schema_validate_email():
    return validate_email()

@app.route('/compare/get_schema')
def compare_get_schema():
    return get_schema()

@app.route('/compare/index')
def compare_index_route():
    return compare_index()

@app.route('/compare/get_schemas')
def compare_get_schemas():
    return get_schemas()

@app.route('/validator/get_db_connection')
def validator_get_db_connection():
    return get_db_connection()

@app.route('/validator/get_emails')
def validator_get_emails():
    return get_emails()

@app.route('/validator/get_logs/<email>')
def validator_get_logs(email):
    return get_logs(email)

@app.route('/validator/index')
def validator_index_route():
    return validator_index()

if __name__ == "__main__":
    app.run(debug=True)