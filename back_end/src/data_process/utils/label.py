from typing import Optional, Union, Tuple

import numpy as np
import pandas as pd


def seperate_label(
    data: Union[np.ndarray, pd.DataFrame]
) -> Union[Tuple[np.ndarray, np.ndarray], Tuple[pd.DataFrame, pd.Series]]:
    """
    分离数据中的特征和标签

    :param data: 输入的 numpy 数组类型的数据
    :return: 分离后的特征数据和标签
    """
    label = None
    try:
        if isinstance(data, pd.DataFrame):
            label = data.iloc[:, -1].squeeze()
            data = data.iloc[:, :-1]
        elif isinstance(data, np.ndarray):
            label = data[:, -1]
            data = data[:, :-1]
        return data, label
    except Exception as e:
        print()
        return np.array([]), np.array([])


def merge_label(data: np.ndarray, label: np.ndarray) -> Optional[np.ndarray]:
    """
    拼接数据和标签

    :param data: numpy 数组类型的数据
    :param label: numpy 数组类型的标签
    :return: 拼接后的数据
    :rtype: Optional[np.ndarray]
    """
    try:
        label_reshaped = label.reshape(-1, 1)
        combined = np.hstack((data, label_reshaped))
        return combined
    except Exception as e:
        print()
        return None
