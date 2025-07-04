import scapy.packet
from pathlib import Path
from typing import Union, Optional, List, Dict
import numpy as np
import time
import socket
from collections import deque

from ..classfiers import CNNClassifier, XGBoosterClassifier
from ..data_process import (
    calculate_session_hash,
    extract_flow_id,
    SessionFeature,
    SessionImage,
)
from ..features import generate_flow_id, analysis_flow_id
from ..config import *


class RealTimePacketAnalysis:
    """
    实时数据包检测
    """

    classifier_type: str = "xgboost"
    classifier_input: dict[int, Union[SessionFeature, SessionImage]] = {}
    cnn_classifier: CNNClassifier = CNNClassifier(device="cpu")
    xgboost_classifier: XGBoosterClassifier = XGBoosterClassifier()

    # flow_id, attack_rate, label_index, time
    history_attack_queues = None
    history_benign_queue = None
    attack_distributions = None

    upload_traffic = 0
    upload_packet_queue = None
    download_traffic = 0
    download_traffic_queue = None

    def __init__(self):
        """
        构造函数
        """
        try:
            # 获取主机名
            hostname = socket.gethostname()
            # 根据主机名获取 IP 地址
            self.ip_address = socket.gethostbyname(hostname)
        except socket.gaierror:
            print("unknown ip")
            self.ip_address = None
        self.cnn_classifier.load(cnn_classifier_path)
        self.xgboost_classifier.load(xgboost_classifier_path)
        self.history_attack_queues = [
            [deque(maxlen=None) for _ in range(7)],  # 分钟队列
            [deque(maxlen=None) for _ in range(7)],  # 小时队列
            [deque(maxlen=None) for _ in range(7)],  # 天队列
        ]
        self.history_benign_queue = [
            [deque(maxlen=None) for _ in range(7)],  # 分钟队列
            [deque(maxlen=None) for _ in range(7)],  # 小时队列
            [deque(maxlen=None) for _ in range(7)],  # 天队列
        ]
        # label_encoder 有 10 个元素, 最后一个元素表示当前区间全部的流量
        # 因为 benign 的下表是 4, 我们还是使用它
        # 每一个数组分别代表 7 分钟 | 小时 | 天的恶意流量的分布
        self.attack_distributions = [[0] * 12, [0] * 12, [0] * 12]

        # 从 log_path 中读取之前的数据并根据当前时间完成更新
        self.init_queues()

    def packet_handler(
        self, realtime_packet: scapy.packet.Packet
    ) -> Optional[np.ndarray]:

        """
        处理一个数据包, 并进行检测

        :param realtime_packet: 捕获的数据包
        :type: scapy.packet.Packet
        :return: 预测结果的概率数组，若不满足条件则返回 None
        """
        try:
            packet_len = len(realtime_packet)
            flow_id = extract_flow_id(realtime_packet)

            if flow_id is None:
                # 不是 ipv4 的数据包
                return None

            session_id = (flow_id[0], flow_id[1])
            upload = session_id[1] == self.ip_address

            # 白名单直接跳过
            other_ip = session_id[0] if upload else session_id[1]
            if other_ip in config.white_ip:
                return None
            elif other_ip in config.black_ip:
                # 不计入攻击分布, 但是计入攻击
                for i in range(3):
                    self.history_attack_queues[i][6].append((flow_id, 1.0, 11, time.time()))
                return None

            session_hash = calculate_session_hash(*session_id)
            flow_id_str = generate_flow_id(*flow_id)

            if self.classifier_type == "xgboost":
                if isinstance(self.classifier_input, SessionImage):
                    self.classifier_input = {
                        session_hash: SessionFeature(realtime_packet)
                    }
                    return None
                else:
                    if session_hash not in self.classifier_input:
                        self.classifier_input[session_hash] = SessionFeature(
                            realtime_packet
                        )
                    else:
                        flow_feature = self.classifier_input[session_hash].update(
                            realtime_packet
                        )
                        if flow_feature is not None and len(flow_feature) > 0:
                            result = self.xgboost_classifier.predict_proba(
                                np.array([flow_feature])
                            )
                            result = result.flatten().tolist()
                            self.record_attack_rate(flow_id_str, result, packet_len, upload)
                            return result
                        else:
                            return None
            elif self.classifier_type == "cnn":
                if isinstance(self.classifier_input, SessionFeature):
                    self.classifier_input = {
                        session_hash: SessionImage(realtime_packet)
                    }
                else:
                    if session_hash not in self.classifier_input:
                        self.classifier_input[session_hash] = SessionImage(
                            realtime_packet
                        )
                        return None
                    else:
                        flow_image_list = self.classifier_input[session_hash].update(
                            realtime_packet
                        )
                        if len(flow_image_list) > 0:
                            result = self.cnn_classifier.predict_proba(
                                np.array(flow_image_list)
                            )
                            result = result[0].flatten().tolist()
                            self.record_attack_rate(flow_id_str, result, packet_len, upload)
                            return result
                        else:
                            return None
            else:
                print("unknown classifier type!")
                return None

        except Exception as e:
            print()
            return None

    def record_attack_rate(
        self, flow_id_str: str, result: List[float], packet_len: int, upload: bool
    ) -> None:
        """
        记录攻击率和攻击分布

        :param flow_id_str: 流的编号
        :type flow_id_str: str
        :param result: 模型预测的概率结果
        :type: List[float]
        :param packet_len: 数据包长度
        :type: int
        :param upload: 是否是上行流量
        :type: bool
        :return: None
        """
        for i in range(3):
            attack_rate = 1 - result[label_encoder["benign"]]
            label_index = int(max(result))

            if attack_rate > config.black_threshold:
                # 进入光荣的黑名单吧
                flow_id = analysis_flow_id(*flow_id_str)
                config.black_ip.add(
                    flow_id[0] if upload else flow_id[1]
                )

            if label_index == label_encoder["benign"]:
                self.history_benign_queue[i][6].append((flow_id_str, time.time()))
            else:
                self.history_attack_queues[i][6].append(
                    (flow_id_str, attack_rate, label_index, time.time())
                )
                self.attack_distributions[i][label_index] += 1
                self.attack_distributions[i][-1] += 1

        if upload:
            self.upload_traffic += packet_len
            self.upload_packet_queue.append((packet_len, time.time()))
        else:
            self.download_traffic += packet_len
            self.download_traffic_queue.append((packet_len, time.time()))

    def update(self):
        """
        更新队列和攻击分布
        """
        intervals = [60, 3600, 3600 * 24]
        for i in range(3):
            self._update(i, intervals[i])

        current_time = time.time()
        while self.upload_packet_queue:
            packet_len, packet_time = self.upload_packet_queue.popleft()
            if current_time - packet_time > 1:
                self.upload_traffic -= packet_len
                continue
            else:
                self.upload_packet_queue.appendleft((packet_len, packet_time))
        
        while self.download_traffic_queue:
            packet_len, packet_time = self.download_traffic_queue.popleft()
            if current_time - packet_time > 1:
                self.download_traffic -= packet_len
                continue
            else:
                self.download_traffic_queue.appendleft((packet_len, packet_time))
        

    def _update(
        self,
        queues_idx: int,
        interval: int,
    ):
        """
        更新队列中的攻击率和攻击分布，并根据当前索引调整队列数据

        :param queues_idx: 队列索引
        :type: int
        :param interval: 时间间隔
        :type: int
        """
        current_time = time.time()
        label_counts = [0] * 11

        # 更新攻击队列
        for i in range(6, -1, -1):
            queue = self.history_attack_queues[queues_idx][i]
            while queue:
                flow_id, data_rate, data_label_index, data_time = queue.popleft()
                correct_index = calculate_index(data_time, current_time, interval)
                if correct_index < 0:
                    label_counts[data_label_index] -= 1
                    self.attack_distributions[queues_idx][data_label_index] -= 1
                    self.attack_distributions[queues_idx][-1] -= 1
                    continue
                if correct_index != i:
                    self.history_attack_queues[queues_idx][correct_index].append(
                        (flow_id, data_rate, data_label_index, data_time)
                    )
                else:
                    queue.appendleft((flow_id, data_rate, data_label_index, data_time))
                    break

        # 更新良性队列
        for i in range(6, -1, -1):
            queue = self.history_benign_queue[queues_idx][i]
            while queue:
                flow_id, data_time = queue.popleft()
                correct_index = calculate_index(data_time, current_time, interval)
                if correct_index < 0:
                    label_counts[label_encoder["benign"]] -= 1
                    continue
                if correct_index != i:
                    self.history_benign_queue[queues_idx][correct_index].append(
                        (flow_id, data_time)
                    )
                else:
                    queue.appendleft((flow_id, data_time))

    def get_attack_distribution(self, index: int) -> Dict[str, float]:
        """
        获取不同分布的攻击

        :param index: 0 表示 min, 1 表示 hour, 2 表示day
        :return: 攻击分布
        """
        if self.attack_distributions[index][-1] == 0:
            return {}

        attack_distribute_dict = {}
        for label, label_index in label_encoder.items():
            if label != "benign":
                attack_distribute_dict[label] = (
                    self.attack_distributions[index][label_index]
                    / self.attack_distributions[index][-1]
                )

        return attack_distribute_dict

    def store_log(self) -> None:
        """
        使用 pathlib 安全地存储日志数据到文件
        会自动创建不存在的目录, 并添加合理的JSON缩进提高可读性

        :return: None
        """
        log_data = {
            "attack_queues": [
                [list(queue) for queue in sub_queues]
                for sub_queues in self.history_attack_queues
            ],
            "benign_queues": [
                [list(queue) for queue in sub_queues]
                for sub_queues in self.history_benign_queue
            ],
            "attack_distributions": self.attack_distributions,
        }
        try:
            log_file = Path(config.log_path)
            log_file.parent.mkdir(parents=True, exist_ok=True)
            log_file.write_text(json.dumps(log_data, indent=2))
        except Exception as e:
            print()

    def init_queues(self):
        """
        从 log.json 读取数据并根据当前时间更新队列
        """
        try:
            with open(config.log_path, "r") as f:
                file_size = os.path.getsize(config.log_path)
                if file_size == 0:
                    print()
                    default_log_data = {
                        "attack_queues": [
                            [list(queue) for queue in sub_queues]
                            for sub_queues in self.history_attack_queues
                        ],
                        "benign_queues": [
                            [list(queue) for queue in sub_queues]
                            for sub_queues in self.history_benign_queue
                        ],
                        "attack_distributions": self.attack_distributions,
                    }
                    with Path(config.log_path).open("w", encoding="utf-8") as log_file:
                        json_data = json.dumps(default_log_data, indent=2)
                        log_file.write(json_data)
                else:
                    f.seek(0)
                    log_data = json.load(f)
                    self.history_attack_queues = [
                        [deque(queue) for queue in sub_queues]
                        for sub_queues in log_data["attack_queues"]
                    ]
                    self.history_benign_queue = [
                        [deque(queue) for queue in sub_queues]
                        for sub_queues in log_data["benign_queues"]
                    ]
                    self.attack_distributions = log_data["attack_distributions"]
                    self.update()
        except FileNotFoundError:
            print(f'"{config.log_path}" not found. Initializing default values.')
            default_log_data = {
                "attack_queues": [
                    [list(queue) for queue in sub_queues]
                    for sub_queues in self.history_attack_queues
                ],
                "benign_queues": [
                    [list(queue) for queue in sub_queues]
                    for sub_queues in self.history_benign_queue
                ],
                "attack_distributions": self.attack_distributions,
            }
            with Path(config.log_path).open("w", encoding="utf-8") as log_file:
                json_data = json.dumps(default_log_data, indent=2)
                log_file.write(json_data)

    def normal_rate(self) -> float:
        """
        正常的概率
        """
        package_size = len(self.history_attack_queues[0][6]) + len(
            self.history_benign_queue[0][6]
        )
        if package_size == 0:
            return 1

        attack_rate = 0
        for _, history_attack_rate, _, _ in self.history_attack_queues[0][6]:
            attack_rate += history_attack_rate

        return 1 - attack_rate / package_size


def calculate_index(data_time, current_time, interval) -> int:
    """
    根据提供的公式计算队列索引

    :param data_time: 数据的时间戳
    :type: int
    :param current_time: 当前时间
    :type: int
    :param interval: 时间间隔
    :type: int
    :return: 计算得到的队列索引
    :rtype: int
    """
    if data_time < current_time - 7 * interval:
        return -1
    return int((data_time - (current_time - 7 * interval)) // interval)


realtime_packet_analysis = RealTimePacketAnalysis()
