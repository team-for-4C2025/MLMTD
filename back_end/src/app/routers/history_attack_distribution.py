from fastapi import APIRouter
from ..models import HistoryRequest
from ...packet_analysis import realtime_packet_analysis

router = APIRouter()

@router.post("/history_attack_distribution")
def post_history_attack_distribution(req: HistoryRequest) -> dict:
    """
    分类历史数据

    :param req: HistoryRequest
    :type req: HistoryRequest
    :return: 分类结果
    :rtype: dict
    """

    dtype_map = {
        'min': 0,
        'hour': 1,
        'day': 2,
    }
    # TODO: 这个有问题
    print(1)
    return realtime_packet_analysis.get_attack_distribution(dtype_map[req.dtype])