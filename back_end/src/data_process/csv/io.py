import concurrent.futures
import multiprocessing
import pandas as pd
import numpy as np
from tqdm import tqdm
from typing import Tuple, Dict
from sklearn.model_selection import train_test_split

from ..utils import seperate_label, get_file_list


def read_single_labelled_csv(
    file_path: str,
    split: bool,
) -> Tuple[
    np.ndarray,
    np.ndarray,
    np.ndarray,
    np.ndarray,
    Dict[str, int],
]:
    """
    处理单个文件

    :param file_path: 文件路径
    :type file_path: str
    :param split: 是否进行训练集和测试集的拆分
    :type split: bool
    :return: 训练数据、训练标签、测试数据、测试标签和更新后的标签编码器
    :rtype: Tuple[]
    """
    file_train_data = None
    file_train_label = None
    file_test_data = None
    file_test_label = None
    file_label_encoder: Dict[str, int] = {}

    try:
        with open(file_path, encoding="latin-1") as f:
            total_lines = sum(1 for _ in f)

        for chunk in tqdm(
            pd.read_csv(
                file_path, chunksize=10000, encoding="latin-1", low_memory=False
            ),
            total=total_lines // 10000 + 1,
        ):
            # 数据清洗
            chunk = chunk.replace([np.inf, -np.inf], np.nan)
            if chunk.isna().any().any():
                chunk = chunk.dropna()

            # 分离特征和标签
            file_train_data_chunk, file_train_label_chunk = seperate_label(chunk)
            if file_train_data_chunk is None or file_train_label_chunk is None:
                raise ValueError("Invalid data or label")

            # 对标签进行编码
            unique_labels = file_train_label_chunk.unique()
            for label_ in unique_labels:
                if label_ not in file_label_encoder:
                    file_label_encoder[label_] = len(file_label_encoder)

            # 进行拆分
            file_test_data_chunk = None
            file_test_label_chunk = None
            if split:
                file_train_data_chunk_np = file_train_data_chunk.values
                file_train_label_chunk_np = file_train_label_chunk

                (
                    file_train_data_chunk,
                    file_test_data_chunk,
                    file_train_label_chunk,
                    file_test_label_chunk,
                ) = train_test_split(
                    file_train_data_chunk_np,
                    file_train_label_chunk_np,
                    test_size=0.2,
                    random_state=42,
                )

            # 合并数据
            if file_train_data is None:
                file_train_data = file_train_data_chunk
            else:
                file_train_data = np.concatenate(
                    (file_train_data, file_train_data_chunk)
                )

            if file_train_label is None:
                file_train_label = file_train_label_chunk
            else:
                file_train_label = np.concatenate(
                    (file_train_label, file_train_label_chunk), axis=0
                )

            if split:
                if file_test_data is None:
                    file_test_data = file_test_data_chunk
                else:
                    file_test_data = np.concatenate(
                        (file_test_data, file_test_data_chunk), axis=0
                    )

                if file_test_label is None:
                    file_test_label = file_test_label_chunk
                else:
                    file_test_label = np.concatenate(
                        (file_test_label, file_test_label_chunk)
                    )

    except Exception as e:
        print()
        return (
            np.array([]),
            np.array([]),
            np.array([]),
            np.array([]),
            file_label_encoder,
        )

    return (
        file_train_data,
        file_train_label,
        file_test_data,
        file_test_label,
        file_label_encoder,
    )


def read_labelled_csv(
    src_path: str,
    split: bool = False,
    name_prifix: str = None,
) -> Tuple[
    np.ndarray,
    np.ndarray,
    np.ndarray,
    np.ndarray,
    Dict[str, int],
]:
    """
    从文件中读取数据
    如果是文件夹就递归取文件夹下所有的 csv 文件, 如果是文件就直接读文件
    完成数据和标签的读取
    多线程读取文件实现加速
    推荐每一个 csv 文件在 150000 行左右

    :param src_path: 文件夹或文件路径
    :type src_path: str
    :param split: 是否进行训练集和测试集的拆分
    :type split: bool
    :param name_prifix: 文件名匹配模式, 默认为 None
    :type name_prifix: str
    :return: 训练数据, 训练标签, 测试数据, 测试标签和更新后的标签编码器
    :rtype: Tuple[]
    """
    file_list = get_file_list(src_path, name_prifix, ".csv")
    if file_list is None or len(file_list) == 0:
        raise ValueError()

    max_workers = min(multiprocessing.cpu_count() // 2, len(file_list))
    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(read_single_labelled_csv, file_path, split) for file_path in file_list]
        train_data = None
        train_label = None
        test_data = None
        test_label = None
        label_encoder: Dict[str, int] = {}
        all_train_labels = []
        all_test_labels = []
        for future in concurrent.futures.as_completed(futures):
            (
                train_data_chunk,
                train_label_chunk,
                test_data_chunk,
                test_label_chunk,
                file_label_encoder,
            ) = future.result()

            # 合并 label_encoder
            for label in file_label_encoder.keys():
                if label not in label_encoder:
                    label_encoder[label] = len(label_encoder)

            if train_data_chunk is None or train_label_chunk is None:
                continue

            # 合并训练数据
            if train_data is None:
                train_data = train_data_chunk
            else:
                if train_data.ndim != train_data_chunk.ndim:
                    raise ValueError(f'The dim of {train_data_chunk.ndim} and {train_data.ndim} is not equal')
                train_data = np.concatenate((train_data, train_data_chunk), axis=0)

            # 合并训练标签
            if train_label is None:
                train_label = train_label_chunk
            else:
                if train_label.ndim != train_label_chunk.ndim:
                    raise ValueError(f'The dim of {train_label.ndim} and {train_label.ndim} is not equal')
                train_label = np.concatenate((train_label, train_label_chunk), axis=0)

            all_train_labels.extend(train_label_chunk)

            # 如果需要拆分，合并测试数据和标签
            if split:
                if test_data is None:
                    test_data = test_data_chunk
                else:
                    test_data = np.concatenate((test_data, test_data_chunk), axis=0)

                if test_label is None:
                    test_label = test_label_chunk
                else:
                    test_label = np.concatenate((test_label, test_label_chunk), axis=0)

                all_test_labels.extend(test_label_chunk)

    # 进程结束后，进行标签映射
    total_labels = len(all_train_labels) + len(all_test_labels)
    with tqdm(total=total_labels, desc="Mapping labels") as pbar:
        new_train_label = []
        for label in all_train_labels:
            new_train_label.append(label_encoder[label])
            pbar.update(1)
        new_train_label = np.array(new_train_label)

        new_test_label = []
        for label in all_test_labels:
            new_test_label.append(label_encoder[label])
            pbar.update(1)
        new_test_label = np.array(new_test_label)

    if train_data is not None:
        print("Data read over")
    else:
        raise ValueError()

    return (
        train_data,
        new_train_label,
        test_data,
        new_test_label,
        label_encoder,
    )


def write_csv(
    path: str,
    data: np.ndarray,
    label: np.ndarray,
) -> None:
    """
    将数据和标签写入文件
    使用 tqdm 显示进度条处理数据的进度条
    Warning: 没有测试过

    :param path: 保存文件路径
    :param data: 数据集
    :param label: 标签
    """
    try:
        # 将 numpy 数组拼接
        combined_data = np.hstack((data, label.reshape(-1, 1)))
        total_rows = combined_data.shape[0]
        with tqdm(total=total_rows, desc="Writing data") as pbar:
            with open(path, "w", encoding="utf-8") as f:
                for row in combined_data:
                    line = ",".join(map(str, row)) + "\n"
                    f.write(line)
                    pbar.update(1)
    except ValueError as ve:
        print()
    except FileNotFoundError as fnfe:
        print()