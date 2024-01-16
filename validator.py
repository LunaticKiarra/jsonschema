from flask import Flask, request, render_template, jsonify
import psycopg2
import psycopg2.extras

app = Flask(__name__)

def get_db_connection():
    conn = psycopg2.connect(database="test", user="postgres", password="12345678", host="localhost", port="5432")
    return conn

@app.route('/emails', methods=['GET'])
def get_emails():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT email FROM message_logs")
    emails = [row[0] for row in cur.fetchall()]
    return jsonify(emails)

@app.route('/logs/<email>', methods=['GET'])
def get_logs(email):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT * FROM message_logs WHERE email = %s", (email,))
    logs = [dict(row) for row in cur.fetchall()]
    return jsonify(logs)

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('validator.html')

if __name__ == '__main__':
    app.run(debug=True)