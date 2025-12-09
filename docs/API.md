# Remove Background API Dokumantasyonu

Twizer Background Removal API'si, gorsellerden arka plani otomatik olarak kaldiran bir servistir.

## Base URL

```
https://api.twizer.xyz
```

## Desteklenen Formatlar

- PNG (.png)
- JPEG/JPG (.jpg, .jpeg)
- WebP (.webp)

## Endpoints

### 1. Health Check

**Endpoint:** `GET /health`

```bash
curl https://api.twizer.xyz/health
```

**Yanit:**
```json
{
  "status": "healthy",
  "model_loaded": true
}
```

### 2. Remove Background (Base64)

**Endpoint:** `POST /api/remove-background`

**Content-Type:** `application/json`

**Request Body:**
```json
{
  "image": "base64_encoded_image_string"
}
```

**Ornek (cURL):**
```bash
curl -X POST https://api.twizer.xyz/api/remove-background \
  -H "Content-Type: application/json" \
  -d '{"image": "BASE64_IMAGE"}'
```

**Basarili Yanit:**
```json
{
  "success": true,
  "image": "base64_encoded_output",
  "format": "png"
}
```

### 3. Remove Background (File Upload)

**Endpoint:** `POST /api/remove`

**Content-Type:** `multipart/form-data`

```bash
curl -X POST https://api.twizer.xyz/api/remove \
  -F "file=@/path/to/image.jpg"
```

## HTTP Status Kodlari

| Kod | Aciklama |
|-----|----------|
| 200 | Basarili |
| 400 | Gecersiz istek |
| 413 | Dosya cok buyuk (max 50MB) |
| 500 | Sunucu hatasi |

## Limitler

- Maksimum dosya boyutu: 50MB
- Desteklenen formatlar: PNG, JPEG, WebP

## Opsiyonel AI Servisleri

Asagidaki servisler `ai.twizer.xyz` uzerinden sunulmaktadir:

- **Upscale:** `POST /api/upscale` - Gorsel kalitesini artirma
- **Watermark Removal:** `POST /api/remove-object` - Filigran kaldirma

Bu servisler opsiyoneldir ve her zaman aktif olmayabilir.

