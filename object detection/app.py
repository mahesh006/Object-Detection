from flask import Flask, request, jsonify, url_for, render_template
import os
from werkzeug.utils import secure_filename
from ultralytics import YOLO

app = Flask(__name__, template_folder='templates')

uploads_dir = os.path.join('static', 'uploads')
os.makedirs(uploads_dir, exist_ok=True)

model = YOLO('/templates/yolov8n.pt')  

@app.route('/upload', methods=['POST'])
def upload():
    files = request.files.getlist('file[]') 
    if not files:
        return jsonify({"error": "No file part"}), 400

    urls = []  
    for file in files:
        if file:  
            filename = secure_filename(file.filename)
            original_file_path = os.path.join(uploads_dir, filename)
            file.save(original_file_path)

            results = model([original_file_path])

            for result in results:
                original_file_name = result.path.split('/')[-1].split('.')[0]
                processed_file_name = 'processed_' + original_file_name + '.jpg'
                processed_file_path = os.path.join(uploads_dir, processed_file_name)
                result.save(processed_file_path)

                original_url = url_for('static', filename=f'uploads/{filename}', _external=True)
                processed_url = url_for('static', filename=f'uploads/{processed_file_name}', _external=True)

                urls.append({'original': original_url, 'processed': processed_url})

    return jsonify(urls)

@app.route('/')
def index():
    return render_template('upload.html')

if __name__ == '__main__':
     app.run(debug=True)
