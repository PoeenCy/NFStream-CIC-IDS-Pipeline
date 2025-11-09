# NFStream-CIC-IDS-Pipeline

![Python](https://img.shields.io/badge/python-3.10%2B-brightgreen.svg)
![Docker](https://img.shields.io/badge/docker-Ready-blue.svg)

Dự án này cung cấp một pipeline xử lý dữ liệu hoàn chỉnh và một bộ dữ liệu đã được xác thực, được xây dựng với một mục tiêu cốt lõi: tạo ra nền tảng để phát triển các **Hệ thống Phát hiện Xâm nhập Mạng (NIDS)** thế hệ mới, có khả năng triển khai thực tế và hoạt động hiệu quả tại **lớp biên (edge)** của mạng.

---

## 1. Vấn đề: "Khoảng cách Triển khai" trong NIDS

Hầu hết các mô hình NIDS dựa trên học máy (ML) đều thất bại khi triển khai trong thực tế. Lý do là sự **Thiếu nhất quán Đặc trưng (Feature Inconsistency)**:

Các mô hình được huấn luyện trong môi trường lab (sử dụng các bộ công cụ nặng như `CICFlowMeter`) dựa trên các đặc trưng mà các thiết bị biên (như Raspberry Pi, router) không thể trích xuất được trong thời gian thực do hạn chế về tài nguyên. Điều này tạo ra một **"Khoảng cách Triển khai" (The Deployment Gap)**, khiến các cảnh báo an ninh trở nên không đáng tin cậy.

## 2. Giải pháp: Pipeline Đồng nhất với NFStream

Dự án này giải quyết "Khoảng cách Triển khai" bằng cách đề xuất một **chuỗi công cụ đồng nhất (unified toolchain)**. Chúng tôi thay thế hoàn toàn `CICFlowMeter` bằng **[`NFStream`](https://github.com/nfstream/nfstream)**—một bộ trích xuất luồng mạng nhẹ, hiệu năng cao—cho cả hai giai đoạn:

* **Huấn luyện (Offline):** Phân tích file `.pcap` thô từ bộ dữ liệu **[CIC-IDS-2017](https://www.unb.ca/cic/datasets/ids-2017.html)**.
* **Triển khai (Online):** Giám sát traffic mạng trực tiếp trên thiết bị biên.

Cách tiếp cận này đảm bảo các đặc trưng mà mô hình học được giống hệt 100% với các đặc trưng mà nó sẽ thấy trong thực tế, mang lại các cảnh báo an ninh chính xác và đáng tin cậy.

## 3. Nội dung Kho lưu trữ (Repository)

Repo này cung cấp:

1.  **Pipeline Xử lý Dữ liệu:** Một pipeline `Python/Docker` hoàn chỉnh (trong `src/`) để chuyển đổi `.pcap` thô -> `.parquet` (đặc trưng NFStream) -> `.csv` (đã gán nhãn).
2.  **Logic Gán nhãn Nâng cao:** Một bộ quy tắc gán nhãn tinh chỉnh (hybrid labeling) cho CIC-IDS-2017, có khả năng xử lý các yếu tố thực tế như **NAT** và phân biệt `PortScan`/`DDoS` bằng heuristic hành vi.
3.  **Báo cáo Xác thực (Validation):** Một báo cáo phân tích chi tiết chứng minh rằng `NFStream` bảo toàn được bản chất dữ liệu và các lớp tấn công vẫn có khả năng phân tách cao.

## 4. Bằng chứng về Chất lượng Dữ liệu

Việc thay đổi công cụ trích xuất đặc trưng là vô nghĩa nếu nó làm mất đi bản chất của dữ liệu. Chúng tôi đã xác thực không gian đặc trưng 86 chiều mới do `NFStream` tạo ra.

Kết quả phân tích t-SNE (xem bên dưới) cho thấy các lớp tấn công (`DDoS`, `PortScan`, `Botnet`) và traffic `Benign` vẫn tạo thành các cụm riêng biệt, có ranh giới rõ ràng. Điều này khẳng định dữ liệu có **tính khả học (learnability)** rất cao.

*(Chèn ảnh t-SNE của bạn vào đây)*

➡️ **Xem Báo cáo Phân tích và Xác thực Dữ liệu chi tiết tại: [docs/ANALYSIS.md](./docs/ANALYSIS.md)**

## 5. Hướng dẫn Sử dụng và Tái tạo

Toàn bộ hướng dẫn chi tiết về cách thiết lập môi trường (Docker), chuẩn bị dữ liệu, và chạy pipeline được đặt trong một tài liệu riêng.

➡️ **Xem Hướng dẫn Bắt đầu tại: [GUIDE.md](./GUIDE.md)**

## 6. Cấu trúc Thư mục

```
. ├── data/ # (Bị bỏ qua bởi .gitignore) 
│ ├── raw/ # Đặt file .pcap gốc tại đây 
│ ├── processed/ # Đầu ra .parquet 
│ └── labeled/ # Đầu ra .csv cuối cùng 
├── docs/ 
│ ├── ANALYSIS.md # Báo cáo phân tích (t-SNE, Boxplots) 
│ └── images/ # Hình ảnh cho tài liệu 
├── src/ 
│ ├── main.py # Bộ điều phối chính 
│ ├── config.py # "Bộ não" chứa IP, ngưỡng 
│ ├── feature_extractor.py 
│ └── labelers/ 
├── Dockerfile 
├── docker-compose.yml 
├── requirements.txt 
└── README.md 
```
## 7. Đóng góp
Dự án này được phát triển và duy trì bởi **Trần Thanh Nhã**, thuộc **CFT**.

