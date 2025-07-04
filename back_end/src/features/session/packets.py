import os.path
from enum import Enum
from typing import List, Dict

from scapy.packet import Packet as ScapyPacket
from scapy.utils import PcapWriter, wrpcap

from .key import SessionKey, generate_session_key


class SessionPackets:
    """
    含有一个流所有的包
    """

    class SessionState(Enum):
        """
        规定的流的类型:
        """
        UNWRITED = 0  # 未写入
        WRITED = 1  # 已写入

    SESSION_KEY: SessionKey = None  # 流的key
    packet_dict: Dict[str, List[ScapyPacket]] = {}  # 标签 + 流的包
    state_dict: Dict[str, SessionState] = {}  # 标签 + 流的状态

    def __init__(self, first_packet: ScapyPacket, label: str):
        """
        初始化

        :param first_packet: 第一个包
        :type first_packet: ScapyPacket
        :param label: 标签
        :type label: str
        :return: None
        """
        self.SESSION_KEY = generate_session_key(first_packet, label)

        self.packet_dict[label] = [first_packet]
        self.state_dict[label] = self.SessionState.UNWRITED

    def write_file(self, dir_path: str):
        """
        将流写入文件

        :param dir_path: 目标路径
        :type dir_path: str
        :return: None
        """
        if not self.packet_dict:
            return

        for label, packet_list in self.packet_dict.items():
            if packet_list == [] or packet_list is None:
                continue

            tgt_path = os.path.join(dir_path, label)
            if not os.path.exists(tgt_path):
                os.makedirs(tgt_path, exist_ok=True)
            file_path = os.path.join(
                tgt_path, self.SESSION_KEY.session_id() + '.pcap')

            try:
                state = self.state_dict[label]
                if state == self.SessionState.UNWRITED:
                    wrpcap(file_path, packet_list)
                    packet_list.clear()
                    self.state_dict[label] = self.SessionState.WRITED
                else:
                    with PcapWriter(file_path, append=True) as pcap_writer:
                        for packet in packet_list:
                            if packet is not None:
                                pcap_writer.write(packet)

                            packet_list.clear()
                    pcap_writer.close()
            except Exception as e:
                print()

    def add_packet(self, packet: ScapyPacket, label: str):
        """
        添加一个包

        :param packet: 要添加的包
        :type packet: ScapyPacket
        :param label: 标签
        :type label: str
        :return: None
        """
        if packet is None:
            return

        if label not in self.packet_dict:
            self.packet_dict[label] = [packet]
            self.state_dict[label] = self.SessionState.UNWRITED
        else:
            self.packet_dict[label].append(packet)
