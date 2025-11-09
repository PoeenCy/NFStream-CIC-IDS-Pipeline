# src/run_extraction.py
import nfstream
import pandas as pd
import time
import os
import sys
from tqdm import tqdm

def pcap_to_raw_flows(pcap_path, output_path):
    print(f"--- BẮT ĐẦU TRÍCH XUẤT: {pcap_path} ---")
    start_time = time.time()

    if not os.path.exists(pcap_path):
        print(f"LỖI: Không tìm thấy file pcap tại: {pcap_path}")
        return

    try:
        streamer = nfstream.NFStreamer(source=pcap_path, decode_tunnels=True, statistical_analysis=True)
        flows_data = []
        flow_attributes = ['id', 'src_ip', 'src_port', 'dst_ip', 'dst_port', 'protocol', 'application_name', 'bidirectional_packets', 'bidirectional_bytes']

        tqdm_streamer = tqdm(streamer, unit="flows", desc="Đang xử lý")
        
        for flow in tqdm_streamer:
            flow_dict = {attr: getattr(flow, attr, None) for attr in flow_attributes}
            flows_data.append(flow_dict)

        if not flows_data:
            print(f"\nCẢNH BÁO: Không có luồng nào được trích xuất.")
            return

        print(f"\nĐã xử lý xong. Chuyển đổi {len(flows_data)} luồng sang DataFrame...")
        df = pd.DataFrame(flows_data)

    except Exception as e:
        print(f"\nLỖI trong quá trình xử lý: {e}")
        return

    print(f"Đang lưu vào {output_path}...")
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df.to_parquet(output_path, index=False, engine='pyarrow')
    except Exception as e:
        print(f"LỖI khi lưu file Parquet: {e}")
        return

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"\n--- HOÀN THÀNH TRÍCH XUẤT ---")
    print(f"Đã lưu thành công vào: {output_path}")
    print(f"Tổng thời gian: {elapsed_time:.2f} giây.")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Sử dụng: python run_extraction.py <đường_dẫn_pcap_đầu_vào> <đường_dẫn_parquet_đầu_ra>")
        sys.exit(1)
        
    pcap_to_raw_flows(sys.argv[1], sys.argv[2])