from typing import List, Dict

import scapy.packet

from ..flow import FlowFeature, calculate_flow_hash, extract_flow_id


class SessionFeature:
    """
    在机器学习中, 我们对同一个 IP 进行恶意流量分析, 我们不仅仅需要进行单独流的分析, 我们还需要对会话本身进行分析

    我们参考的对象是 KDD_CUP 和 CIC_IDS2017 的流量提取特征, 同时根据我对网络的理解进行了一些调整
    """

    flow_count: int = 0
    flow_feature_dict: Dict[int, FlowFeature] = {}
    session_feature: FlowFeature = None

    def __init__(self, packet: scapy.packet.Packet) -> None:
        """
        初始化函数

        :param packet: 数据包
        :type packet: scapy.packet.Packet
        :return: 无
        """
        self.session_feature = FlowFeature(packet)
        self.flow_count += 1

        flow_hash = self.session_feature.FLOW_KEY.hash
        self.flow_feature_dict[flow_hash] = FlowFeature(packet)

    def update(
        self, packet: scapy.packet.Packet,
    ) -> List[float | str]:
        """
        更新函数并获取数据
        可能是一组数据, 可能是所有的数据

        :param packet: 新的数据包
        :type packet: scapy.packet.Packet
        :return: 特征数据
        :rtype: Union[List[float], List[List[float]]]
        """
        _ = self.session_feature.update(packet)

        flow_hash = calculate_flow_hash(*extract_flow_id(packet))
        if flow_hash not in self.flow_feature_dict:
            self.flow_feature_dict[flow_hash] = FlowFeature(packet)
            return []

        flow_feature = self.flow_feature_dict[flow_hash].update(packet)
        if len(flow_feature) > 0:
            all_feature = [self.flow_count]
            all_feature.extend(flow_feature)
            all_feature.extend(self.session_feature.get_data())
            return all_feature
        return []

    def get_data(self) -> List[List[float | str]]:
        """
        获取所有的数据

        :return: 所有的数据
        :rtype: List[List[float]]
        """
        session_feature = self.session_feature

        all_feature = []
        for flow_feature in self.flow_feature_dict.values():
            temp_feature = [self.flow_count]
            temp_feature.extend(flow_feature.get_data())
            temp_feature.extend(session_feature.get_data())
            all_feature.append(temp_feature)
        return all_feature

    @staticmethod
    def get_columns() -> List[str]:
        """
        获取特征的列名, 不含有 label

        :return: 列名列表
        :rtype: List[str]
        """
        columns = ["flow_count"]
        columns.extend(FlowFeature.get_columns())
        columns.extend(FlowFeature.get_columns())
        return columns
