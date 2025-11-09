# Hướng dẫn Cài đặt và Thực thi Pipeline

Tài liệu này cung cấp hướng dẫn kỹ thuật đầy đủ để cài đặt môi trường, chuẩn bị dữ liệu và thực thi pipeline xử lý dữ liệu từ kho lưu trữ này.

## 1. Giới thiệu

Pipeline này được đóng gói bằng Docker và được thiết kế để thực hiện hai nhiệm vụ chính:

1.  **Giai đoạn 1 (Trích xuất):** Đọc các file `.pcap` thô (từ CIC-IDS-2017), sử dụng `nfstream` để trích xuất đặc trưng, và lưu kết quả dưới dạng file `.parquet`.

## 2. Yêu cầu Cài đặt (Prerequisites)

Cần đảm bảo các công cụ sau đã được cài đặt và đang hoạt động trên hệ thống:
*   **Git:** Để tải (clone) kho lưu trữ.
*   **Docker Desktop:** Để xây dựng (build) và chạy (run) môi trường container. (Tải tại: `https://www.docker.com/products/docker-desktop/`)
*   **Dung lượng đĩa trống:** Tối thiểu 100GB (khuyến nghị) để chứa bộ dữ liệu `.pcap` gốc và các file `.parquet` đầu ra.

## 3. Quy trình Thực thi

### Bước 1: Tải Mã nguồn (Clone Repository)

Mở Terminal hoặc PowerShell, sao chép kho lưu trữ về máy và di chuyển vào thư mục dự án:

```bash
git clone https://github.com/PoeenCy/NFStream-CIC-IDS-Pipeline.git
cd NFStream-CIC-IDS-Pipeline
```

### Bước 2: Chuẩn bị Dữ liệu Thô (`.pcap`)

1.  Tải các file `.pcap` gốc từ trang chủ [CIC-IDS-2017](http://cicresearch.ca/CICDataset/CIC-IDS-2017/Dataset/CIC-IDS-2017/PCAPs/).
2.  Tạo một thư mục mới tên là `data` bên trong thư mục dự án.
3.  Sao chép tất cả các file `.pcap` đã tải vào thư mục `data` vừa tạo.

Cấu trúc thư mục của dự án lúc này sẽ là:
```plaintext
\NFStream-CIC-IDS-Pipeline
├── GUIDE.md
├── .gitignore
├── .dockerignore
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── data
│   ├── Monday-WorkingHours.pcap
│   ├── ...
├── output
│   ├── monday_raw_flows.parquet
│   └── ...
└── src
    ├── __init__.py
    ├── run_extraction.py
    ├── run_labeling.py
    └── labelers
        ├── __init__.py
        └── friday_labeler.py
```
*(Lưu ý: Thư mục `data/` được cấu hình trong `.gitignore` để tránh đưa dữ liệu lớn lên Git).*

### Bước 3: Xây dựng (Build) Image Docker

Trước khi chạy lần đầu tiên, cần build image Docker. Lệnh này sẽ đọc `Dockerfile` và cài đặt tất cả các thư viện (như `nfstream`, `pandas`) vào một image cục bộ tên là `extractor`.

```bash
docker-compose build
```

### Bước 4: Thực thi Giai đoạn 1 (Trích xuất `.parquet`)

Sử dụng `docker-compose run` để thực thi script `run_extraction.py` bên trong container. Container sẽ tự động ánh xạ (mount) thư mục `data/` (đầu vào) và `output/` (đầu ra).

**Lệnh mẫu (Xử lý ngày Thứ Hai):**
```bash
docker-compose run --rm extractor \
  python src/run_extraction.py /app/data/Monday-WorkingHours.pcap /app/output/monday_raw_flows.parquet
```

**Lệnh mẫu (Xử lý ngày Thứ Ba):**
```bash
docker-compose run --rm extractor \
  python src/run_extraction.py /app/data/Tuesday-WorkingHours.pcap /app/output/tuesday_raw_flows.parquet
```
- `--rm`: Tự động xóa container sau khi chạy xong để giữ hệ thống sạch sẽ.
- `extractor`: Tên của service được định nghĩa trong `docker-compose.yml`.
- `/app/data/` và `/app/output/`: Là các đường dẫn bên trong container, tương ứng với thư mục `data/` và `output/` trên máy của bạn.

Quá trình này sẽ mất nhiều thời gian và sẽ hiển thị một thanh tiến độ trong terminal.

### Bước 5: Kiểm tra Kết quả (Giai đoạn 1)

Sau khi hoàn tất, một thư mục `output/` sẽ được tự động tạo ra (nếu chưa tồn tại) ở thư mục gốc dự án, chứa các file `.parquet` đã được xử lý.

```plaintext
NFStream-CIC-IDS-Pipeline/
├── data/
│   └── ... (file .pcap)
├── output/
│   ├── monday_raw_flows.parquet
│   └── tuesday_raw_flows.parquet
└── src/
    └── ...
```

## 5. Xử lý Hàng loạt (Batch Processing)

Việc chạy từng lệnh cho mỗi file rất tốn thời gian. Các script dưới đây giúp tự động hóa quá trình này.

### 1. Trên Linux/macOS (Bash Script)

Tạo file `run_all.sh` trong thư mục gốc dự án:

```bash
#!/bin/bash
# run_all.sh
# Tu dong tim tat ca file .pcap trong ./data va chay Giai doan 1

echo "--- BAT DAU XU LY HANG LOAT ---"
# Dam bao image duoc build
docker-compose build

DATA_DIR="./data"
OUTPUT_DIR="./output"

# Tao thu muc output neu chua co
mkdir -p $OUTPUT_DIR

# Kiem tra thu muc data
if [ ! -d "$DATA_DIR" ]; then
    echo "LOI: Khong tim thay thu muc 'data'. Vui long tao va dat cac file .pcap vao do."
    exit 1
fi

# Lap qua tung file .pcap
for pcap_file in "$DATA_DIR"/*.pcap; do
    base_name=$(basename "$pcap_file" .pcap)
    
    input_path="/app/data/${base_name}.pcap"
    output_path="/app/output/${base_name,,}_raw_flows.parquet" # Chuyen ten sang chu thuong

    echo "=================================================="
    echo "Dang xu ly: $base_name"
    echo "=================================================="

    docker-compose run --rm extractor python src/run_extraction.py "$input_path" "$output_path"
done

echo "--- HOAN THANH XU LY HANG LOAT ---"
```

**Cách chạy:**
```bash
chmod +x run_all.sh
./run_all.sh
```

### 2. Trên Windows (PowerShell Script)

Tạo file `run_all.ps1` trong thư mục gốc dự án:

```powershell
# run_all.ps1
# Tu dong tim tat ca file .pcap trong ./data va chay Giai doan 1

Write-Host "--- BAT DAU XU LY HANG LOAT ---" -ForegroundColor Green
# Dam bao image duoc build
docker-compose build

$dataDir = ".\data"
$outputDir = ".\output"

# Tao thu muc output neu chua co
if (-not (Test-Path $outputDir)) {
    New-Item -ItemType Directory -Path $outputDir
}

# Kiem tra thu muc data
if (-not (Test-Path $dataDir -PathType Container)) {
    Write-Host "LOI: Khong tim thay thu muc 'data'. Vui long tao va dat cac file .pcap vao do." -ForegroundColor Red
    exit 1
}

$pcapFiles = Get-ChildItem -Path $dataDir -Filter *.pcap

foreach ($pcapFile in $pcapFiles) {
    $baseName = $pcapFile.BaseName
    
    $inputPath = "/app/data/$($pcapFile.Name)"
    $outputPath = "/app/output/$($baseName.ToLower())_raw_flows.parquet" # Chuyen ten sang chu thuong

    Write-Host "==================================================" -ForegroundColor Cyan
    Write-Host "Dang xu ly: $baseName" -ForegroundColor Cyan
    Write-Host "==================================================" -ForegroundColor Cyan

    docker-compose run --rm extractor python src/run_extraction.py $inputPath $outputPath
}

Write-Host "--- HOAN THANH XU LY HANG LOAT ---" -ForegroundColor Green
```

**Cách chạy:**
```powershell
.\run_all.ps1
```
*(Lưu ý: Nếu gặp lỗi execution policy, có thể cần chạy `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` trước).*

## 5. Xử lý Sự cố (Troubleshooting)

-   **Lỗi:** `docker: command not found` (hoặc tương tự).
    -   **Nguyên nhân:** Docker chưa được cài đặt hoặc chưa được khởi động.
    -   **Giải pháp:** Cài đặt Docker Desktop và đảm bảo nó đang chạy.

-   **Lỗi:** `File not found` (báo từ bên trong container).
    -   **Nguyên nhân:** Cấu trúc thư mục ở Bước 2 bị sai, hoặc lệnh `docker-compose run` được thực thi từ một thư mục khác.
    -   **Giải pháp:** Đảm bảo các file `.pcap` nằm trong thư mục `data/` và lệnh được chạy từ thư mục gốc của dự án.

-   **Lỗi (Windows/macOS):** `path is not shared` hoặc `permission denied`.
    -   **Nguyên nhân:** Docker Desktop cần được cấp quyền để truy cập vào ổ đĩa/thư mục chứa dự án.
    -   **Giải pháp:** Mở **Settings** của Docker Desktop -> **Resources** -> **File Sharing**. Thêm đường dẫn đến thư mục dự án (ví dụ: `D:\NCKH_Project`) và bấm **Apply & Restart**.