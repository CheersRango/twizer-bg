# Sorun Giderme Rehberi

## "Sunucuya baglanilamadi" Hatasi

### 1. API Durumunu Kontrol Et

```bash
curl https://api.twizer.xyz/health
```

Beklenen:
```json
{
  "status": "healthy",
  "model_loaded": true
}
```

### 2. Local Test

```bash
pip install -r requirements.txt
python app.py
```

API `http://localhost:5000` adresinde calisacak.

### 3. CORS Kontrol

`app.py` dosyasinda:
```python
from flask_cors import CORS
CORS(app)
```

### 4. manifest.json Kontrol

```json
{
  "networkAccess": {
    "allowedDomains": ["https://api.twizer.xyz", "https://ai.twizer.xyz"]
  }
}
```

## Yaygin Hatalar

### "ModuleNotFoundError: No module named 'cv2'"

```bash
pip install opencv-python-headless
```

### "Model not loaded"

Model ilk calistirmada otomatik indirilir. Internet baglantisi gerekli.

### "CORS policy" Hatasi

CORS ayarlarini kontrol edin.

### Port 5000 kullanilmda

```bash
gunicorn --bind 0.0.0.0:5001 app:app
```

## Debug Ipuclari

1. Browser Console (F12) kontrol edin
2. API loglari: `gunicorn --log-level debug`
3. Network tab'inda istekleri kontrol edin

## Upscale/Watermark Servisleri

Bu servisler `ai.twizer.xyz` uzerinden sunulur ve her zaman aktif olmayabilir. Hata alindiginda:

- "Upscale gecici olarak aktif degil" mesaji gosterilir
- Servis sonra tekrar denenebilir

