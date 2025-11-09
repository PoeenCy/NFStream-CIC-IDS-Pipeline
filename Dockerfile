# Dockerfile
# Sử dụng một image Python 3.10 ổn định làm base
FROM python:3.10-slim

# Thiết lập thư mục làm việc bên trong container
WORKDIR /app

# Cài đặt các gói phụ thuộc hệ thống cần thiết cho nfstream (ví dụ: libpcap)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpcap-dev \
    && rm -rf /var/lib/apt/lists/*

# Sao chép tệp requirements.txt trước để tận dụng Docker layer caching
COPY requirements.txt .

# Cài đặt các thư viện Python
RUN pip install --no-cache-dir -r requirements.txt

# Sao chép toàn bộ mã nguồn của dự án vào container
COPY ./src ./src