from flask import Flask, render_template, request, jsonify
import sqlite3
import csv
import json
from threading import Lock

app = Flask(__name__, static_folder='static', template_folder='templates')
DATABASE = 'scammers.db'
lock = Lock()

def get_db():
    db = sqlite3.connect(DATABASE)
    db.execute('''CREATE TABLE IF NOT EXISTS scammers
                (ip TEXT, country TEXT, region TEXT, city TEXT,
                 latitude TEXT, longitude TEXT, user_agent TEXT, device TEXT)''')
    return db

def ip_to_location(ip):
    """Convert IP to location using IP2Location DB"""
    try:
        ip_num = sum(int(part) * (256 ** (3 - i)) for i, part in enumerate(ip.split('.')))
        with open('IP2LOCATION-LITE-DB1.CSV', 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                if int(row[0]) <= ip_num <= int(row[1]):
                    return {
                        "country": row[2],
                        "region": row[3],
                        "city": row[4],
                        "latitude": row[5],
                        "longitude": row[6]
                    }
    except Exception as e:
        print(f"IP lookup failed: {e}")
    return {"country": "Unknown", "latitude": "20.5937", "longitude": "78.9629"}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/track')
def track():
    # Get real IP (works when deployed)
    scammer_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    device = request.args.get('device', '{}')
    
    # For local testing - mock Mumbai location
    if scammer_ip in ('127.0.0.1', '::1'):
        location = {
            "ip": "YOUR_LOCAL_IP",
            "country": "India",
            "region": "Maharashtra",
            "city": "Mumbai",
            "latitude": "19.0760",
            "longitude": "72.8777"
        }
    else:
        location = ip_to_location(scammer_ip)
    
    # Log to database
    with lock:
        db = get_db()
        db.execute("INSERT INTO scammers VALUES (?,?,?,?,?,?,?,?)",
                  (scammer_ip, location["country"], location["region"],
                   location["city"], location["latitude"], location["longitude"],
                   request.headers.get('User-Agent'), device))
        db.commit()
    
    return jsonify({
        "ip": scammer_ip,
        **location,
        "device": json.loads(device)
    })

if __name__ == '__main__':
    with app.app_context():
        get_db().close()
    app.run(port=5000, debug=True)