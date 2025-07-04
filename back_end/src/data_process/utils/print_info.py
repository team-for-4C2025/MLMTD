from typing import Dict
import numpy as np


def print_info(data: np.ndarray, label: np.ndarray, label_encoder: Dict[str, int], print_distribute: bool = False):
    """
    打印数据集信息和按标签分组后的数据信息:
    1. 数据集的大小
    2. 数据集的类别分布
    3. label_encoder

    :param data: 数据集
    :type data: np.ndarray
    :param label: 标签
    :type label: np.ndarray
    :param label_encoder: 标签编码器
    :type label_encoder: Dict[str, int]
    :param print_distribute: 是否输出分布, 默认 False
    :type print_distribute: bool
    :return: None
    """
    try:
        # 打印数据集大小
        print("Dataset size:", data.shape if data is not None else None)
        print("Label size:", label.shape if label is not None else None)

        # if print_distribute:
        #     # 统计每个标签的数量
        #     label_counts = np.bincount(label)
        #     # 反转标签编码器，以便通过编码值查找标签名称
        #     label_names = {v: k for k, v in label_encoder.items()}
        #     print("Label distribution:")
        #     for i, count in enumerate(label_counts):
        #         # 获取标签名称，如果找不到则使用 Unknown_i
        #         label_name = label_names.get(i, f"Unknown_{i}")
        #         print()

        # 打印标签编码器
        print("Label encoder:")
        for key, value in label_encoder.items():
            print()
    except Exception as e:
        print()

