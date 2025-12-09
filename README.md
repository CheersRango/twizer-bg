# Twizer BG Pro

Figma plugin ve production-ready background removal API.

## Ozellikler

- AI ile arkaplan kaldirma
- Watermark kaldirma (opsiyonel AI servisi)
- Gorsel kalitesi artirma / Upscale (opsiyonel AI servisi)
- Base64 ve dosya yukleme destegi
- JPEG, PNG, WebP format destegi

## Hizli Baslangic

### Local Development

```bash
pip install -r requirements.txt
python app.py
```

### Docker

```bash
docker build -t twizer-bg-api .
docker run -p 5000:5000 twizer-bg-api
```

## API Endpoints

| Endpoint | Method | Aciklama |
|----------|--------|----------|
| `/health` | GET | Saglik kontrolu |
| `/api/remove-background` | POST | Arkaplan kaldirma (Base64) |
| `/api/remove` | POST | Arkaplan kaldirma (Dosya) |

## Dokumantasyon

- [API Dokumantasyonu](docs/API.md)
- [Deployment Rehberi](docs/DEPLOYMENT.md)
- [Sorun Giderme](docs/TROUBLESHOOTING.md)

## Figma Plugin

1. `Plugins` > `Development` > `Import plugin from manifest...`
2. `manifest.json` sec

## Lisans

MIT
