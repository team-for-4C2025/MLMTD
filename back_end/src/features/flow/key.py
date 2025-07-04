from enum import IntEnum, auto
from typing import Optional, Tuple
import ipaddress

import scapy
from scapy.packet import Packet as ScapyPacket
from scapy.layers.inet import IP, TCP, UDP, ICMP


class Protocol(IntEnum):
    """
    协议类型
    """
    TCP = 6
    UDP = 17
    ICMP = 1


class FlowKey:
    """
    流的标识符
    """

    class Idx(IntEnum):
        DESTINATION_IP = 0
        SOURCE_IP = auto()
        DESTINATION_PORT = auto()
        SOURCE_PROT = auto()
        PROTOCOL = auto()

    destination_ip: str
    source_ip: str
    destination_port: int
    source_port: int
    protocol: int
    hash: int
    label: str = ""

    def __init__(
        self, distination_ip: str, source_ip: str, destination_port: int, source_port: int, protocol: int,
        label: str = ""
    ):
        """
        构造函数

        :param distination_ip: 目标 IP 地址 (Ipv4)
        :type distination_ip: str
        :param source_ip: 源 IP 地址 (Ipv4)
        :type source_ip: str
        :param destination_port: 目标端口
        :type destination_port: int
        :param source_port: 源端口
        :type source_port: int
        :param protocol: 协议
        :param label: 标签
        :type label: str
        """
        self.destination_ip = distination_ip
        self.source_ip = source_ip
        self.destination_port = destination_port
        self.source_port = source_port
        self.protocol = protocol
        self.hash = calculate_flow_hash(
            self.destination_ip, self.source_ip, self.destination_port, self.source_port, self.protocol
        )
        self.label = label

    def __str__(self):
        """
        实际的数据集中的标识

        :return: str
        :rtype: str
        """
        return generate_flow_id(
            self.destination_ip,
            self.source_ip,
            self.destination_port,
            self.source_port,
            self.protocol,
        )

    def flow_id(self) -> str:
        """
        返回FlowID

        :return: flow_id
        :rtype: str
        """
        return generate_flow_id(
            self.destination_ip,
            self.source_ip,
            self.destination_port,
            self.source_port,
            self.protocol,
        )

    def __hash__(self):
        """
        返回哈希值

        :return: int
        :rtype: int
        """
        return self.hash

    def __eq__(self, other):
        """
        判断两个对象是否相等

        :param other: 另一个对象
        :type other: FlowKey
        :return: bool
        :rtype: bool
        """
        if isinstance(other, FlowKey):
            return self.__hash__() == other.__hash__()
        else:
            return False


def generate_flow_key(packet: ScapyPacket, label: str = "") -> FlowKey:
    """
    从Packet中生成FlowKey

    :param packet: Packet
    :type packet: ScapyPacket
    :param label: 标签
    :type label: str
    :return: FlowKey
    :rtype: FlowKey
    """
    (
        distination_ip,
        source_ip,
        destination_port,
        source_port,
        protocol,
    ) = extract_flow_id(packet)
    return FlowKey(distination_ip, source_ip, destination_port,
                   source_port, protocol, label)


def extract_flow_id(
        packet: scapy.packet.Packet) -> Optional[Tuple[str, str, int, int, int]]:
    """
    从Packet中提取五元组信息（FlowKey）

    :param packet: Packet
    :type packet: scapy.packet.Packet
    :return: FlowKey 或 None（如果无法提取）
    :rtype: Optional[Tuple[str, str, int, int, int]]
    """
    # 初始化五元组信息
    source_port = 0
    destination_port = 0

    # 处理 IPv4 数据包
    if IP in packet:
        ip_layer = packet[IP]
        source_ip = ip_layer.src
        destination_ip = ip_layer.dst
        protocol_num = ip_layer.proto

        if protocol_num == Protocol.TCP.value:
            if TCP in packet:
                tcp_layer = packet[TCP]
                source_port = tcp_layer.sport
                destination_port = tcp_layer.dport
        elif protocol_num == Protocol.UDP.value:
            if UDP in packet:
                udp_layer = packet[UDP]
                source_port = udp_layer.sport
                destination_port = udp_layer.dport
        elif protocol_num == Protocol.ICMP.value:
            if ICMP in packet:
                source_port = 0
                destination_port = 0
        else:
            return None
    else:
        return None

    # 返回五元组信息
    return source_ip, destination_ip, source_port, destination_port, protocol_num


def ip4_to_int(ip_str: str) -> int:
    """
    将IPv4地址转换为整数

    :param ip_str: IPv4地址
    :type ip_str: str
    :return: 整数
    :rtype: int
    """
    return int(ipaddress.IPv4Address(ip_str))


def calculate_flow_hash(
    destination_ip: str, source_ip: str, destination_port: int, source_port: int, protocol: int
):
    """
    计算FlowKey的哈希值
    其中端口占有 16 位, 协议占有 5 位, 目的 IP 占有 32 位

    :param destination_ip: 目标IP地址
    :type destination_ip: str
    :param source_ip: 源IP地址
    :type source_ip: int
    :param destination_port: 目标端口
    :type destination_port: int
    :param source_port: 源端口
    :type source_port: int
    :param protocol: 协议
    :type protocol: int
    :return: int
    :rtype: int
    """
    return ((ip4_to_int(destination_ip) ^ ip4_to_int(source_ip) << 21) +
            (destination_port ^ source_port << 5) + protocol ^ 0x1F)


def generate_flow_id(
    destination_ip: str,
    source_ip: str,
    destination_port: int,
    source_port: int,
    protocol: int,
):
    """
    生成 FlowID

    :param destination_ip: 目标IP地址
    :type destination_ip: str
    :param source_ip: 源IP地址
    :type source_ip: str
    :param destination_port: 目标端口
    :type destination_port: int
    :param source_port: 源端口
    :type source_port: int
    :param protocol: 协议
    :type protocol: int
    :return: 流的标识符
    :rtype: FlowID
    """
    return f"{source_ip}-{destination_ip}-{source_port}-{destination_port}-{protocol}"


def analysis_flow_id(flow_id: str) -> Tuple[str, str, int, int, int]:
    """
    解析 FlowID

    :param flow_id: 流的标识符
    :type flow_id: str
    :return: 目标IP地址, 源IP地址, 目标端口, 源端口, 协议
    :rtype: Tuple[str, str, int, int, int]
    """
    parts = flow_id.split('-')
    source_ip = parts[0]
    destination_ip = parts[1]
    source_port = int(parts[2])
    destination_port = int(parts[3])
    protocol = int(parts[4])
    return destination_ip, source_ip, destination_port, source_port, protocol
