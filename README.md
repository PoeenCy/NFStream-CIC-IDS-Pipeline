# Hướng dẫn Cài đặt và Thực thi Pipeline

Tài liệu này cung cấp hướng dẫn kỹ thuật đầy đủ để cài đặt môi trường, chuẩn bị dữ liệu và thực thi pipeline xử lý dữ liệu từ kho lưu trữ này.

## 1. Giới thiệu

Pipeline này được đóng gói bằng Docker và được thiết kế để thực hiện hai nhiệm vụ chính:

1.  **Giai đoạn 1 (Trích xuất):** Đọc các file `.pcap` thô (từ CIC-IDS-2017), sử dụng `nfstream` để trích xuất đặc trưng, và lưu kết quả dưới dạng file `.parquet`.

## 2. Yêu cầu Cài đặt (Prerequisites)

Cần đảm bảo các công cụ sau đã được cài đặt và đang hoạt động trên hệ thống:
*   **Docker Desktop:** Để xây dựng (build) và chạy (run) môi trường container. (Tải tại: `https://www.docker.com/products/docker-desktop/`)
*   **Dung lượng đĩa trống:** Tối thiểu 100GB (khuyến nghị) để chứa bộ dữ liệu `.pcap` gốc và các file `.parquet` đầu ra.

### 3. Chạy Xử lý
1.  Mở **PowerShell** (trên Windows) hoặc **Terminal** (trên macOS/Linux).
2.  Dùng lệnh `cd` để đi vào thư mục `cic_work` của bạn.
    ```bash
    cd path/to/your/cic_work
    ```
3.  **Sao chép và dán lệnh dưới đây** để xử lý file. Lệnh này sẽ tự động tải image `poeency/nfstream-cic-ids-pipeline` từ Docker Hub về nếu bạn chưa có.

💡 **Lệnh để xử lý ngày Thứ Hai:**
```bash
docker run --rm -v "./data:/app/data" -v "./output:/app/output" poeency/nfstream-cic-ids-pipeline:latest python src/run_extraction.py /app/data/Monday-WorkingHours.pcap /app/output/monday_raw_flows.parquet
```

💡 **Ví dụ: Để xử lý ngày Thứ Ba,** chỉ cần thay đổi tên file:
```bash
docker run --rm -v "./data:/app/data" -v "./output:/app/output" poeency/nfstream-cic-ids-pipeline:latest python src/run_extraction.py /app/data/Tuesday-WorkingHours.pcap /app/output/tuesday_raw_flows.parquet
```

Sau khi lệnh chạy xong, file `.parquet` tương ứng sẽ xuất hiện trong thư mục `output` của bạn.

---

### Xử lý Hàng loạt (Tùy chọn)

Nếu bạn có nhiều file, hãy tạo một script `run_all.ps1` (cho Windows) hoặc `run_all.sh` (cho macOS/Linux) bên trong thư mục `cic_work` với nội dung dưới đây, sau đó chạy nó.

#### **Cho Windows (file `run_all.ps1`)**
```powershell
# Lặp qua tất cả các file .pcap trong thư mục data
Get-ChildItem -Path ".\data" -Filter *.pcap | ForEach-Object {
    $baseName = $_.BaseName
    Write-Host "--- Processing $($baseName) ---"
    docker run --rm -v "./data:/app/data" -v "./output:/app/output" poeency/nfstream-cic-ids-pipeline:latest python src/run_extraction.py "/app/data/$($_.Name)" "/app/output/$($baseName.ToLower())_raw_flows.parquet"
}
```
**Cách chạy:** Mở PowerShell trong thư mục `cic_work` và gõ `.\run_all.ps1`.

#### **Cho macOS / Linux (file `run_all.sh`)**
```bash
#!/bin/bash
for pcap_file in ./data/*.pcap; do
    base_name=$(basename "$pcap_file" .pcap)
    echo "--- Processing $base_name ---"
    docker run --rm -v "./data:/app/data" -v "./output:/app/output" poeency/nfstream-cic-ids-pipeline:latest python src/run_extraction.py "/app/data/$(basename $pcap_file)" "/app/output/$(echo $base_name | tr '[:upper:]' '[:lower:]')_raw_flows.parquet"
done
```
**Cách chạy:** Mở Terminal trong thư mục `cic_work` và gõ `bash run_all.sh`.

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