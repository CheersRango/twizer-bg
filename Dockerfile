FROM python:3.11-slim

# OpenCV iÃ§in gerekli sistem kÃ¼tÃ¼phaneleri
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libgl1 \
        libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Model'i Ã¶nceden indir
RUN python -c "from rembg import new_session; new_session('u2net')" || true

# App dosyalarÄ±nÄ± kopyala
COPY . .

# Health check (curl yerine python kullan)
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('https://api.twizer.xyz/health')" || exit 1

EXPOSE 5000

# Production server
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--threads", "4", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-", "app:app"]


