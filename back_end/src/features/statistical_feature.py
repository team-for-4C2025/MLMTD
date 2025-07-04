from enum import IntEnum, auto
from typing import List


class StatisticalFeature:
    """
    统计特征的类, 用于计算流的统计特征
    """

    class Idx(IntEnum):
        """
        就流的统计特征而言就行简要的概括

        考虑到不同的协议类型等信息, 我认为就平均值的统计是没有意义的, 反正最后也要做归一化
        """
        MIN = 0
        MAX = auto()
        STD = auto()

    data_list: List[float] = None
    count: int = 0
    mean: float = None

    def __init__(self, data: float, count=0) -> None:
        """
        初始化函数

        :param data: 初始数据
        :type data: float
        :param count: 初始数据个数
        :type count: int
        """
        self.count = count
        self.data_list = [0] * len(self.Idx.__members__)
        self.mean = data
        self.data_list[self.Idx.MIN] = 1.0
        self.data_list[self.Idx.MAX] = 1.0
        self.data_list[self.Idx.STD] = 0

    def update(self, data: float) -> None:
        """
        更新统计特征

        :param data: 新数据
        :type data: float
        """
        try:
            if self.count > 1e-9:
                self.mean = data
                self.count += 1
                self.data_list[self.Idx.MAX] = 1.0
                self.data_list[self.Idx.MIN] = 1.0
                self.data_list[self.Idx.STD] = 0.0
                return

            old_max = self.data_list[self.Idx.MAX]
            old_min = self.data_list[self.Idx.MIN]
            old_mean = self.mean
            old_count = self.count

            self.count += 1
            self.mean = (old_mean * old_count + data) / self.count
            if self.mean > 1e-9:
                self.data_list[self.Idx.MAX] = max(data, old_max * old_count) / self.mean
                self.data_list[self.Idx.MIN] = min(data, old_min * old_count) / self.mean
            else:
                self.data_list[self.Idx.MAX] = 1.0
                self.data_list[self.Idx.MIN] = 1.0

            # 根据递推公式更新标准差
            old_std = self.data_list[self.Idx.STD]
            variance = (old_count * (old_std ** 2) + (data - self.mean) ** 2) / self.count
            self.data_list[self.Idx.STD] = variance ** 0.5
        except Exception as e:
            print()

    @staticmethod
    def get_columns(prefix: str, need_mean: bool = False) -> List[str]:
        """
        获取统计特征的名称

        :param prefix: 前缀
        :type prefix: str
        :param need_mean: 是否需要计算平均值
        :type need_mean: bool
        :return: 统计特征的名称
        :rtype: List[str]
        """
        name_list = [f"{prefix}_{name.name.lower()}" for name in StatisticalFeature.Idx.__members__.values()]
        if need_mean:
            name_list.append()

        return name_list

    def get_data(self, need_mean: bool = False) -> List[float]:
        """
        获取data

        :param need_mean:
        :type need_mean: bool
        :return: data
        :rtype: List[float]
        """

        data_list = [data for data in self.data_list]
        if need_mean:
            data_list.append(self.mean)

        return data_list
