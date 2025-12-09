# Proje Sıkıntıları ve Riskleri

Aşağıdaki maddeler mevcut kod tabanında hızlıca göze çarpan kritik noktaları özetler.

## 1) Güvenlik ve istismar yüzeyi
- Uygulama tüm origin'lere CORS açıyor ve hiçbir endpoint'te kimlik doğrulama ya da oran sınırlama (rate limiting) uygulanmıyor. Bu durum, anonim kullanıcıların sınırsız istek atarak CPU yoğun rembg işlemleriyle sistemi kolayca yormasına izin veriyor. `flask-limiter` bağımlılığı zaten eklenmiş olmasına rağmen kullanılmıyor, bu da koruma eksikliğini daha da belirgin kılıyor. 【F:app.py†L21-L35】【F:requirements.txt†L1-L8】

## 2) Model yüklenemediğinde servis ayakta ama işlevsiz
- `u2net` modeli import sırasında yüklenemezse `session = None` olarak devam ediliyor ve süreç yine de servisleniyor. Bu durumda `/health` `model_loaded` bilgisini dönse de ana endpoint'ler 500 hatası vererek çalışmaz hale geliyor; yani başlangıçta sorun fark edilmese de canlı ortamda işlevsiz bir servis ayağa kalkabiliyor. 【F:app.py†L24-L114】

## 3) CPU yoğun işlemlerde koruyucu önlem yok
- Hem base64 hem dosya yükleme endpoint'lerinde gelen görüntüler doğrudan rembg / OpenCV ile işleniyor; yeniden boyutlandırma, zaman aşımı, kuyruğa alma ya da worker sayısını ayarlama gibi önlemler yok. Tek bir büyük görsel bile (50 MB sınırına kadar) iki gunicorn worker'ı uzun süre bloklayarak hizmet kesintisine yol açabilir. 【F:app.py†L84-L200】

## 4) Deployment script'inde varsayılan izin riski
- Systemd servisi varsayılan olarak `www-data` kullanıcısıyla çalıştırılıyor ancak `CHOWN_APP_DIR` değişkeni false olduğu için kod dizini çoğu kurulumda root'un sahipliğinde kalıyor. Bu durumda servis, repo dosyalarını okuyamazsa veya venv ikililerini çalıştıramazsa başarısız olabilir; betiğin varsayılanlarının güvenli biçimde tamamlanması için sahiplik devrinin açıkça yapılması gerekiyor. 【F:deployment/deploy_twizer.sh†L20-L68】
