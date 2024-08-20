from flask import Flask, request, jsonify, render_template, send_file, abort
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
from data.data_reader import DataReader
from similarity_models.cosine_similarity import get_cosine_similarity_score

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:5174"}})

current_file_path = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_file_path, '..'))
UPLOAD_FOLDER = os.path.join(project_root, 'data', 'storage')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


@app.route('/')
def home():
    return render_template('index.html')


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

        root_img_path = 'processed'
        size = (224, 224)
        data_reader = DataReader(root=root_img_path)

        _, ls_path_score = get_cosine_similarity_score(data_reader, file_path, size)

        top_10_results = [{'image_path': path, 'score': score}
                          for path, score in sorted(ls_path_score, key=lambda x: x[1], reverse=True)[:10]]

        return jsonify(top_10_results), 200


@app.route('/images/<path:url>', methods=['GET'])
def serve_image(url):
    url = "/" + url
    try:
        return send_file(url)
    except FileNotFoundError:
        abort(404, description="File not found.")
    except Exception as e:
        abort(500, description=f"An error occurred: {str(e)}")


if __name__ == '__main__':
    app.run(port=7000, debug=True)
