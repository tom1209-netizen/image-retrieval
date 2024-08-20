from flask import Flask, request, jsonify
import os
from werkzeug.utils import secure_filename
from data.data_reader import DataReader
from similarity_models.cosine_similarity import get_cosine_similarity_score

app = Flask(__name__)

# Configure the upload directory
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


@app.route('/upload', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Process the image with DataReader
        root_img_path = 'processed'
        size = (224, 224)
        data_reader = DataReader(root=root_img_path)

        # Calculate cosine similarity
        _, ls_path_score = get_cosine_similarity_score(data_reader, file_path, size)

        # Return the results as JSON
        results = [{'image_path': path, 'score': score} for path, score in sorted(ls_path_score, key=lambda x: x[1], reverse=True)]
        return jsonify(results), 200


if __name__ == '__main__':
    app.run(debug=True)