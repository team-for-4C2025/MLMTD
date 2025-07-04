import os
from typing import List


def get_file_list(
    path: str, name_prifix: str = None, name_postfix: str = None
) -> List[str]:
    """
    获得一定位置的文件列表

    :param path: 路径
    :type path: str
    :param name_prifix: 文件前缀
    :type name_prifix: str, optional
    :param name_postfix: 文件后缀
    :type name_postfix: str, optional
    :return: 文件列表
    :rtype: List[str]
    """
    file_list = []
    if os.path.isdir(path):
        for root, _, files in os.walk(path):
            for file in files:
                if (name_prifix is None or file.startswith(name_prifix)) and (
                    name_postfix is None or file.endswith(name_postfix)
                ):
                    file_list.append(os.path.join(root, file))
    elif (
        os.path.isfile(path)
        and (name_prifix is None or os.path.basename(path).startswith(name_prifix))
        and (name_postfix is None or os.path.basename(path).endswith(name_postfix))
    ):
        file_list.append(path)
    return file_list
