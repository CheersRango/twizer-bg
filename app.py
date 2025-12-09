from flask import Flask, request, jsonify
from flask_cors import CORS
import base64
import requests

app = Flask(__name__)
CORS(app)

# Sağlık kontrolü
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"message": "twizer bg test", "status": "ok"})


# Base64 decode helper
def decode_image(base64_string):
    try:
        return base64.b64decode(base64_string.split(",")[-1])
    except Exception as e:
        print("Decode error:", e)
        return None


# Base64 encode helper
def encode_image(binary_data):
    return "data:image/png;base64," + base64.b64encode(binary_data).decode("utf-8")


# ------------------------------------------
# 1) REMOVE BACKGROUND
# ------------------------------------------
@app.route("/api/remove-background", methods=["POST"])
def remove_background():
    try:
        data = request.get_json()
        img_b64 = data.get("image")
        if not img_b64:
            return jsonify({"error": "No image provided"}), 400

        img_bytes = decode_image(img_b64)

        # MODEL API → BURAYA İSTEDİĞİN MODELİ BAĞLAYABİLİRSİN
        # DEMO ÇIKTI ÜRETİYORUZ
        result = img_bytes  # Şimdilik aynı resmi geri döndürüyoruz

        return jsonify({"image": encode_image(result)})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ------------------------------------------
# 2) REMOVE OBJECT
# ------------------------------------------
@app.route("/api/remove-object", methods=["POST"])
def remove_object():
    try:
        data = request.get_json()
        img_b64 = data.get("image")
        mask_b64 = data.get("mask")

        if not img_b64 or not mask_b64:
            return jsonify({"error": "Missing image or mask"}), 400

        # DEMO → Model entegrasyonu istersen hemen eklerim
        img_bytes = decode_image(img_b64)
        result = img_bytes

        return jsonify({"image": encode_image(result)})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ------------------------------------------
# 3) UPSCALE
# ------------------------------------------
@app.route("/api/upscale", methods=["POST"])
def upscale():
    try:
        data = request.get_json()
        img_b64 = data.get("image")

        if not img_b64:
            return jsonify({"error": "Missing image"}), 400

        img_bytes = decode_image(img_b64)

        # DEMO → Buraya RealESRGAN veya başka upscale servisi bağlanabilir
        result = img_bytes

        return jsonify({"image": encode_image(result)})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
