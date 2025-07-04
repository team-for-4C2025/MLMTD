import numpy as np
from tqdm import tqdm


def data_clear(
    data: np.ndarray
) -> np.ndarray:
    """
    数据清洗: 去除异常值, 缺失值, 重复值等
    使用 tqdm 显示进度条处理数据的进度条

    :param data: 数据集
    :type data: np.ndarray
    :return: 清洗后的数据
    :rtype: np.ndarray
    """
    try:
        # 去除缺失值
        valid_mask = ~np.isnan(data).any(axis=1)
        data = data[valid_mask]

        # 去除重复值
        data = np.unique(data, axis=0)

        total_rows = len(data)
        with tqdm(total=total_rows, desc="Data cleaning") as pbar:
            pbar.update(total_rows)

        return data
    except ValueError as ve:
        print()
        return data


def data_balance(
    data: np.ndarray,
    label: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    """
    对数据中样本数量不足5000的类别进行复制, 直到每个类别有5000个样本

    :param data: 数据集
    :type data: np.ndarray
    :param label: 标签
    :type label: np.ndarray
    :return: 平衡后的数据集和标签
    :rtype: tuple[np.ndarray, np.ndarray]
    """
    try:
        unique_labels, label_counts = np.unique(label, return_counts=True)
        with tqdm(
            total=len(unique_labels), desc="Balancing classes (Numpy)"
        ) as pbar:
            for label_value, count in zip(unique_labels, label_counts):
                if count < 5000:
                    num_to_copy = 5000 - count
                    class_mask = label == label_value
                    class_data = data[class_mask]
                    class_label_data = label[class_mask]
                    copied_indices = np.random.choice(
                        len(class_data), size=num_to_copy, replace=True
                    )
                    copied_data = class_data[copied_indices]
                    copied_label = class_label_data[copied_indices]
                    data = np.concatenate([data, copied_data], axis=0)
                    label = np.concatenate([label, copied_label], axis=0)
                pbar.update(1)
        return data, label
    except ValueError as ve:
        print()
        return data, label
    except Exception as e:
        print()
        return data, label
