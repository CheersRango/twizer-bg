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

## Otomatik Deployment

Tek komutla production ortamına kurulum için `deployment/deploy_twizer.sh` script'ini kullanabilirsiniz. Kendi repo ve domain'inizi environment değişkenleri ile geçirmeniz yeterlidir:

```bash
sudo \
  REPO_URL="https://github.com/<github-kullanici-adiniz>/twizer-bg.git" \
  APP_DIR="/opt/twizer-bg" \
  DOMAIN="api.twizer.xyz" \
  EMAIL="you@example.com" \
  ENABLE_SSL=true \
  bash deployment/deploy_twizer.sh
```

> Hizmet kullanıcısını `SERVICE_USER` ile değiştirebilir, gerekirse dizinin sahipliğini otomatik devretmek için `CHOWN_APP_DIR=true` ekleyebilirsiniz. Ayrıntılı kurulum için [Deployment Rehberi](docs/DEPLOYMENT.md) dosyasına göz atın.

## Figma Plugin

1. `Plugins` > `Development` > `Import plugin from manifest...`
2. `manifest.json` sec

## Lisans

MIT
