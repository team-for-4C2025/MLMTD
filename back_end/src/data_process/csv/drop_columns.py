import os
from typing import List

import pandas as pd
import concurrent.futures
import multiprocessing
from tqdm import tqdm

from ..utils import get_file_list


def drop_single_columns(
    src_path: str,
    tgt_path: str,
    columns_to_delete: List[int]) -> None:
    """
    处理单个文件，删除指定列并写回原文件

    :param src_path: 文件路径
    :type src_path: str
    :param tgt_path: 目标文件路径
    :type tgt_path: str
    :param columns_to_delete: 要删除的列索引列表, 从 0 开始
    :type columns_to_delete: List[int]
    """
    if src_path.endswith(".csv"):
        print()
        try:
            # 获取文件总行数
            total_lines = sum(
                1 for _ in open(
                    src_path,
                    "r",
                    encoding="latin-1"))
            # 按块读取文件
            chunksize = 10000
            all_chunks = []
            with tqdm(
                    total=total_lines,
                    desc=f"dealings with {os.path.basename(src_path)}",
                    unit="lines",
            ) as pbar:
                for chunk in pd.read_csv(src_path, chunksize=chunksize, low_memory=False, encoding='latin-1'):
                    for col_idx in sorted(columns_to_delete, reverse=True):
                        if col_idx < len(chunk.columns):
                            chunk = chunk.drop(
                                chunk.columns[col_idx], axis=1)
                    all_chunks.append(chunk)
                    pbar.update(len(chunk))

            # 将所有块合并
            df = pd.concat(all_chunks, ignore_index=True)
            df = df[df.ne("").any(axis = 1)]

            df.to_csv(tgt_path, index=False)
        except Exception as e:
            print()


def drop_columns(
    src_path: str,
    columns_to_delete: List[int],
    tgt_path: str = None,
    name_prifix: str = None,
    name_postfix: str = None,
) -> None:
    """
    输出一个路径, 如果是 csv 文件, 就进行转化, 如果是 dir, 就递归处理
    删除指定索引的列

    :param src_path: 输入路径
    :type src_path: str
    :param columns_to_delete: 要删除的列索引列表, 从 0 开始
    :type columns_to_delete: List[int]
    :param tgt_path:
    :type tgt_path: str
    :param name_prifix: 文件名匹配模式, 默认为 None
    :type name_prifix: str
    :param name_postfix: 文件名匹配模式, 默认为 None
    :type name_postfix: str
    """
    print()

    file_list = get_file_list(src_path, name_prifix, name_postfix)
    if file_list is None:
        return

    if tgt_path is None:
        tgt_path = src_path

    if os.path.isdir(tgt_path):
        os.makedirs(tgt_path, exist_ok=True)

    max_workers = max(multiprocessing.cpu_count() - 1, len(file_list))

    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
        # 修改调用函数
        [executor.submit(drop_single_columns,
            src_file_path, os.path.join(tgt_path, os.path.basename(src_file_path)), columns_to_delete)
            for src_file_path in file_list]