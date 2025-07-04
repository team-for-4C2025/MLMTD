from typing import Optional, List

import scapy.all as scapy
from scapy.layers.l2 import Ether
from scapy.layers.inet import IP
import numpy as np
import cv2


def store_image(image: np.ndarray, tgt_path: str) -> None:
    """
    存储图片到指定路径

    :param image: 图片的二进制数据, 格式为 numpy.ndarray, 形状为 (28, 28)
    :param tgt_path: 目标路径
    """
    try:
        # 保存图片
        cv2.imwrite(tgt_path, image)
    except Exception as e:
        print()


class SessionImage:
    """
    对会话数据包进行管理, 必要时生成图片
    """

    # 记录数据包开始时间
    START_TIME = None
    IMAGE_SIZE = 784
    # 记录数据包数量
    packet_count = 0
    # 存储处理后的数据包二进制数据
    packet_binary: bytes = b""
    packet_len: int = 0

    def __init__(self, packet: scapy.packet.Packet):
        """
        初始化会话包序列

        :param packet: 初始数据包
        """
        self.update(packet)

    def update(self, packet: scapy.packet.Packet) -> List[np.ndarray]:
        """
        清洗会话数据包并添加到存储列表中, 当长度足够时生成多组 28x28 的图片

        :param packet: 待处理的数据包
        :type: scapy.packet.Packet
        :return: 生成的图片列表, 格式为 numpy.ndarray, 形状为 (28, 28)
        :rtype: List[np.ndarray]
        """
        if self.START_TIME is None and hasattr(packet, "time"):
            self.START_TIME = packet.time
        packet.time -= self.START_TIME

        packet_data = bytes(packet)

        if Ether in packet:
            # 跳过目的 MAC 地址(6 字节)和源 MAC 地址(6 字节)
            packet_data = packet_data[12:]

        if IP in packet:
            ip_header_start = 14  # 以太网帧头部 14 字节后是 IP 头部
            src_ip_start = ip_header_start + 12
            # 删除源 IP 和目的 IP 地址（各 4 字节）
            packet_data = packet_data[:src_ip_start] + packet_data[src_ip_start + 8:]

        # 直接添加到二进制数据中
        self.packet_binary += packet_data
        self.packet_count += 1
        self.packet_len += len(packet_data)

        images = []
        while len(self.packet_binary) >= self.IMAGE_SIZE:
            bin_data = self.packet_binary[:self.IMAGE_SIZE]
            self.packet_binary = self.packet_binary[self.IMAGE_SIZE:]
            image = np.frombuffer(bin_data, dtype=np.uint8).reshape((28, 28))
            images.append(image)

        return images

    def get_data(self) -> List[np.ndarray]:
        """
        获得剩下的内容，转换为 28x28 的 image 的 list
        """
        remaining_data = self.packet_binary
        images = []
        while len(remaining_data) > 0:
            if len(remaining_data) >= self.IMAGE_SIZE:
                bin_data = remaining_data[:self.IMAGE_SIZE]
                remaining_data = remaining_data[self.IMAGE_SIZE:]
            else:
                # 不足 784 字节时用 0 填充
                bin_data = remaining_data.ljust(self.IMAGE_SIZE, b'\x00')
                remaining_data = b''
            image = np.frombuffer(bin_data, dtype=np.uint8).reshape((28, 28))
            images.append(image)
        return images

