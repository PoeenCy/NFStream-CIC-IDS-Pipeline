# 🧩 Hướng dẫn Sử dụng Pipeline Trích xuất Dữ liệu CIC-IDS-2017

Tài liệu này hướng dẫn quy trình đầy đủ để sử dụng Docker image đã được xây dựng sẵn nhằm mục đích chuyển đổi các file dữ liệu mạng thô (`.pcap`) của bộ dữ liệu CIC-IDS-2017 thành định dạng Parquet (`.parquet`) hiệu quả hơn.

---

## 🎯 Mục tiêu

Mục tiêu chính là chạy một công cụ đã được đóng gói sẵn để xử lý các file `.pcap` có dung lượng rất lớn thành các file `.parquet` có dung lượng nhỏ hơn và tốc độ truy vấn nhanh hơn, phục vụ cho các bước phân tích dữ liệu về sau.

---

## 🖥️ Yêu cầu Hệ thống

Trước khi bắt đầu, cần đảm bảo hệ thống đáp ứng các yêu cầu sau

- Docker Desktop Đã được cài đặt và đang chạy.  
  👉 [Tải tại đây](httpswww.docker.comproductsdocker-desktop)
- Kết nối Internet Để tải Docker image và bộ dữ liệu.
- Dung lượng đĩa trống lớn Bộ dữ liệu CIC-IDS-2017 rất lớn (hàng chục đến hàng trăm GB).  
  Cần đảm bảo có đủ không gian lưu trữ cho cả file `.pcap` gốc và file `.parquet` đầu ra.
- Terminal hoặc PowerShell Để thực thi các dòng lệnh.

---

## ⚙️ Quy trình Thực hiện

Vui lòng thực hiện tuần tự theo các bước dưới đây.

---
## Quy trình Thực hiện

### Bước 1: Tải Mã nguồn (Clone Repository)

Đầu tiên, tải mã nguồn của pipeline này về máy và di chuyển vào thư mục dự án.

```
# Tải kho lưu trữ
git clone [https://github.com/PoeenCy/NFStream-CIC-IDS-Pipeline.git](https://github.com/PoeenCy/NFStream-CIC-IDS-Pipeline.git)

# Di chuyển vào thư mục dự án
cd NFStream-CIC-IDS-Pipeline

```

### 🔹 Bước 2: Chuẩn bị dữ liệu Gốc (.pcap)

1. Truy cập vào trang web chính thức của bộ dữ liệu CIC-IDS-2017 tại Đại học New Brunswick  
   🔗 [Bộ dữ liệu thô tại đây!](http://cicresearch.ca/CICDataset/CIC-IDS-2017/Dataset/CIC-IDS-2017/PCAPs/)
2. Tải về các file `.pcap` cho các ngày cần xử lý (ví dụ  
   `Monday-WorkingHours.pcap`, `Tuesday-WorkingHours.pcap`, v.v.).

Đặt các file .pcap đó vào thư mục /data có sẵn trong dự án.

Cấu trúc thư mục data/ sẽ trông như sau:

NFStream-CIC-IDS-Pipeline/
├── data/
│   ├── Friday-WorkingHours.pcap
│   ├── Tuesday-WorkingHours.pcap
│   └── ...
└── labeled/
│   └── .gitkeep
├── src/
└── ... (các file khác của dự án)
(Lưu ý: Thư mục data/ được liệt kê trong .gitignore, vì vậy các file dữ liệu lớn sẽ không bị đẩy lên Git).

### 🔹 Bước 3 Chạy Pipeline Trích xuất

Một dòng lệnh duy nhất sẽ được sử dụng để tự động tải image từ Docker Hub và chạy quá trình xử lý.

1. Mở Terminal (macOSLinux) hoặc PowerShell (Windows).  
2. Dùng lệnh `cd` để điều hướng vào thư mục `NFStream-CIC-IDS-Pipeline`.
3. Sao chép và chạy lệnh dưới đây. Lệnh này xử lý file `Monday-WorkingHours.pcap`.

💡 Lệnh mẫu cho ngày Thứ Hai

```bash
docker run --rm 
-v $(pwd)dataappdata 
-v $(pwd)outputappoutput 
poeencynfstream-cic-ids-pipelinelatest 
python srcrun_extraction.py appdataMonday-WorkingHours.pcap appoutputmonday_raw_flows.parquet
🔹 Lưu ý (Windows PowerShell) Thay $(pwd) bằng ${pwd}.
```

```
🧠 Giải thích Lệnh
docker run --rm:	Khởi chạy container và tự động xóa nó sau khi chạy xong.
-v $(pwd)dataappdata:	Mount thư mục data trên máy host vào appdata trong container.
-v $(pwd)outputappoutput:	Mount thư mục output trên máy host vào appoutput trong container.
poeencynfstream-cic-ids-pipelinelatest:	Image trên Docker Hub (tự động tải nếu chưa có).
python srcrun_extraction.py ...:	Lệnh chính để chạy quá trình trích xuất bên trong container.
```

Ví dụ Để xử lý ngày Thứ Ba, chỉ cần thay tên file
```bash
docker run --rm 
-v $(pwd)dataappdata 
-v $(pwd)outputappoutput 
poeencynfstream-cic-ids-pipelinelatest 
python srcrun_extraction.py appdataTuesday-WorkingHours.pcap appoutputtuesday_raw_flows.parquet
```

🔹 Bước 4 Theo dõi Tiến trình và Kiểm tra Kết quả
Sau khi chạy lệnh, output trên màn hình sẽ bắt đầu bằng

--- BẮT ĐẦU TRÍCH XUẤT appdata....pcap ---
Ngay sau đó, một thanh tiến độ sẽ xuất hiện, cho biết số luồng đã được xử lý.

(Hình 2 Quá trình chạy trong terminal với thanh tiến độ)

⏳ Quá trình này có thể mất vài phút đến vài giờ tùy vào kích thước file và tài nguyên hệ thống.

Khi hoàn tất, sẽ thấy thông báo
```
--- HOÀN THÀNH TRÍCH XUẤT ---
Sau đó, kiểm tra thư mục output, bạn sẽ thấy file .parquet tương ứng, ví dụ
```
```
output
└── monday_raw_flows.parquet
(Hình 3 File monday_raw_flows.parquet đã được tạo thành công trong thư mục output)
```

🧯 Xử lý Lỗi Thường Gặp
❌ Lỗi docker command not found
Nguyên nhân Docker chưa được cài đặt hoặc chưa khởi động.

Giải pháp Cài đặt Docker Desktop và đảm bảo Docker đang chạy.

❌ Lỗi File not found (từ bên trong container)
Nguyên nhân Cấu trúc thư mục sai hoặc bạn chưa cd vào đúng thư mục cic_processing.

Giải pháp Kiểm tra lại cấu trúc và đảm bảo bạn đang ở đúng vị trí khi chạy lệnh.

❌ Lỗi (WindowsmacOS) path is not shared hoặc permission denied
Nguyên nhân Docker chưa được cấp quyền truy cập vào ổ đĩathư mục chứa dự án.

Giải pháp

Mở Docker Desktop → Settings → Resources → File Sharing

Bấm vào dấu + để thêm đường dẫn đến thư mục cic_processing

Nhấn Apply & Restart

(Hình 4 Cài đặt chia sẻ file (File Sharing) trong Docker Desktop)