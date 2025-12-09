# Deployment Rehberi

## 1. Backend API Deployment

### Tek Komutla Otomatik Kurulum

`deployment/deploy_twizer.sh` script'i Ubuntu 22.04+/24.04 üzerinde tüm adımları (bağımlılık kurulumu, repo klonlama/güncelleme, Python venv, systemd servisi, Nginx reverse proxy ve isteğe bağlı Let's Encrypt) otomatik yapar.

```bash
sudo DOMAIN=api.twizer.xyz EMAIL=devops@example.com \
  APP_DIR=/opt/twizer-bg REPO_URL=https://github.com/your-org/twizer-bg.git \
  bash deployment/deploy_twizer.sh
```

Önemli environment değişkenleri:

- `DOMAIN`: Nginx server_name ve (ENABLE_SSL=true ise) SSL sertifikası için alan adı.
- `EMAIL`: Let's Encrypt için e-posta (SSL aktifse zorunlu).
- `APP_DIR`: Kodun klonlanacağı dizin (varsayılan `/opt/twizer-bg`).
- `REPO_URL`: Git repo adresi (varsayılan `https://github.com/your-org/twizer-bg.git`).
- `BRANCH`: Deploy edilecek branch (varsayılan `main`).
- `ENABLE_SSL`: `true/false` (varsayılan `true`). False yapılırsa certbot çalışmaz.

Script tamamlandığında:

- Systemd servisi: `/etc/systemd/system/twizer-bg.service`
- Nginx konfigürasyonu: `/etc/nginx/sites-available/twizer-bg`
- Servis adresi: `http(s)://<DOMAIN>`

### Docker ile Deploy (Onerilen)

```bash
# Image build
docker build -t twizer-bg-api .

# Container calistir
docker run -d -p 5000:5000 --name twizer-api twizer-bg-api
```

### Ubuntu'da Manuel Kurulum

```bash
# Virtual environment olustur
apt install python3-venv
python3 -m venv venv
source venv/bin/activate

# Bagimliliklari yukle
pip install --upgrade pip
pip install -r requirements.txt

# Calistir
gunicorn --bind 0.0.0.0:5000 app:app
```

### Systemd Service

```ini
[Unit]
Description=Twizer Background Removal API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/app
Environment="PATH=/path/to/app/venv/bin"
ExecStart=/path/to/app/venv/bin/gunicorn --bind 0.0.0.0:5000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
systemctl daemon-reload
systemctl start twizer-api
systemctl enable twizer-api
```

## 2. Figma Plugin Deployment

### Figma Community'ye Publish

1. Figma Desktop ac
2. `Plugins` > `Development` > `Import plugin from manifest...`
3. `manifest.json` sec
4. `Plugins` > `Development` > `Publish plugin...`

### Gerekli Dosyalar

- `manifest.json`
- `code.js`
- `ui.html`

## 3. Production Onerileri

- Nginx reverse proxy kullan
- SSL/TLS ekle (Let's Encrypt)
- Rate limiting uygula
- Log yonetimi yap

