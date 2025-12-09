# Deployment Rehberi

## 1. Backend API Deployment

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

