from enum import IntEnum, auto
from typing import List

import scapy.packet


class TcpFeature:
    """
    这是用于提取 TCP 层的特征的类:
    """

    class Idx(IntEnum):
        """
        这是 TCP 层特征的索引:
        """

        ## 这是一些基本的特征:
        DURATION = 0  # 流之间持续的的时间
        PROTOCOL = auto()  # 协议类型: TCP, UDP, ICMP

        ## 一些标志的特征:
        WRONG_FRAGMENT = auto()  # 错误的分段, 使用 IP 报头和中 MF 和 FRAG 进行判断
        URG_COUNT = auto()  # 加急包的个数: URG 标志位为 1 的包的个数
        PSH_COUNT = auto()  # 推送包的个数: PSH 标志位为 1 的包的个数
        RST_COUNT = auto()  # 重置连接的个数: RST 标志位为 1 的包的个数
        SYN_COUNT = auto()  # 建立连接的个数: SYN 标志位为 1 的包的个数
        FIN_COUNT = auto()  # 结束连接的个数: FIN 标志位为 1 的包的个数
        ACK_COUNT = auto()  # 确认包的个数: ACK 标志位为 1 的包的个数
        ECE_COUNT = auto()  # 显著拥塞的个数: ECE 标志位为 1 的包的个数
        CWR_COUNT = auto()  # 连接重置的个数: CWR 标志位为 1 的包的个数
        NS_COUNT = auto()  # 特殊包的个数:

    tcp_features: List[float] = None
    start_time: float = None

    def __init__(self, packet: scapy.packet.Packet) -> None:
        """
        初始化 TCP 特征提取器:

        :param packet: 要提取特征的 TCP 报文
        :type packet: scapy.packet.Packet
        """

        self.tcp_features = [0] * len(self.Idx.__members__)
        self.start_time = packet.time
        self.tcp_features[self.Idx.PROTOCOL] = float(packet.proto)

    def update(self, packet: scapy.packet.Packet) -> None:
        """
        更新 TCP 特征:

        :param packet: 要提取特征的 TCP 报文
        :type packet: scapy.packet.Packet
        """
        # 基本特征
        self.tcp_features[self.Idx.DURATION] = packet.time - self.start_time

        # 标志位特征
        if 'TCP' in packet:
            tcp_flags = packet['TCP'].flags
            self.tcp_features[self.Idx.URG_COUNT] += int (tcp_flags & 0x20) >> 5
            self.tcp_features[self.Idx.PSH_COUNT] += int (tcp_flags & 0x08) >> 3
            self.tcp_features[self.Idx.RST_COUNT] += int (tcp_flags & 0x04) >> 2
            self.tcp_features[self.Idx.SYN_COUNT] += int (tcp_flags & 0x02) >> 1
            self.tcp_features[self.Idx.FIN_COUNT] += int (tcp_flags & 0x01)
            self.tcp_features[self.Idx.ACK_COUNT] += int (tcp_flags & 0x10) >> 4
            self.tcp_features[self.Idx.ECE_COUNT] += int (tcp_flags & 0x40) >> 6  # 修正 ECE 标志位计算
            self.tcp_features[self.Idx.CWR_COUNT] += int (tcp_flags & 0x80) >> 7  # 修正 CWR 标志位计算
            self.tcp_features[self.Idx.NS_COUNT] += int (tcp_flags & 0x80) >> 7

            # 补充 WRONG_FRAGMENT 特征计算
            if 'IP' in packet:
                ip_layer = packet['IP']
                mf = ip_layer.flags & 0x02  # MF 标志位
                frag = ip_layer.frag  # 片偏移
                # 简单示例判断逻辑，实际情况可能更复杂
                if (mf == 1 and frag == 0) or (mf == 0 and frag > 0):
                    self.tcp_features[self.Idx.WRONG_FRAGMENT] += 1

    @staticmethod
    def get_columns(prefix: str = None) -> List[str]:
        """
        获得列名称

        :param prefix:
        :type prefix: str
        :return: 列名称列表
        :rtype: List[str]
        """
        if prefix is not None:
            return [f"{prefix}_{name.lower()}" for name in TcpFeature.Idx.__members__.keys()]
        else:
            return [name.lower() for name in TcpFeature.Idx.__members__.keys()]

    def get_data(self) -> List[float]:
        """
        获取特征数据

        :return: 特征数据列表
        :rtype: List[float]
        """
        return self.tcp_features