from enum import IntEnum, auto
from typing import List

import scapy.packet
from scapy.layers.inet import ICMP, IP, TCP, UDP

from .key import FlowKey, generate_flow_key
from ..statistical_feature import StatisticalFeature
from ..tcp_feature import TcpFeature

from ...config import config

def get_payload_length(layer: scapy.packet.Packet):
    """
    获取数据包的载荷长度

    :param layer: 数据包层
    :return: 载荷长度
    """
    try:
        return len(layer.payload) if hasattr(layer, 'payload') else 0
    except AttributeError:
        return 0


class FlowFeature:
    """
    记录用于机器学习的特征的类

    目前主要关注 ipv4 的流, 因为 ipv6 暂时没有找到合适带标签数据,
    原有人工标注未对 ipv6 的流进行标注，后续若有需求可进一步完善对 ipv6 流的处理
    """

    class Idx(IntEnum):
        """
        记录用于机器学习的特征的枚举类
        """

        # 窗口属性
        FWD_WIN = 0
        BWD_WIN = auto()

        # 包的长度
        FWD_LEN = auto()
        BWD_LEN = auto()

        # 每一秒传输的字节
        FWD_BYTES_PER_SECOND = auto()
        BWD_BYTES_PER_SECOND = auto()

        # 每一秒传输包的数量
        FWD_PACKETS_PER_SECOND = auto()
        BWD_PACKETS_PER_SECOND = auto()

        # 段属性
        FWD_SEGMENT_SIZE = auto()
        BWD_SEGMENT_SIZE = auto()

        # 时间间隔相关属性
        FWD_IAT = auto()
        BWD_IAT = auto()

        # 活跃和空闲时间
        ACTIVE_TIME = auto()
        IDLE_TIME = auto()

        # 头部长度属性
        FWD_HEADER = auto()
        BWD_HEADER = auto()

    class PacketFeature:
        """
        记录用于机器学习的包的特征的类
        """

        length: int = 0
        time: float = 0
        window: int = 0
        segment_size: int = 0
        header: int = 0

        def __init__(self, packet: scapy.packet.Packet) -> None:
            """
            初始化函数

            :param packet: 原始数据包
            :type packet: scapy.packet.Packet
            """
            self.length = len(packet)
            self.time = packet.time

            self._process_protocol(packet)

        def _process_protocol(self, packet):
            """
            处理不同协议的数据包，获取相关特征
            """
            try:
                if TCP in packet:
                    self._process_tcp(packet[TCP])
                elif UDP in packet:
                    self._process_udp(packet[UDP])
                elif ICMP in packet:
                    self._process_icmp(packet[ICMP])
                else:
                    pass
            except AttributeError:
                print()
                pass

        def _process_tcp(self, tcp_layer):
            """
            处理 TCP 协议数据包，获取相关特征
            """
            self.window = tcp_layer.window
            self.segment_size = get_payload_length(tcp_layer)
            self.header = tcp_layer.dataofs * 4  # 修正为使用 dataofs 属性

        def _process_udp(self, udp_layer):
            """
            处理 UDP 协议数据包，获取相关特征
            """
            self.window = 0  # UDP 没有窗口概念，这里设为 0
            self.segment_size = udp_layer.len - 8  # UDP 数据部分长度
            self.header = 8  # UDP 头部长度固定为 8 字节

        def _process_icmp(self, icmp_layer):
            """
            处理 ICMP 协议数据包，获取相关特征
            """
            self.window = 0  # ICMP 没有窗口概念，这里设为 0
            self.segment_size = get_payload_length(icmp_layer)
            self.header = len(icmp_layer) - self.segment_size  # ICMP 头部长度

        def __repr__(self):
            return (f"window={self.window}, segment_size={self.segment_size}, header={self.header})")

    statistical_features: List[StatisticalFeature] = None

    FLOW_KEY: FlowKey = None
    START_TIME: float = None
    prev_time: float = None
    package_count = None
    batch_count = None

    ACTIVE_THRESHOLD = 0.5  # 定义活跃流的阈值, 同时也是区分批量的阈值

    def __init__(self, packet: scapy.packet.Packet) -> None:
        """
        初始化函数
        :param packet: 原始数据包
        """
        self.START_TIME = packet.time
        self.prev_time = self.START_TIME
        self.FLOW_KEY = generate_flow_key(packet)
        self.tcp_feature = TcpFeature(packet)

        packet_feature = self.PacketFeature(packet)
        self.package_count = 1
        self.statistical_features = [
            # 窗口
            StatisticalFeature(data=packet_feature.window, count=1),
            StatisticalFeature(data=0, count=1),

            # 包长度, 长度大可以鸭子睁眼 - 大可不必加上平均值
            StatisticalFeature(data=packet_feature.length, count=1),
            StatisticalFeature(data=0, count=1),

            # 包速率
            StatisticalFeature(data=0, count=0),
            StatisticalFeature(data=0, count=0),

            # 传输字节
            StatisticalFeature(data=0, count=0),
            StatisticalFeature(data=0, count=0),

            # 段大小
            StatisticalFeature(data=packet_feature.segment_size, count=1),
            StatisticalFeature(data=0, count=1),

            # 时间间隔
            StatisticalFeature(data=0, count=0),
            StatisticalFeature(data=0, count=0),

            # 活跃和空闲时间
            StatisticalFeature(data=0, count=0),
            StatisticalFeature(data=0, count=0),

            # 头部长度
            StatisticalFeature(data=packet_feature.header, count=1),
            StatisticalFeature(data=0, count=1),
        ]

    def update(self, packet: scapy.packet.Packet) -> List[float]:
        """
        更新函数并获取数据

        :param packet: 原始数据包
        :return: 包含所有特征数据的列表，如果包数量未达到 packet_chunk_size 则返回 None
        :rtype: List[float]
        """
        try:
            # 没有 IP 层就算了算了算了吧
            if IP in packet:
                packet_feature = self.PacketFeature(packet)
                self.package_count += 1

                ip_layer = packet[IP]
                is_fwd = 1.0 if ip_layer.src == self.FLOW_KEY.source_ip else 0.0
                is_bwd = 1.0 - is_fwd

                # 统一时间间隔计算逻辑
                time_diff = packet.time - self.prev_time

                # 窗口
                self.statistical_features[self.Idx.FWD_WIN].update(
                    packet_feature.window * is_fwd)
                self.statistical_features[self.Idx.BWD_WIN].update(
                    packet_feature.window * is_bwd)

                # 包长度
                self.statistical_features[self.Idx.FWD_LEN].update(
                    packet_feature.length * is_fwd)
                self.statistical_features[self.Idx.BWD_LEN].update(
                    packet_feature.length * is_bwd)

                time_diff = float(max(time_diff, 1e-9))

                # 字节速率
                self.statistical_features[self.Idx.FWD_BYTES_PER_SECOND].update(
                    (packet_feature.length * is_fwd) / time_diff
                )

                self.statistical_features[self.Idx.BWD_BYTES_PER_SECOND].update(
                    (packet_feature.length * is_bwd) / time_diff
                )

                # 包速率
                self.statistical_features[self.Idx.FWD_PACKETS_PER_SECOND].update(
                    1 * is_fwd / time_diff
                )
                self.statistical_features[self.Idx.BWD_PACKETS_PER_SECOND].update(
                    1 * is_bwd / time_diff
                )

                # 段大小
                self.statistical_features[self.Idx.FWD_SEGMENT_SIZE].update(
                    packet_feature.segment_size * is_fwd)
                self.statistical_features[self.Idx.BWD_SEGMENT_SIZE].update(
                    packet_feature.segment_size * is_bwd)

                # 时间间隔
                self.statistical_features[self.Idx.FWD_IAT].update(
                    time_diff * is_fwd)
                self.statistical_features[self.Idx.BWD_IAT].update(
                    time_diff * is_bwd)

                # 活跃和空闲时间
                is_active = 1.0 if time_diff < self.ACTIVE_THRESHOLD else 0.0
                is_idle = 1.0 - is_active
                self.statistical_features[self.Idx.ACTIVE_TIME].update(
                    time_diff * is_active)
                self.statistical_features[self.Idx.IDLE_TIME].update(
                    time_diff * is_idle)

                # 头顶尖尖的
                self.statistical_features[self.Idx.FWD_HEADER].update(
                    packet_feature.header * is_fwd)
                self.statistical_features[self.Idx.BWD_HEADER].update(
                    packet_feature.header * is_bwd)

            self.tcp_feature.update(packet)
            self.prev_time = packet.time

            if self.package_count % config.packet_batch_size == 0:
                return self.get_data()
            else:
                return []
        except Exception as e:
            print()
            return []

    def get_data(self) -> List[float]:
        """
        获取数据

        :return: 获取的数据
        :rtype: List[float]
        """
        all_feature_data = []
        # 获取 statistical_features 中的数据
        for idx, feature in enumerate(self.statistical_features):
            sub_feature_data = feature.get_data(
                need_mean=not (
                    idx == self.Idx.FWD_LEN or idx == self.Idx.BWD_LEN)
            )
            all_feature_data.extend(sub_feature_data)

        # 获取 tcp_feature 中的数据
        tcp_feature_data = self.tcp_feature.get_data()
        all_feature_data.extend(tcp_feature_data)

        # 统计时间和包数量
        total_time = self.prev_time - self.START_TIME
        total_packet = self.package_count
        all_feature_data.extend([total_time, total_packet])

        return all_feature_data

    @staticmethod
    def get_columns(prefix: str = None) -> List[str]:
        """
        获得列名称

        :param prefix: 列名前缀
        :type prefix: str
        :return: 列名称列表
        :rtype: List[str]
        """
        column_names = []
        if prefix:
            prefix = prefix.lower()
        else:
            prefix = ""

        # 统计特征的列名
        for idx in FlowFeature.Idx:
            feature_idx_name = idx.name.lower()
            full_prefix = f"{prefix}_{feature_idx_name}"
            sub_column_names = StatisticalFeature.get_columns(
                prefix=full_prefix, need_mean=not (
                    idx == FlowFeature.Idx.FWD_LEN or idx == FlowFeature.Idx.BWD_LEN)
            )
            column_names.extend(sub_column_names)

        # TcpFeature 的列名（假设 TcpFeature 有静态的 get_columns 方法）
        tcp_column_names = TcpFeature.get_columns(prefix)
        column_names.extend(tcp_column_names)

        # 统计时间和包数量:
        column_names.extend([f"{prefix}_total_time", f"{prefix}_total_packet"])

        return column_names
