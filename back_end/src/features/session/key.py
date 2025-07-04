from enum import IntEnum, auto
from typing import Optional, Tuple
import scapy
from scapy.packet import Packet as ScapyPacket
from scapy.layers.inet import IP


class Protocol(IntEnum):
    """
    协议类型
    """
    TCP = 6
    UDP = 17
    ICMP = 1


class SessionKey:
    """
    流的标识符
    """
    destination_ip: str
    source_ip: str

    class Idx(IntEnum):
        """
        流的标识符的索引
        """
        DESTINATION_IP = 0
        SOURCE_IP = auto()

        def __str__(self):
            """
            实际的数据集中的标识

            :return: str
            :rtype: str
            """
            return "{DESTINATION_IP}-{SOURCE_IP}"

    def __init__(self, destination_ip: str, source_ip: str, label: str = ""):
        """
        构造函数

        :param destination_ip: 目标 IP 地址
        :type destination_ip: str
        :param source_ip: 源 IP 地址
        :type source_ip: str
        :param label: 标签
        :type label: str
        """
        self.destination_ip = destination_ip
        self.source_ip = source_ip
        self.hash = calculate_session_hash(
            self.destination_ip, self.source_ip
        )
        self.label = label

    def __str__(self):
        """
        实际的数据集中的标识

        :return: str
        :rtype: str
        """
        return generate_session_id(
            self.destination_ip,
            self.source_ip,
        )

    def session_id(self) -> str:
        """
        返回FlowID

        :return: flow_id
        :rtype: str
        """
        return generate_session_id(
            self.destination_ip,
            self.source_ip,
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
        :type other: SessionKey
        :return: bool
        :rtype: bool
        """
        if isinstance(other, SessionKey):
            return self.__hash__() == other.__hash__()
        else:
            return False


def generate_session_key(packet: ScapyPacket, label: str = "") -> SessionKey:
    """
    从Packet中生成FlowKey

    :param packet: Packet
    :type packet: ScapyPacket
    :param label: 标签
    :type label: str
    :return: FlowKey
    :rtype: SessionKey
    """
    (
        destination_ip,
        source_ip,
    ) = extract_session_id(packet)
    return SessionKey(destination_ip, source_ip, label)


def extract_session_id(packet: scapy.packet.Packet) -> Optional[Tuple[str, str]]:
    """
    从Packet中提取五元组信息（FlowKey）

    :param packet: Packet
    :type packet: scapy.packet.Packet
    :return: FlowKey 或 None（如果无法提取）
    :rtype: Optional[Tuple[str, str]]
    """

    # 处理 IP 数据包
    if IP in packet:
        ip_layer = packet[IP]
        source_ip = ip_layer.src
        destination_ip = ip_layer.dst

        return source_ip, destination_ip
    else:
        return None


def ip_to_int(ip_str: str) -> int:
    """
    将 IP 地址转换为整数

    :param ip_str: IP 地址
    :type ip_str: str
    :return: 整数
    :rtype: int
    """
    import ipaddress
    # 检查 ipv4
    if ':' in ip_str:
        return 0

    return int(ipaddress.ip_address(ip_str))


def calculate_session_hash(
    destination_ip: str, source_ip: str
):
    """
    计算FlowKey的哈希值

    :param destination_ip: 目标 IP 地址
    :type destination_ip: str
    :param source_ip: 源 IP 地址
    :type source_ip: str
    :return: int
    :rtype: int
    """
    return ip_to_int(destination_ip) ^ ip_to_int(source_ip)


def generate_session_id(
    destination_ip: str,
    source_ip: str,
):
    """
    生成 FlowID

    :param destination_ip: 目标 IP 地址
    :type destination_ip: str
    :param source_ip: 源 IP 地址
    :type source_ip: str
    :return: 流的标识符
    :rtype: str
    """
    return f"{source_ip}-{destination_ip}"


def analysis_session_id(flow_id: str) -> Tuple[str, str]:
    """
    解析 FlowID

    :param flow_id: 流的标识符
    :type flow_id: str
    :return: 目标 IP 地址, 源 IP 地址
    :rtype: Tuple[str, str]
    """
    parts = flow_id.split('-')
    source_ip = parts[0]
    destination_ip = parts[1]
    return destination_ip, source_ip
