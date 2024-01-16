# from flask import Flask, render_template, request, jsonify
# from jsonschema import Draft202012Validator
# import json

# app = Flask(__name__)

# @app.route('/', methods=['GET', 'POST'])
# def index():
#     errors = []
#     schema = ""
#     data = ""
#     if request.method == 'POST':
#         schema = request.form.get('schema')
#         data = request.form.get('data')
#         v = Draft202012Validator(json.loads(schema))
#         errors = [error.message for error in v.iter_errors(json.loads(data))]
#         if not errors:
#             errors = ["No errors detected."]
#     else:
#         schema = ""
#         data = ""
#     return render_template('compare.html', errors=errors, schema=schema, data=data)

# if __name__ == '__main__':
#     app.run(debug=True)

from flask import Flask, request, render_template, jsonify
import psycopg2
from jsonschema import Draft202012Validator
import json

app = Flask(__name__)

def get_schemas():
    conn = psycopg2.connect(database="test", user="postgres", password="12345678", host="localhost", port="5432")
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

@app.route('/', methods=['GET', 'POST'])
def index():
    errors = []
    schemas = get_schemas()
    data = ""
    schema = ""
    if request.method == 'POST':
        data = request.form.get('data')
        schema = schemas[request.form.get('scenario')]
        v = Draft202012Validator(schema)
        errors = [error.message for error in v.iter_errors(json.loads(data))]
        if not errors:
            errors = ["No errors detected."]
    return render_template('compare.html', errors=errors, schemas=schemas, data=data, schema=json.dumps(schema, indent=4))

if __name__ == '__main__':
    app.run(debug=True)