from flask import Flask, request, jsonify, send_file
import os
from braille.braille_converter import make_braille_image, text_to_braille, decode_braille_image
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = './uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route("/api/text-to-braille-image", methods=["POST"])
def api_text_to_braille_image():
    data = request.json
    text = data.get("text", "")
    if not text:
        return jsonify({"error": "텍스트 입력 필요"}), 400
    img_path, cell_count = make_braille_image(text)
    return send_file(img_path, mimetype="image/png")

@app.route("/api/text-to-braille-unicode", methods=["POST"])
def api_text_to_braille_unicode():
    data = request.json
    text = data.get("text", "")
    if not text:
        return jsonify({"error": "텍스트 입력 필요"}), 400
    braille_unicode = text_to_braille(text, use_unicode=True)
    return jsonify({"braille_unicode": braille_unicode})

@app.route('/api/braille-image-to-text', methods=['POST'])
def api_braille_image_to_text():
    if 'file' not in request.files:
        return jsonify({"error": "이미지 파일 업로드 필요"}), 400
    file = request.files['file']
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)
    try:
        text = decode_braille_image(file_path)
        # 변환 정보 저장 (예: data/restore_20240527_000000.json)
        import json
        from datetime import datetime
        os.makedirs("data", exist_ok=True)
        info = {
            "restored_text": text,
            "input_image": filename,
            "restored_at": datetime.now().isoformat()
        }
        info_filename = f"restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(os.path.join("data", info_filename), "w", encoding="utf-8") as f:
            json.dump(info, f, ensure_ascii=False, indent=2)
        return jsonify({'text': text})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)