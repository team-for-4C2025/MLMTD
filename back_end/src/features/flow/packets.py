import os.path
from typing import List
from enum import Enum

from scapy.packet import Packet as ScapyPacket
from scapy.utils import PcapWriter, wrpcap

from .key import FlowKey, generate_flow_key


class FlowPackets:
    """
    含有一个流所有的包
    """

    class FlowState(Enum):
        """
        规定的流的类型:
        """
        UNWRITED = 0  # 未写入
        WRITED = 1  # 已写入

    packet_list: List[ScapyPacket] = []
    start_time: float = 0.0  # 第一个包的时间
    pre_time: float = 0.0  # 上一个包的时间
    total_size: float = 0.0  # 总大小
    FLOW_KEY: FlowKey = None  # 流的key
    state: FlowState = FlowState.UNWRITED

    def __init__(self, first_packet: ScapyPacket, label: str):
        """
        初始化

        :param first_packet: 第一个包
        :type first_packet: ScapyPacket
        :param label: 标签
        :type label: str
        :return: None
        """
        self.packet_list = [first_packet]
        self.start_time = first_packet.time
        self.pre_time = first_packet.time
        self.total_size += len(bytes(first_packet))
        self.state = self.FlowState.UNWRITED
        self.LABEL = label
        self.FLOW_KEY = generate_flow_key(first_packet, label)

    def write_file(self, dir_path: str):
        """
        将流写入文件

        :param dir_path: 目标路径
        :type dir_path: str
        :return: None
        """
        if self.packet_list == [] or self.packet_list is None:
            return
        tgt_path = os.path.join(dir_path, self.LABEL)
        if not os.path.exists(tgt_path):
            os.makedirs(tgt_path, exist_ok=True)

        file_path = os.path.join(tgt_path, self.FLOW_KEY.__str__() + '.pcap')

        # print(f'write file to {file_path}, total size: {self.total_size} bytes')
        try:
            if self.state == self.FlowState.UNWRITED:
                # 未写入状态，进行覆盖写入
                wrpcap(file_path, self.packet_list)
                self.packet_list.clear()
            elif self.state == self.FlowState.WRITED:
                # 已写入状态，继续写入
                with PcapWriter(file_path, append=True) as pcap_writer:
                    for packet in self.packet_list:
                        pcap_writer.write(packet)

                pcap_writer.close()
            self.packet_list.clear()
        except Exception as e:
            print()

    def add_packet(self, packet: ScapyPacket):
        """
        添加一个包

        :param packet: 要添加的包
        :type packet: ScapyPacket
        :return: None
        """
        if packet is None:
            return False
        self.packet_list.append(packet)
        self.pre_time = packet.time
        self.total_size += len(bytes(packet))
