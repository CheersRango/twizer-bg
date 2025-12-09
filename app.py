cat <<'EOF' > /opt/twizer-bg/app.py
from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
import base64

app = Flask(__name__)
ALLOWED_HEADERS = "Content-Type,Authorization,Accept"
ALLOWED_METHODS = "GET,POST,OPTIONS"
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)
app.config["MAX_CONTENT_LENGTH"] = 100 * 1024 * 1024

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"message": "twizer bg test", "status": "ok"})

@app.after_request
def after_request(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", ALLOWED_HEADERS)
    response.headers.add("Access-Control-Allow-Methods", ALLOWED_METHODS)
    response.headers.add("Access-Control-Expose-Headers", ALLOWED_HEADERS)
    return response

def _decode_image(data):
    if not data:
        return None
    try:
        return base64.b64decode(data.split(",")[-1])
    except Exception:
        return None

def _encode_image(binary_data):
    return "data:image/png;base64," + base64.b64encode(binary_data).decode("utf-8")

def _options_ok():
    resp = make_response("", 200)
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Headers"] = ALLOWED_HEADERS
    resp.headers["Access-Control-Allow-Methods"] = ALLOWED_METHODS
    resp.headers["Access-Control-Expose-Headers"] = ALLOWED_HEADERS
    return resp

@app.route("/api/remove-background", methods=["POST", "OPTIONS"])
def remove_bg():
    if request.method == "OPTIONS":
        return _options_ok()
    data = request.get_json() or {}
    image_b64 = data.get("image")
    if not image_b64:
        return jsonify({"error": "No image provided"}), 400
    img_bytes = _decode_image(image_b64)
    if img_bytes is None:
        return jsonify({"error": "Invalid base64"}), 400
    return jsonify({"success": True, "image": _encode_image(img_bytes), "format": "png"})

@app.route("/api/remove-object", methods=["POST", "OPTIONS"])
def remove_object():
    if request.method == "OPTIONS":
        return _options_ok()
    data = request.get_json() or {}
    image_b64 = data.get("image")
    if not image_b64:
        return jsonify({"error": "Missing image"}), 400
    img_bytes = _decode_image(image_b64)
    if img_bytes is None:
        return jsonify({"error": "Invalid base64"}), 400
    return jsonify({"success": True, "image": _encode_image(img_bytes), "format": "png"})

@app.route("/api/upscale", methods=["POST", "OPTIONS"])
def upscale():
    if request.method == "OPTIONS":
        return _options_ok()
    data = request.get_json() or {}
    image_b64 = data.get("image")
    if not image_b64:
        return jsonify({"error": "Missing image"}), 400
    img_bytes = _decode_image(image_b64)
    if img_bytes is None:
        return jsonify({"error": "Invalid base64"}), 400
    return jsonify({"success": True, "image": _encode_image(img_bytes), "format": "png"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
EOF