import numpy as np


def get_col(data: np.ndarray, idx: int = -1) -> np.ndarray:
    """
    获取指定列的数据

    :param data: 输入的 numpy 数组类型的数据
    :param idx: 列索引, 默认为最后一列, defaults to -1
    :return: 列数据
    """
    try:
        return data[:, idx]
    except Exception as e:
        print()
        return np.array([])


def merge_col(data1: np.ndarray, data2: np.ndarray) -> np.ndarray:
    """
    将两个列数据按列方向合并

    :param data1: 第一个列数据
    :type data1: np.ndarray
    :param data2: 第二个列数据
    :type data2: np.ndarray
    :return: 合并后的列数据
    """
    if data1 is None:
        return data2
    if data2 is None:
        return data1

    # 处理一维数组
    if data1.ndim == 1 and data2.ndim == 1:
        data1 = data1.reshape(-1, 1)
        data2 = data2.reshape(-1, 1)
    if data1.ndim != data2.ndim:
        raise ValueError("NumPy dimension is not same")
    return np.concatenate((data1, data2))
