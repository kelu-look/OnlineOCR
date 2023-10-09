from flask import Flask, render_template, request, jsonify
from paddleocr import PaddleOCR
from pdf2image import convert_from_path
import os
import uuid

app = Flask(__name__)
ocr = PaddleOCR()

UPLOAD_FOLDER = './uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)

    extracted_texts = []

    if file.filename.endswith('.pdf'):
        pages = convert_from_path(file_path)
        for page in pages:
            temp_image_path = os.path.join(app.config['UPLOAD_FOLDER'], f"temp_image_{uuid.uuid4()}.png")
            page.save(temp_image_path, 'PNG')
            result = ocr.ocr(temp_image_path)
            extracted_texts.extend(["".join(word_info[0]) for line in result for word_info in line[1:]])
            os.remove(temp_image_path)
    else:
        result = ocr.ocr(file_path)
        extracted_texts.extend(["".join(word_info[0]) for line in result for word_info in line[1:]])

    os.remove(file_path)
    return jsonify({"text": "\n".join(extracted_texts)})

if __name__ == "__main__":
    app.run(debug=True)