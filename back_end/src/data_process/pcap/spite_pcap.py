import heapq
from concurrent.futures import ProcessPoolExecutor
from typing import Dict, List, Tuple
import os

import pandas as pd
from tqdm import tqdm
from scapy.utils import PcapReader

from ...features import (
    SessionKey,
    calculate_session_hash,
    extract_session_id,
    SessionPackets,
    FlowKey,
    extract_flow_id,
    calculate_flow_hash,
    analysis_flow_id,
)

from ..utils import get_file_list


class FilePath:
    """
    静态类:
    存储文件路径的某些文件路径
    """

    @staticmethod
    def get_file_partern(pcap_path: str) -> List[str]:
        """
        输入 pcap 文件路径, 返回对应的 pcap 的标签文件路径

        :param pcap_path: pcap 文件路径
        :type pcap_path: str
        :return: 标签文件路径
        :rtype: str
        """
        # 从路径中提取 pcap 文件名称
        pcap_name = os.path.basename(pcap_path)
        label_dir_path = r'D:\code_repository\mtd\data\ml_label'

        label_pcap_dict: dict[str, list[str]] = {
            "Friday-WorkingHours.pcap": [
                os.path.join(label_dir_path,
                             "Friday-WorkingHours-Afternoon-DDos.csv"),
                os.path.join(label_dir_path,
                             "Friday-WorkingHours-Afternoon-PortScan.csv"),
                os.path.join(label_dir_path, "Friday-WorkingHours-Morning.csv")
            ],
            "Monday-WorkingHours.pcap": [os.path.join(label_dir_path, "Monday-WorkingHours.csv")],
            "Thursday-WorkingHours.pcap": [
                os.path.join(
                    label_dir_path,
                    "Thursday-WorkingHours-Afternoon-Infilteration.csv"),
                os.path.join(label_dir_path,
                             "Thursday-WorkingHours-Morning-WebAttacks.csv")
            ],
            "Tuesday-WorkingHours.pcap": [os.path.join(label_dir_path, "Tuesday-WorkingHours.csv")],
            "Wednesday-WorkingHours.pcap": [os.path.join(label_dir_path, "Wednesday-workingHours.csv")]
        }
        return label_pcap_dict.get(pcap_name, [])


def read_label_file(pcap_path: str) -> Dict[int, FlowKey]:
    """
    读取标签文件, 返回标签字典

    :param pcap_path: pcap 文件路径
    :type pcap_path: str
    :return: 标签字典
    :rtype: Dict[int, FlowKey]
    """
    print()
    label_file_paths = FilePath.get_file_partern(pcap_path)
    flow_dict: Dict[int, FlowKey] = {}
    label_distirbution: Dict[str, int] = {}

    for label_file_path in label_file_paths:
        try:
            # 获取文件总行数
            total_lines = sum(
                1 for _ in open(
                    label_file_path,
                    'r',
                    encoding='utf-8'))
            # 分块读取文件
            chunksize = 10000
            with tqdm(total=total_lines, desc=f"Reading {label_file_path}", unit="lines") as pbar:
                for chunk in pd.read_csv(label_file_path, chunksize=chunksize):
                    for _, row in chunk.iterrows():
                        flow_id = row.iloc[0]
                        flow_hash = calculate_flow_hash(
                            *analysis_flow_id(flow_id))
                        label = row.iloc[-1]
                        flow_dict[flow_hash] = FlowKey(
                            *analysis_flow_id(flow_id), label=label)
                        if label not in label_distirbution:
                            label_distirbution[label] = 1
                        else:
                            label_distirbution[label] += 1
                    pbar.update(len(chunk))
            print()
     
            for label, count in label_distirbution.items():
                print()
        except FileNotFoundError:
            print()
        except Exception as e:
            print()

    return flow_dict


def spilt_single_labelled_pcap(file_path: str, dst_path: str):
    """
    处理单个 pcap 文件的函数
    按照 session 进行划分
    第一列: flow_id
    第二列: 标签

    :param file_path: pcap 文件路径
    :type file_path: str
    :param dst_path: 目标目录路径
    :type dst_path: str
    :return: None
    """

    timeout = 0.5
    timeout_heap: List[Tuple[int, int]] = []
    label_dict: Dict[int, FlowKey] = read_label_file(file_path)
    if label_dict == {}:
        print()
        return

    session_dict: Dict[int, SessionPackets] = {}
    unlabelled_packet_count = 0
    error_packet_count = 0

    try:
        file_size = os.path.getsize(file_path)
        print('Start to read pcap file...')
        with tqdm(total=file_size, unit='B', unit_scale=True, desc=f"Processing {file_path}") as pbar:
            with PcapReader(file_path) as pcap_reader:
                for packet in pcap_reader:
                    cur_time = packet.time
                    session_id = extract_session_id(packet)
                    flow_id = extract_flow_id(packet)

                    # 异常的数据包, 不进行计数
                    if session_id is None or flow_id is None:
                        error_packet_count += 1
                    else:
                        # 计算 flow hash
                        session_hash = calculate_session_hash(*session_id)
                        flow_hash = calculate_flow_hash(*flow_id)
                        if flow_hash not in label_dict:
                            unlabelled_packet_count += 1
                        else:
                            label = label_dict[flow_hash].label
                            session_key = SessionKey(*session_id, label)

                            if session_hash not in session_dict:
                                # 第一次读入
                                session_dict[session_hash] = SessionPackets(
                                    first_packet=packet, label=label)
                                heapq.heappush(
                                    timeout_heap, (cur_time + timeout, session_hash))
                            else:
                                # 正常读入
                                cur_session = session_dict[session_key.hash]
                                cur_session.add_packet(
                                    packet=packet, label=label)
                                heapq.heappush(
                                    timeout_heap, (cur_time + timeout, session_hash))

                            # 对其他协议类型重拳出击
                            while timeout_heap and timeout_heap[0][0] < cur_time:
                                _, expired_flow_hash = heapq.heappop(
                                    timeout_heap)
                                session_dict[expired_flow_hash].write_file(
                                    dst_path)

                        pbar.update(len(packet))
            print()
            for session_hash in session_dict:
                session_dict[session_hash].write_file(dst_path)
        print(
            
        )
    except FileNotFoundError:
        print()
    except Exception as e:
        print()


def split_labelled_pcap(
    src_path: str, dst_path: str
) -> None:
    """
    将 pcap 文件按照 session 进行分割, 并将 session 按照 label 进行分类

    :param src_path: 源 pcap 文件路径
    :type src_path: str
    :param dst_path: 目标目录路径
    :type dst_path: str
    :return: None
    """
    file_list = get_file_list(src_path)

    with ProcessPoolExecutor(max_workers=len(file_list)) as executor:
        for file_path in file_list:
            executor.submit(spilt_single_labelled_pcap, file_path, dst_path)
