# src/labelers/friday_labeler.py
import pandas as pd

def apply_logic(df):
    """
    Áp dụng logic gán nhãn cụ thể cho ngày Thứ Sáu.
    Bao gồm gán nhãn Botnet và phân tích hành vi để phân biệt DDoS/PortScan.
    """
    print("Áp dụng logic gán nhãn cho: Friday")
    
    # --- ĐỊNH NGHĨA CÁC THAM SỐ CHO NGÀY THỨ SÁU ---
    ATTACKER_IP_NAT = '172.16.0.1' 
    VICTIM_IP_UBUNTU = '192.168.10.50'
    CNC_SERVER_IP = '205.174.165.73'
    BOT_IPS = {'192.168.10.15', '192.168.10.8', '192.168.10.9', '192.168.10.14', '192.168.10.5'}
    DDOS_COUNT_THRESHOLD = 10000 

    # --- BẮT ĐẦU GÁN NHÃN ---

    # 1. Gán nhãn Botnet (Logic này chạy trước)
    botnet_mask = (df['src_ip'].isin(BOT_IPS) & (df['dst_ip'] == CNC_SERVER_IP))
    df.loc[botnet_mask, 'label'] = 'Botnet'
    
    # 2. Lọc ra tất cả các luồng tấn công chính (từ NAT đến Victim)
    attack_flows_mask = (df['src_ip'] == ATTACKER_IP_NAT) & (df['dst_ip'] == VICTIM_IP_UBUNTU)
    
    if attack_flows_mask.any():
        print(f" -> Tìm thấy {attack_flows_mask.sum()} luồng tấn công tiềm năng từ {ATTACKER_IP_NAT}.")
        
        # --- PHÂN TÍCH HÀNH VI ĐỂ PHÂN LOẠI ---
        # Chỉ phân tích trên các luồng tấn công
        attack_df = df[attack_flows_mask].copy()
        
        # Đếm số lần xuất hiện của mỗi cổng đích
        port_counts = attack_df['dst_port'].value_counts()
        
        # Tìm các cổng bị tấn công với số lượng cực lớn -> mục tiêu DDoS
        ddos_target_ports = port_counts[port_counts > DDOS_COUNT_THRESHOLD].index.tolist()
        
        if ddos_target_ports:
            print(f" -> Các cổng được xác định là mục tiêu DDoS (vượt ngưỡng {DDOS_COUNT_THRESHOLD}): {ddos_target_ports}")
            
            # Gán nhãn DDoS cho các luồng nhắm vào các cổng này
            ddos_mask = attack_flows_mask & (df['dst_port'].isin(ddos_target_ports))
            df.loc[ddos_mask, 'label'] = 'DDoS'
            
            # Gán nhãn PortScan cho TẤT CẢ các luồng tấn công CÒN LẠI
            # (Là luồng tấn công nhưng chưa được gán nhãn DDoS)
            portscan_mask = attack_flows_mask & (df['label'] == 'Benign')
            df.loc[portscan_mask, 'label'] = 'PortScan'
        else:
            # Nếu không có cổng nào vượt ngưỡng, giả định toàn bộ khối tấn công là PortScan
            print(" -> Không tìm thấy cổng nào bị tấn công tập trung. Giả định toàn bộ là PortScan.")
            df.loc[attack_flows_mask, 'label'] = 'PortScan'
            
    # Trả về DataFrame đã được gán nhãn
    return df