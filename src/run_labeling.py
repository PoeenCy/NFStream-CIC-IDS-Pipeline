# src/run_labeling.py
import pandas as pd
import time
import os
import sys

# --- HÀM GÁN NHÃN CHUNG ---
def apply_labeling_logic(df, day):
    """Điều phối, gọi hàm gán nhãn tương ứng cho từng ngày."""
    print(f"Áp dụng logic gán nhãn cho ngày: {day.upper()}")
    
    # Định nghĩa IP chung
    ATTACKER_KALI = '205.174.165.73'
    VICTIM_WEBSERVER_LOCAL = '192.168.10.50'
    VICTIM_UBUNTU12_LOCAL = '192.168.10.51'
    VICTIM_VISTA_LOCAL = '192.168.10.8'
    
    # Chuẩn hóa dữ liệu
    df['src_ip'] = df['src_ip'].astype(str).str.strip()
    df['dst_ip'] = df['dst_ip'].astype(str).str.strip()
    
    # Bắt đầu với nhãn Benign
    df['label'] = 'Benign'

    # Gọi hàm gán nhãn cụ thể
    if day == 'monday':
        # Monday chỉ có traffic Benign, không cần làm gì thêm
        pass
    elif day == 'tuesday':
        # Brute Force (FTP & SSH)
        brute_force_mask = (df['src_ip'] == ATTACKER_KALI) & \
                           (df['dst_ip'] == VICTIM_WEBSERVER_LOCAL) & \
                           (df['dst_port'].isin([21, 22]))
        df.loc[brute_force_mask, 'label'] = 'BruteForce'
    elif day == 'wednesday':
        # DoS attacks on WebServer
        dos_mask = (df['src_ip'] == ATTACKER_KALI) & (df['dst_ip'] == VICTIM_WEBSERVER_LOCAL)
        df.loc[dos_mask, 'label'] = 'DoS'
        # Heartbleed attack on Ubuntu12
        heartbleed_mask = (df['src_ip'] == ATTACKER_KALI) & (df['dst_ip'] == VICTIM_UBUNTU12_LOCAL)
        df.loc[heartbleed_mask, 'label'] = 'Heartbleed'
    elif day == 'thursday':
        # Web Attacks (Brute Force, XSS, Sql Injection)
        web_attack_mask = (df['src_ip'] == ATTACKER_KALI) & (df['dst_ip'] == VICTIM_WEBSERVER_LOCAL)
        df.loc[web_attack_mask, 'label'] = 'WebAttack'
        # Infiltration: Vista bị chiếm và quét mạng nội bộ
        infiltration_scan_mask = (df['src_ip'] == VICTIM_VISTA_LOCAL) & (df['dst_ip'].str.startswith('192.168.10.'))
        df.loc[infiltration_scan_mask, 'label'] = 'Infiltration'
    elif day == 'friday':
        # Logic phức tạp của ngày Thứ Sáu
        ATTACKER_IP_NAT = '172.16.0.1' 
        CNC_SERVER_IP = '205.174.165.73' # Kali đóng vai trò C&C
        BOT_IPS = {'192.168.10.15', '192.168.10.8', '192.168.10.9', '192.168.10.14', '192.168.10.5'}
        DDOS_ATTACKERS = {'205.174.165.69', '205.174.165.70', '205.174.165.71'}

        # 1. Gán nhãn Botnet
        botnet_mask = (df['src_ip'].isin(BOT_IPS) & (df['dst_ip'] == CNC_SERVER_IP))
        df.loc[botnet_mask, 'label'] = 'Botnet'
        
        # 2. Gán nhãn DDoS
        ddos_mask = (df['src_ip'].isin(DDOS_ATTACKERS) | df['src_ip'] == ATTACKER_IP_NAT) & \
                    (df['dst_ip'] == VICTIM_WEBSERVER_LOCAL)
        df.loc[ddos_mask, 'label'] = 'DDoS'

        # 3. Gán nhãn PortScan (khác với DDoS)
        portscan_mask = (df['label'] == 'Benign') & \
                        (df['src_ip'] == ATTACKER_KALI) & \
                        (df['dst_ip'] == VICTIM_WEBSERVER_LOCAL)
        df.loc[portscan_mask, 'label'] = 'PortScan'
    else:
        print(f"CẢNH BÁO: Không có logic gán nhãn nào cho ngày '{day}'.")

    return df

# --- HÀM CHÍNH ---
def label_from_parquet(input_path, output_path, day):
    print(f"--- BẮT ĐẦU GÁN NHÃN: {input_path} ---")
    start_time = time.time()
    
    if not os.path.exists(input_path):
        print(f"LỖI: Không tìm thấy file parquet tại: {input_path}")
        return
        
    try:
        df = pd.read_parquet(input_path)
        print(f"Đã đọc thành công {len(df)} luồng.")
    except Exception as e:
        print(f"LỖI khi đọc file parquet: {e}")
        return

    # Áp dụng logic gán nhãn
    df_labeled = apply_labeling_logic(df, day)

    # Lưu kết quả
    print(f"\nĐang lưu kết quả vào: {output_path}...")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df_labeled.to_csv(output_path, index=False)

    end_time = time.time()
    elapsed_time = end_time - start_time
    print("\n--- HOÀN THÀNH GÁN NHÃN ---")
    print(f"Đã lưu thành công vào: {output_path}")
    print("Thống kê nhãn cuối cùng:")
    print(df_labeled['label'].value_counts().to_markdown())
    print(f"Tổng thời gian: {elapsed_time:.2f} giây.")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Sử dụng: python run_labeling.py <ngày> <đường_dẫn_parquet_đầu_vào> <đường_dẫn_csv_đầu_ra>")
        print("Ví dụ: python run_labeling.py tuesday /app/output/tuesday_raw_flows.parquet /app/output/tuesday_labeled_data.csv")
        sys.exit(1)
        
    day_of_week = sys.argv[1].lower()
    input_parquet = sys.argv[2]
    output_csv = sys.argv[3]
    
    label_from_parquet(input_parquet, output_csv, day_of_week)