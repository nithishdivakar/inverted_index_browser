from flask import Flask, jsonify, send_from_directory, send_file
from flask import Flask, render_template, request, jsonify
import argparse
import os,json
from datetime import datetime
from pathlib import Path

app = Flask(__name__)

# @app.route('/data', methods=['GET'])
# def get_data():
#     data_file = 'data.json'
#     if os.path.exists(data_file):
#         with open(data_file, 'r') as file:
#             data = json.load(file)
#         return jsonify(data)
#     else:
#         return jsonify({"error": "data.json file not found"}), 404

# @app.route('/', methods=['GET'])
# def serve_home():
#     print(app.config['ASSETS_DIR'])
#     return send_from_directory(app.config['ASSETS_DIR'], 'ii_index.html')


@app.route('/', methods=['GET'])
def serve_home():
    return send_file(app.config['ASSETS_DIR']/'ii_index.html')

@app.route('/data.json', methods=['GET'])
def serve_json():
    return send_file(app.config['ASSETS_DIR']/'ii_data.json')

@app.route('/app.js', methods=['GET'])
def serve_js():
    return send_file(app.config['ASSETS_DIR']/'ii_app.js')

@app.route('/customstyle.css', methods=['GET'])
def serve_css():
    return send_file(app.config['ASSETS_DIR']/'ii_customstyle.css')

@app.route('/api/add_note', methods=['POST'])
def add_note():
    data = request.get_json()
    out_path = Path(app.config['NOTES_DIR'])/data['uri']
    if out_path.suffix != '.md':
        out_path = out_path.with_suffix('.md')
    with open(out_path,"w") as F:
        F.write(data['content'])
    print(f"[INFO] added note {out_path}")
    return jsonify({'note_id': data['uri'], 'content': data['content']})


@app.route('/api/get_note_content/<path:note_id>', methods=['GET'])
def get_note_content(note_id):
    print(note_id)
    if note_id=='_empty':
        current_time = datetime.now()
        formatted_time = current_time.strftime("%Y-%m-%dT%H:%M:%S")
        return jsonify({'note_id': f"{formatted_time[:10]}.md", 'content': f"""---
ctime: '{formatted_time}'
index: ''
related: []
tags: []
title: '{formatted_time[:10]}'
---
## {formatted_time[:10]}"""})


    note_path = Path(app.config['NOTES_DIR'])/note_id
    if note_path.suffix != '.md':
        note_path = note_path.with_suffix('.md')

    if os.path.exists(note_path):
        with open(note_path, 'r') as file:
            return jsonify({'note_id': note_id, 'content': file.read()})
    else:
        return jsonify({'note_id': note_id, "content" :"", "error": "data.json file not found"}), 404
    

if __name__ == '__main__':
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Run Flask app on a specified port with optional hot reloading.')
    parser.add_argument('--port', type=int, required=True, help='Port number to run the Flask app on.')
    parser.add_argument('--notes_dir', type=str, required=True, help='root path of the files')
    parser.add_argument('--assets_dir', type=str, required=True, help='root path of the files')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode with hot reloading.')
    args = parser.parse_args()
    app.config['NOTES_DIR'] = args.notes_dir
    app.config['DEBUG'] = args.debug
    app.config['ASSETS_DIR'] = Path.cwd()/args.assets_dir

    # Run the Flask app on the specified port
    app.run(port=args.port, debug=args.debug, extra_files=['app.py'])