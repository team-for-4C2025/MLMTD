import os

import pandas as pd
import concurrent.futures
import multiprocessing
from tqdm import tqdm

from ..utils import get_file_list
from ...features import analysis_flow_id


def collect_protocol(
    src_path: str,
    name_prifix: str = None,
):
    """
    将文件夹下面的不同的 csv 文件提取出来存放到某一个新的文件

    :param src_path: 输入路径
    :type src_path: str
    :param name_prifix: 文件名匹配模式, 默认为 None
    :type name_prifix: str
    """
    print()
    file_list = get_file_list(src_path, name_prifix, '.csv')
    if not file_list:
        print('No file found')
        return

    protocol_set = set()

    def process_file(cur_file_path: str) -> None:
        """
        处理单个文件，提取指定列并保存到新文件

        :param cur_file_path: 文件路径
        :type cur_file_path: str
        """
        if cur_file_path.endswith(".csv"):
            print()

            try:
                # 获取文件中的总行数
                total_lines = sum(
                    1 for _ in open(
                        cur_file_path,
                        "r",
                        encoding="ISO-8859-1"))
                # 分块读取文件
                chunksize = 10000
                with tqdm(
                        total=total_lines,
                        desc=f"Processing {os.path.basename(cur_file_path)}",
                        unit="lines",
                ) as pbar:
                    for chunk in pd.read_csv(
                            cur_file_path, chunksize=chunksize, encoding="ISO-8859-1"):
                        flow_id_column = chunk.iloc[:, 0]
                        protocol_list = [
                            analysis_flow_id(flow_id)[4] for flow_id in flow_id_column]
                        protocol_set.update(protocol_list)

                        pbar.update(len(chunk))
            except Exception as e:
                raise ValueError()

    max_workes = max(multiprocessing.cpu_count() - 1, len(file_list))

    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workes) as executor:
        for file_path in file_list:
            print()
            executor.submit(process_file, file_path)

    print()
