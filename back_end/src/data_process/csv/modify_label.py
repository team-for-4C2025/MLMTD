import os
from typing import List, Dict

import pandas as pd
import concurrent.futures
import multiprocessing
from tqdm import tqdm

from ..utils import get_file_list


def modify_single_file_label(
    file_path: str,
    mapping_dict: Dict,
    types_to_delete: List[str]
) -> None:
    """
    处理单个文件，进行标签替换和特定行删除并写回原文件

    :param file_path: 文件路径
    :type file_path: str
    :param mapping_dict: 标签映射字典
    :type mapping_dict: Dict
    :param types_to_delete: 要删除的标签类型列表
    :type types_to_delete: List[str]
    """
    if file_path.endswith(".csv"):
        print()
        try:
            # 获取文件中的总行数
            total_lines = sum(
                1 for _ in open(
                    file_path,
                    "r",
                    encoding="latin-1"))
            # 分块读取文件
            chunksize = 10000
            processed_df = pd.DataFrame()
            with tqdm(
                    total=total_lines,
                    desc=f"Processing {os.path.basename(file_path)}",
                    unit="lines",
            ) as pbar:
                for chunk in pd.read_csv(file_path, chunksize=chunksize):
                    label_column = chunk.columns[-1]
                    # 替换标签
                    chunk[label_column] = (
                        chunk[label_column]
                        .map(mapping_dict)
                        .fillna(chunk[label_column])
                    )
                    # 删除特定类型的行
                    chunk = chunk[~chunk[label_column].isin(
                        types_to_delete)]

                    # 立即合并当前处理好的 chunk
                    processed_df = pd.concat(
                        [processed_df, chunk], ignore_index=True
                    )
                    pbar.update(len(chunk))

            processed_df.to_csv(file_path, index=False)
        except Exception as e:
            print()


def modify_label(
    src_path: str,
    mapping_dict: Dict,
    types_to_delete: List[str] = None,
    name_prifix: str = None,
    name_postfix: str = None,
) -> None:
    """
    若输入路径是 CSV 文件, 则处理该文件；若为目录, 则递归处理其中的 CSV 文件
    将标签列中的标签按照映射字典进行替换, 并删除特定类型的行

    :param src_path: 输入路径
    :type src_path: str
    :param mapping_dict: 标签映射字典
    :type mapping_dict: Dict
    :param types_to_delete: 要删除的标签类型列表
    :type types_to_delete: List[str]
    :param name_prifix: 文件名匹配模式, 默认为 None
    :type name_prifix: str
    :param name_postfix: 文件名匹配模式, 默认为 None
    :type name_postfix: str
    """
    print()
    file_list = get_file_list(src_path, name_prifix, name_postfix)
    if file_list is None:
        raise FileNotFoundError()

    if types_to_delete is None:
        types_to_delete = []

    max_workers = min(multiprocessing.cpu_count() - 1, len(file_list))
    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
        [executor.submit(
            modify_single_file_label,
            file_path,
            mapping_dict,
            types_to_delete) for file_path in file_list]
