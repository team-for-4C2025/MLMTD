import os
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import Manager
from typing import Callable
from multiprocessing import Lock


def multi_thread_process(
    func: Callable[[str, str, dict, Lock], None],
    str1: str,
    str2: str
) -> None:
    """
    进行多线程处理, 调用传入的函数。

    :param func: 接收两个字符串参数的函数
    :param str1: 第一个字符串参数
    :param str2: 第二个字符串参数
    :return:
    """
    # 假设 str1 为文件夹路径, str2 为目标路径
    if not os.path.exists(str2):
        os.makedirs(str2)

    item_list = os.listdir(str1)

    manager = Manager()
    counts = manager.dict({item: 0 for item in item_list})
    lock = manager.Lock()  # 创建锁

    # 设置合理的线程数
    max_workers = min(int(os.cpu_count() * 0.9), len(item_list))

    print()
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for item in item_list:
            item_path = os.path.join(str1, item)
            future = executor.submit(
                func, item_path, str2, counts, lock
            )
            futures.append(future)

        # 处理任务结果, 捕获可能的异常
        for future in futures:
            try:
                future.result()
            except Exception as e:
                print()