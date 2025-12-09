# Deployment Rehberi

## 1. Backend API Deployment

### Tek Komutla Otomatik Kurulum

`deployment/deploy_twizer.sh` script'i Ubuntu 22.04+/24.04 üzerinde tüm adımları (bağımlılık kurulumu, repo klonlama/güncelleme, Python venv, systemd servisi, Nginx reverse proxy ve isteğe bağlı Let's Encrypt) otomatik yapar.

### Hızlı senaryo (kendi domain ve GitHub adresinle)

1. DNS'te alan adını (örn. `api.twizer.xyz`) sunucunun IP'sine yönlendir.
2. Script'i repo içinden çalıştırırken kendi bilgilerini env olarak geçir:

```bash
sudo \
  REPO_URL="https://github.com/<github-kullanici-adiniz>/twizer-bg.git" \
  APP_DIR="/opt/twizer-bg" \
  DOMAIN="api.twizer.xyz" \
  EMAIL="you@example.com" \
  ENABLE_SSL=true \
  bash deployment/deploy_twizer.sh
```

Hazır doldurulmuş örnek (script'i çalıştırmadan önce `chmod +x deployment/deploy_twizer.sh` ve DNS yönlendirmesini yapmayı unutma):

```bash
sudo \
  REPO_URL="https://github.com/CheersRango/twizer-bg.git" \
  APP_DIR="/opt/twizer-bg" \
  DOMAIN="api.twizer.xyz" \
  EMAIL="elxsirmedia@gmail.com" \
  ENABLE_SSL=true \
  bash deployment/deploy_twizer.sh
```

3. Servis durumunu kontrol et: `systemctl status twizer-bg`
4. Dışarıdan doğrula: `curl -k https://api.twizer.xyz/health`

> SSL için gerçek bir e-posta gereklidir; `EMAIL=admin@example.com` ile certbot çalışmayacaktır.

Önemli environment değişkenleri:

- `DOMAIN`: Nginx server_name ve (ENABLE_SSL=true ise) SSL sertifikası için alan adı.
- `EMAIL`: Let's Encrypt için e-posta (SSL aktifse zorunlu).
- `APP_DIR`: Kodun klonlanacağı dizin (varsayılan `/opt/twizer-bg`).
- `REPO_URL`: Git repo adresi (varsayılan `https://github.com/CheersRango/twizer-bg.git`).
- `BRANCH`: Deploy edilecek branch (varsayılan `main`).
- `ENABLE_SSL`: `true/false` (varsayılan `true`). False yapılırsa certbot çalışmaz.
- `SERVICE_USER`: Systemd servisinin çalışacağı kullanıcı (varsayılan `www-data`).
- `CHOWN_APP_DIR`: `true` ise `APP_DIR` dizinini `SERVICE_USER` kullanıcısına devreder (varsayılan `false`).

Script tamamlandığında:

- Systemd servisi: `/etc/systemd/system/twizer-bg.service`
- Nginx konfigürasyonu: `/etc/nginx/sites-available/twizer-bg`
- Servis adresi: `http(s)://<DOMAIN>`

> Veya servis kullanıcısını `root` yapmak için çağrı sırasında `SERVICE_USER=root` verebilirsin. `www-data` kullanıyorsan ve dizin izinlerini önceden vermek istersen: `sudo chown -R www-data:www-data /opt/twizer-bg`.

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

