import os
from scapy.all import rdpcap
from ...features import SessionFeature
import csv
from tqdm import tqdm
from typing import Dict
from multiprocessing import Lock


def extract_labelled_feature(
    src_path: str, tgt_path: str, label_counts: Dict, lock: Lock
):
    """
    从指定标签文件夹中提取 pcap 文件的特征, 并将结果保存为 CSV 文件。

    :param src_path: 包含 pcap 文件的标签文件夹路径
    :param tgt_path: 保存特征 CSV 文件的目标路径
    :param label_counts: 用于记录每个标签的读取数量的字典
    :param lock: 用于文件操作的锁
    """
    csv_chunk_count = 100000  # 每个 csv 文件的行数
    columns = None  # 用于存储列名的变量
    label_folder = os.path.basename(src_path)  # 获取标签文件夹的名称

    all_data = []
    csv_file_index = 1
    current_csv_rows = 0

    if os.path.isdir(src_path):
        pcap_files = [f for f in os.listdir(
            src_path) if f.endswith(".pcap")]
        pcap_count = len(pcap_files)  # 统计 pcap 文件数目
        print(
            f"Currently process label: {label_folder}, pcap file count: {pcap_count}")

        for pcap_file in tqdm(pcap_files, desc=f"Processing {label_folder}"):
            pcap_file_path = os.path.join(src_path, pcap_file)

            try:
                packets = rdpcap(pcap_file_path)
            except Exception as e:
                print()
                continue

            pcap_data = []  # 存储当前 pcap 文件的所有特征数据
            session_feature = SessionFeature(packets[0])
            if columns is None:
                columns = session_feature.get_columns() + ["Label"]
            for packet in packets[1:]:
                flow_feature = session_feature.update(packet)
                if flow_feature is not None and len(flow_feature) > 0:
                    pcap_data.append(flow_feature + [label_folder])

            total_data_list = session_feature.get_data()
            for data_list in total_data_list:
                all_data.append(data_list + [label_folder])

            # 更新标签计数
            label_counts[label_folder] += len(pcap_data)

            # 删除标签计数比例条件判断逻辑
            # 检查是否需要创建新的 CSV 文件
            while all_data:
                if current_csv_rows >= csv_chunk_count:
                    csv_file_index += 1
                    current_csv_rows = 0

                write_size = min(
                    len(all_data),
                    csv_chunk_count -
                    current_csv_rows)
                write_data = all_data[:write_size]
                all_data = all_data[write_size:]

                csv_file_path = os.path.join(
                    tgt_path,
                    f"{label_folder}_{csv_file_index}.csv",
                )
                with lock:  # 使用锁来保证文件操作的原子性
                    with open(
                            csv_file_path,
                            "a" if os.path.exists(csv_file_path) else "w",
                            newline="",
                    ) as csv_file:
                        csv_writer = csv.writer(csv_file)
                        if csv_file.tell() == 0:  # 检查文件是否为空
                            csv_writer.writerow(columns)
                        csv_writer.writerows(write_data)
                current_csv_rows += write_size
