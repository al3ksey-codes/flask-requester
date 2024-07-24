import uuid
import time
from flask import Flask, render_template, request, jsonify, redirect, url_for
import psycopg2

app = Flask(__name__)

# Replace with your database credentials
DB_NAME = "your_db_name"
DB_USER = "your_db_user"
DB_PASS = "your_db_password"
DB_HOST = "your_db_host"

conn = psycopg2.connect(database=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
cur = conn.cursor()

cur.execute("""
    CREATE TABLE IF NOT EXISTS requests (
        id UUID PRIMARY KEY,
        url TEXT,
        ip TEXT,
        method TEXT,
        content TEXT,
        timestamp TIMESTAMP
    )
""")
conn.commit()

def store_request(url, ip, method, content):
    request_id = str(uuid.uuid4())
    timestamp = time.time()

    cur.execute("INSERT INTO requests VALUES (%s, %s, %s, %s, %s, %s)",
                (request_id, url, ip, method, content, timestamp))
    conn.commit()

    return request_id

@app.route('/app/receiver', methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
def receiver():
    request_id = store_request(request.url, request.remote_addr, request.method, request.data)
    return jsonify({'request_id': request_id})

@app.route('/app/webui')
def webui():
    cur.execute("SELECT * FROM requests")
    requests = cur.fetchall()
    return render_template('requests.html', requests=requests)

@app.route('/app/webui/delete/<request_id>')
def delete_request(request_id):
    cur.execute("DELETE FROM requests WHERE id = %s", (request_id,))
    conn.commit()
    return redirect(url_for('webui'))

@app.route('/app/webui/clear')
def clear_all():
    cur.execute("DELETE FROM requests")
    conn.commit()
    return redirect(url_for('webui'))

# Create a basic HTML template for the web UI
with open('templates/requests.html', 'w') as f:
    f.write("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Request Viewer</title>
    </head>
    <body>
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>URL</th>
                    <th>IP</th>
                    <th>Method</th>
                    <th>Content</th>
                    <th>Timestamp</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                {% for request in requests %}
                <tr>
                    <td>{{ request[0] }}</td>
                    <td>{{ request[1] }}</td>
                    <td>{{ request[2] }}</td>
                    <td>{{ request[3] }}</td>
                    <td>{{ request[4] }}</td>
                    <td>{{ request[5] }}</td>
                    <td><a href="/app/webui/delete/{{ request[0] }}">Delete</a></td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        <a href="/app/webui/clear">Clear All</a>
    </body>
    </html>
    """)

if __name__ == '__main__':
    app.run(debug=True)
