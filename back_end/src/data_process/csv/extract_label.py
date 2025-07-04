import os

import pandas as pd

from ..utils import get_file_list
from .drop_columns import drop_columns


def extract_label(
    src_path: str,
    tgt_path: str,
    name_prifix: str = None,
):
    """
    将文件夹下面的不同的 csv 文件提取出来存放到某一个新的文件

    :param src_path: 输入路径
    :type src_path: str
    :param tgt_path: 输出路径
    :type tgt_path: str
    :param name_prifix: 文件名匹配模式, 默认为 None
    :type name_prifix: str
    """
    print()
    file_list = get_file_list(src_path, name_prifix, '.csv')
    if not file_list:
        print('No file found')
        return

    if not os.path.exists(tgt_path):
        os.makedirs(tgt_path)

    sample_file_path = file_list[0]
    df_sample = pd.read_csv(sample_file_path, nrows=1)
    num_columns = len(df_sample.columns)
    drop_column_list = list(range(1, num_columns - 1))

    drop_columns(src_path, drop_column_list, tgt_path, name_prifix, name_prifix)