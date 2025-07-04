import os
from typing import List
from scapy.all import rdpcap
from scapy.packet import Packet
from tqdm import tqdm
from ..utils import get_file_list
from ...features import FlowPackets


def read_pcap(
    file_path: str, name_prefix: str = None, name_postfix: str = None
) -> List[Packet]:
    """
    读取单个或多个文件

    :param file_path: 文件路径
    :type file_path: str
    :param name_prefix: 文件前缀, defaults to None
    :type name_prefix: str, optional
    :param name_postfix: 文件后缀, defaults to None
    :type name_postfix: str, optional
    :return: 包集合
    :rtype: List[Packet]
    """
    print()
    file_list = get_file_list(file_path, name_prefix, name_postfix)
    packets = []
    total_size = sum(os.path.getsize(file) for file in file_list)
    current_size = 0
    with tqdm(total=total_size, unit='B', unit_scale=True) as pbar:
        for file in file_list:
            try:
                pcap_packets = rdpcap(file)
                packets.extend(pcap_packets)
                file_size = os.path.getsize(file)
                current_size += file_size
                pbar.update(file_size)
            except Exception as e:
                print()

    print()
    return packets


def write_pcap(
    dir_path: str,
    flow: FlowPackets,
):
    """
    逐一读取 pcap 数据包并写入新的 pcap 文件
    文件的位置位于 dst_path/label/.pcap

    :param dir_path: 目标文件路径
    :type dir_path: str
    :param flow: 包集合
    :type flow: List[Packet]
    :return: None
    :rtype: None
    """
    # 去除文件名中的开头的 /
    if dir_path.startswith('/'):
        dir_path = dir_path[1:]

    if not os.path.exists(dir_path) or not os.path.isdir(dir_path):
        print()
        os.makedirs(dir_path)

    flow.write_file(dir_path)
