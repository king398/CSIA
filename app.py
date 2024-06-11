from flask import Flask, request, render_template, session, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
import os
import requests

app = Flask(__name__)
app.secret_key = 'secret'  # Set a secret key for session handling

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('upload_file'))
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    session['username'] = username
    user_folder = os.path.join(app.config['UPLOAD_FOLDER'], username)
    if not os.path.exists(user_folder):
        os.makedirs(user_folder)
    return redirect(url_for('upload_file'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

API_URL = "https://api-inference.huggingface.co/models/google/vit-base-patch16-224"
headers = {"Authorization": "Bearer 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"}

def query(filename):
    with open(filename, "rb") as f:
        data = f.read()
    response = requests.post(API_URL, headers=headers, data=data)
    return response.json()

@app.route('/upload_file', methods=['GET', 'POST'])
def upload_file():
    if 'username' not in session:
        return redirect(url_for('index'))
    if request.method == 'POST':
        if 'file' not in request.files:
            return 'No file part'
        file = request.files['file']
        if file.filename == '':
            return 'No selected file'
        if file:
            filename = secure_filename(file.filename)
            user_folder = os.path.join(app.config['UPLOAD_FOLDER'], session['username'])
            os.makedirs(user_folder, exist_ok=True)  # Create the user's folder if it doesn't exist
            file.save(os.path.join(user_folder, filename))
            output = query(os.path.join(user_folder, filename))
            print(output)
            if 'uploaded_images' not in session:
                session['uploaded_images'] = []
            session['uploaded_images'].append(filename)
            url = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent'
            headers = {
                'Content-Type': 'application/json',
            }
            data = {
                "contents": [{
                    "parts": [{
                        "text": f"""{output}. Talk about the most confident class in this. 
                        Like for example if its a cat give me cool facts and stuff about the class."""
                    }]
                }]
            }

            # Replace 'YOUR_API_KEY' with your actual API key
            params = {
                'key': 'AIzaSyAJ3FnpdHzQAhGIQ97iqNlkQcK0VZMzin4'
            }

            response = requests.post(url, headers=headers, json=data, params=params)
            chatbot = response.json()["candidates"][0]['content']['parts'][0]['text']

            return render_template('results.html', text=output,chatbot=chatbot)
    uploaded_images = session.get('uploaded_images', [])
    return render_template('upload.html', uploaded_images=uploaded_images)
@app.route('/uploads/<username>/<filename>')
def uploaded_file(username, filename):
    return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], username), filename)
if __name__ == '__main__':
    app.run(debug=True)


