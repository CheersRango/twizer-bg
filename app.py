"""
Remove Background API
Production-ready Flask API for background removal using rembg
"""
import os
import base64
import io
from flask import Flask, request, jsonify
from flask_cors import CORS
from rembg import remove
from PIL import Image
import logging

# Logging ayarları
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Config
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size

# Model'i önceden yükle
try:
    from rembg import new_session
    session = new_session('u2net')
    logger.info("✅ U2Net model loaded successfully")
except Exception as e:
    logger.error(f"❌ Model loading error: {e}")
    session = None


def detect_image_format(image):
    """
    Görsel formatını tespit eder ve normalize eder
    Returns: (format_name, pil_format)
    """
    format_map = {
        'JPEG': ('jpeg', 'JPEG'),
        'JPG': ('jpeg', 'JPEG'),
        'PNG': ('png', 'PNG'),
        'WEBP': ('webp', 'WEBP')
    }
    
    # Image formatını al
    img_format = image.format
    
    if img_format and img_format.upper() in format_map:
        return format_map[img_format.upper()]
    
    # Format tespit edilemezse varsayılan olarak PNG döndür
    return ('png', 'PNG')


@app.route('/', methods=['GET'])
def index():
    """API bilgi endpoint'i"""
    return jsonify({
        "name": "Remove Background API",
        "version": "1.0.0",
        "endpoints": {
            "/health": "Health check",
            "/api/remove-background": "Remove background (Base64 input)",
            "/api/remove": "Remove background (File upload)",
            "/api/remove-watermark": "Remove watermark (Base64 input)"
        },
        "status": "running"
    })


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "model_loaded": session is not None
    }), 200


@app.route('/api/remove-background', methods=['POST'])
def remove_background_base64():
    """
    Base64 encoded image ile background removal
    Request body: {"image": "base64_string"}
    """
    try:
        data = request.get_json()
        
        if not data or 'image' not in data:
            return jsonify({"error": "Missing 'image' field in request body"}), 400
        
        # Base64 decode
        try:
            image_data = base64.b64decode(data['image'])
        except Exception as e:
            return jsonify({"error": f"Invalid base64 encoding: {str(e)}"}), 400
        
        # Image'i aç
        try:
            input_image = Image.open(io.BytesIO(image_data))
        except Exception as e:
            return jsonify({"error": f"Invalid image format: {str(e)}"}), 400
        
        # Gelen görselin formatını tespit et
        output_format_name, output_format_pil = detect_image_format(input_image)
        
        # Background removal
        if session is None:
            return jsonify({"error": "Model not loaded"}), 500
        
        output = remove(image_data, session=session)
        
        # Gelen görselin formatında döndür
        output_image = Image.open(io.BytesIO(output))
        output_buffer = io.BytesIO()
        
        # JPEG için optimize=True kullan (kalite için)
        if output_format_pil == 'JPEG':
            # RGBA modundaysa RGB'ye çevir (JPEG alpha channel desteklemez)
            if output_image.mode == 'RGBA':
                # Beyaz arka plan üzerine yerleştir
                rgb_image = Image.new('RGB', output_image.size, (255, 255, 255))
                rgb_image.paste(output_image, mask=output_image.split()[3] if output_image.mode == 'RGBA' else None)
                output_image = rgb_image
            output_image.save(output_buffer, format=output_format_pil, quality=95, optimize=True)
        else:
            output_image.save(output_buffer, format=output_format_pil)
        
        output_buffer.seek(0)
        
        # Base64 encode
        output_base64 = base64.b64encode(output_buffer.getvalue()).decode('utf-8')
        
        return jsonify({
            "success": True,
            "image": output_base64,
            "format": output_format_name
        }), 200
        
    except Exception as e:
        logger.error(f"Error in remove_background_base64: {str(e)}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@app.route('/api/remove-watermark', methods=['POST'])
def remove_watermark_base64():
    """
    Base64 encoded image ile watermark removal
    Request body: {"image": "base64_string"}
    """
    try:
        data = request.get_json()
        
        if not data or 'image' not in data:
            return jsonify({"error": "Missing 'image' field in request body"}), 400
        
        # Base64 decode
        try:
            image_data = base64.b64decode(data['image'])
        except Exception as e:
            return jsonify({"error": f"Invalid base64 encoding: {str(e)}"}), 400
        
        # Image'i aç
        try:
            input_image = Image.open(io.BytesIO(image_data))
        except Exception as e:
            return jsonify({"error": f"Invalid image format: {str(e)}"}), 400
        
        # Gelen görselin formatını tespit et
        output_format_name, output_format_pil = detect_image_format(input_image)
        
        # OpenCV ile watermark kaldırma
        try:
            import cv2
            import numpy as np
            
            # PIL Image'i OpenCV formatına çevir
            img_array = np.array(input_image)
            if len(img_array.shape) == 3:
                img_cv = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
            else:
                img_cv = img_array
            
            height, width = img_cv.shape[:2]
            
            # 1. TÜM GÖRSELDE watermark'ları tespit et
            gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
            
            # Canny edge detection ile yazı kenarlarını bul (tüm görselde)
            edges = cv2.Canny(gray, 50, 150)
            
            # Morphological operations ile yazıları birleştir
            kernel = np.ones((3, 3), np.uint8)
            edges = cv2.dilate(edges, kernel, iterations=2)
            edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
            
            # Adaptive threshold ile yüksek kontrastlı alanları bul (tüm görselde)
            thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                          cv2.THRESH_BINARY_INV, 11, 2)
            
            # İki yöntemi birleştir
            combined = cv2.bitwise_or(edges, thresh)
            combined = cv2.morphologyEx(combined, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
            
            # Tüm görsel için mask başlangıcı
            mask = combined.copy()
            
            # 2. Beyaz/şeffaf watermark'ları tespit et (TÜM GÖRSELDE)
            hsv = cv2.cvtColor(img_cv, cv2.COLOR_BGR2HSV)
            # Daha geniş beyaz aralığı
            lower_white = np.array([0, 0, 180])
            upper_white = np.array([180, 50, 255])
            white_mask = cv2.inRange(hsv, lower_white, upper_white)
            
            # 3. Yarı-şeffaf watermark'ları tespit et (düşük doygunluk, yüksek parlaklık)
            lower_semi = np.array([0, 0, 200])
            upper_semi = np.array([180, 30, 255])
            semi_mask = cv2.inRange(hsv, lower_semi, upper_semi)
            
            # 4. Düşük kontrastlı watermark'ları tespit et (gradient tabanlı)
            laplacian = cv2.Laplacian(gray, cv2.CV_64F)
            laplacian_abs = np.absolute(laplacian)
            laplacian_8u = np.uint8(laplacian_abs)
            _, low_contrast = cv2.threshold(laplacian_8u, 10, 255, cv2.THRESH_BINARY_INV)
            
            # Tüm mask'ları birleştir
            mask = cv2.bitwise_or(mask, white_mask)
            mask = cv2.bitwise_or(mask, semi_mask)
            
            # Düşük kontrastlı alanları sadece kenarlarda kullan (watermark olabilir)
            # Kenar tespiti ile birleştir
            contours, _ = cv2.findContours(low_contrast, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for contour in contours:
                area = cv2.contourArea(contour)
                # Küçük ve düzenli şekiller watermark olabilir
                if 100 < area < (height * width * 0.1):  # Çok küçük veya çok büyük değilse
                    cv2.drawContours(mask, [contour], -1, 255, -1)
            
            # Mask'ı optimize et - sadece watermark alanları
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
            
            # Çok büyük mask'ları sınırla
            mask_area = np.sum(mask > 0)
            if mask_area > (height * width * 0.25):  # %25'ten fazla ise
                # Sadece en yoğun alanları al
                _, mask = cv2.threshold(mask, 127, 255, cv2.THRESH_BINARY)
            
            # Gelişmiş inpainting: Navier-Stokes algoritması (daha iyi sonuç)
            # Küçük radius ile başla (daha az blur)
            result = cv2.inpaint(img_cv, mask, 3, cv2.INPAINT_NS)
            
            # Eğer mask çok büyükse, sadece mask alanını iyileştir
            if mask_area > 0:
                # İkinci pass: Sadece problemli alanları düzelt
                diff = cv2.absdiff(img_cv, result)
                diff_gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
                _, problem_mask = cv2.threshold(diff_gray, 10, 255, cv2.THRESH_BINARY)
                problem_mask = cv2.bitwise_and(problem_mask, mask)
                
                if np.sum(problem_mask) > 0:
                    # Problemli alanları tekrar işle
                    refined = cv2.inpaint(result, problem_mask, 5, cv2.INPAINT_NS)
                    result[problem_mask > 0] = refined[problem_mask > 0]
            
            # Edge-preserving filter ile blur'u azalt ve detayları koru
            # flags=2: Recursive filtering (daha yavaş ama daha iyi)
            result = cv2.edgePreservingFilter(result, flags=2, sigma_s=50, sigma_r=0.4)
            
            # Unsharp mask ile keskinliği artır (blur'u azalt)
            gaussian = cv2.GaussianBlur(result, (0, 0), 2.0)
            result = cv2.addWeighted(result, 1.5, gaussian, -0.5, 0)
            
            # OpenCV formatını PIL'e çevir
            result_rgb = cv2.cvtColor(result, cv2.COLOR_BGR2RGB)
            output_image = Image.fromarray(result_rgb)
            
        except ImportError:
            # OpenCV yoksa, basit bir yaklaşım: Görseli olduğu gibi döndür
            logger.warning("OpenCV not available, returning original image")
            output_image = input_image
        except Exception as e:
            logger.error(f"Watermark removal error: {str(e)}")
            # Hata durumunda orijinal görseli döndür
            output_image = input_image
        
        # Gelen görselin formatında döndür
        output_buffer = io.BytesIO()
        
        # JPEG için optimize=True kullan (kalite için)
        if output_format_pil == 'JPEG':
            if output_image.mode == 'RGBA':
                rgb_image = Image.new('RGB', output_image.size, (255, 255, 255))
                rgb_image.paste(output_image, mask=output_image.split()[3] if output_image.mode == 'RGBA' else None)
                output_image = rgb_image
            output_image.save(output_buffer, format=output_format_pil, quality=95, optimize=True)
        else:
            output_image.save(output_buffer, format=output_format_pil)
        
        output_buffer.seek(0)
        
        # Base64 encode
        output_base64 = base64.b64encode(output_buffer.getvalue()).decode('utf-8')
        
        return jsonify({
            "success": True,
            "image": output_base64,
            "format": output_format_name
        }), 200
        
    except Exception as e:
        logger.error(f"Error in remove_watermark_base64: {str(e)}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@app.route('/api/remove', methods=['POST'])
def remove_background_file():
    """
    File upload ile background removal
    Content-Type: multipart/form-data
    Field name: 'file'
    """
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        # Image'i oku
        try:
            image_data = file.read()
            input_image = Image.open(io.BytesIO(image_data))
        except Exception as e:
            return jsonify({"error": f"Invalid image format: {str(e)}"}), 400
        
        # Gelen görselin formatını tespit et
        output_format_name, output_format_pil = detect_image_format(input_image)
        
        # Background removal
        if session is None:
            return jsonify({"error": "Model not loaded"}), 500
        
        output = remove(image_data, session=session)
        
        # Gelen görselin formatında döndür
        output_image = Image.open(io.BytesIO(output))
        output_buffer = io.BytesIO()
        
        # JPEG için optimize=True kullan (kalite için)
        if output_format_pil == 'JPEG':
            # RGBA modundaysa RGB'ye çevir (JPEG alpha channel desteklemez)
            if output_image.mode == 'RGBA':
                # Beyaz arka plan üzerine yerleştir
                rgb_image = Image.new('RGB', output_image.size, (255, 255, 255))
                rgb_image.paste(output_image, mask=output_image.split()[3] if output_image.mode == 'RGBA' else None)
                output_image = rgb_image
            output_image.save(output_buffer, format=output_format_pil, quality=95, optimize=True)
        else:
            output_image.save(output_buffer, format=output_format_pil)
        
        output_buffer.seek(0)
        
        # Base64 encode
        output_base64 = base64.b64encode(output_buffer.getvalue()).decode('utf-8')
        
        return jsonify({
            "success": True,
            "image": output_base64,
            "format": output_format_name
        }), 200
        
    except Exception as e:
        logger.error(f"Error in remove_background_file: {str(e)}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@app.errorhandler(413)
def request_entity_too_large(error):
    """File size limit exceeded"""
    return jsonify({"error": "File too large. Maximum size: 50MB"}), 413


@app.errorhandler(500)
def internal_error(error):
    """Internal server error handler"""
    logger.error(f"Internal error: {str(error)}")
    return jsonify({"error": "Internal server error"}), 500


if __name__ == '__main__':
    # Development server (production'da gunicorn kullanılacak)
    app.run(host='0.0.0.0', port=5000, debug=False)
