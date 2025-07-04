from ..classfiers import XGBoosterClassifier, CNNClassifier
from scapy.all import *
import numpy as np
import multiprocessing
from concurrent.futures import ProcessPoolExecutor
from ..config import *
from tqdm import tqdm
import time

from ..data_process import (
    extract_flow_id,
    calculate_session_hash,
    SessionFeature,
    SessionImage,
    get_file_list,
)


class PcapPacketAnalyzer:
    """
    静态分析当前的成分
    """

    processed_size: float = 0.0
    total_size: float = 0.0

    def __init__(self):
        pass

    def process_pcap_group(
        self, pcap_group: list[str], model_type: str
    ) -> dict[str, int]:
        """
        处理 pcap 函数

        :param pcap_group:
        :type: List[str]
        :param model_type:
        :type: str
        :return: 每一个标签的分布
        """
        cnn_classifier = None
        xgboost_classifier = None
        if model_type == "xgboost":
            xgboost_classifier = XGBoosterClassifier()
            xgboost_classifier.load(xgboost_classifier_path)
        else:
            cnn_classifier = CNNClassifier(device="cpu")
            cnn_classifier.load(cnn_classifier_path)

        classifier_input = {}
        all_features_or_images = []

        # 开始处理
        batch_total_size = 0
        for pcap_path in pcap_group:
            batch_total_size += os.path.getsize(pcap_path)
            self.total_size += batch_total_size

            # 最复杂的异步等待, 往往只需要最简单的方式
            time.sleep(0.02)

        with tqdm(total=batch_total_size, desc="Processing pcap files") as pbar:
            for pcap_path in pcap_group:
                with PcapReader(pcap_path) as pcap_reader:
                    for pcap_packet in pcap_reader:
                        packet_len = len(pcap_packet)

                        flow_id = extract_flow_id(pcap_packet)
                        if flow_id is not None:
                            # 可能是 IPv6 什么的
                            session_id = (flow_id[0], flow_id[1])
                            session_hash = calculate_session_hash(*session_id)

                            if model_type == "xgboost":
                                if session_hash not in classifier_input:
                                    classifier_input[session_hash] = SessionFeature(
                                        pcap_packet
                                    )
                                    _ = classifier_input[session_hash].update(pcap_packet)
                            else:
                                if session_hash not in classifier_input:
                                    classifier_input[session_hash] = SessionImage(
                                        pcap_packet
                                    )
                                else:
                                    _ = classifier_input[session_hash].update(pcap_packet)

                        self.processed_size += packet_len
                        pbar.update(packet_len)

        for session_content in classifier_input.values():
            if model_type == 'xgboost':
                for feature_content in session_content.get_data():
                    all_features_or_images.append(feature_content)
            else:
                all_features_or_images.append(session_content.get_data())

        if all_features_or_images is None or len(all_features_or_images) == 0:
            print("too small packet to predict")
            return {}

        all_features_or_images = np.array(all_features_or_images)
        print(all_features_or_images.shape)

        print("Predict pcap packet...")
        if model_type == "xgboost":
            predictions = xgboost_classifier.predict_label(all_features_or_images)
        else:
            predictions = cnn_classifier.predict_label(all_features_or_images)

        inverse_label_encoder = {v: k for k, v in label_encoder.items()}
        labels = [inverse_label_encoder[pred] for pred in predictions]

        label_counts = {}
        for label in labels:
            label_counts[label] = label_counts.get(label, 0) + 1

        return label_counts

    def pcap_analysis(
        self,
        pcap_path: str,
        model_type: str = "xgboost",
    ) -> dict[str, float]:
        """
        多线程处理 pcap 文件

        :param pcap_path:
        :param model_type:
        :return:
        """
        self.processed_size = 0.0
        self.total_size = 0.0
        pcap_list = get_file_list(pcap_path, None, ".pcap")
        num_pcaps = len(pcap_list)
        print()

        # 对 pcap 进行分区, 暂时没有完成对同一个 IP 的合并处理
        num_processes = min(len(pcap_list), multiprocessing.cpu_count() // 2)
        chunk_size = len(pcap_list) // num_processes
        pcap_groups = [
            pcap_list[i : i + chunk_size] for i in range(0, len(pcap_list), chunk_size)
        ]

        # 多线程
        with ProcessPoolExecutor(max_workers=num_processes) as executor:
            futures = []
            for pcap_group in pcap_groups:
                future = executor.submit(
                    self.process_pcap_group, pcap_group, model_type
                )
                futures.append(future)

        total_label_counts = {}
        for future in futures:
            label_counts = future.result()
            for label, count in label_counts.items():
                total_label_counts[label] = total_label_counts.get(label, 0) + count

        total_count = sum(total_label_counts.values())
        if total_count == 0:
            return {}

        # 归一化
        label_proportions = {
            label: count / total_count for label, count in total_label_counts.items()
        }

        # 将结果写入 JSON 文件
        try:
            with open(config.pcap_result_path, 'w') as f:
                json_data = json.dumps(label_proportions, indent=4)
                f.write(json_data)
            print()
        except Exception as e:
            print()

        return label_proportions


pcap_packet_analysis = PcapPacketAnalyzer()
