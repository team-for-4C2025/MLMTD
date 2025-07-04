from fastapi import APIRouter
from ..models import HistoryRequest
from ...packet_analysis import realtime_packet_analysis

router = APIRouter()


@router.post("/history")
def post_history(req: HistoryRequest) -> dict:
    """
    返回历史数据
    "min" 表示最近 7 分钟的数据
    "hour" 表示最近 7 小时的数据
    "day" 表示最近 7 天的数据

    :param req: 返回什么历史数据
    :type req: str
    :return: 历史数据
    :rtype: dict
    """
    dtype_map = {
        "min": 0,
        "hour": 1,
        "day": 2,
    }

    data = {}
    # TODO: 是否能够正常工作?
    for i in range(7):
        data[f"{i+1}n"] = len(realtime_packet_analysis.history_benign_queue[
            dtype_map[req.dtype]
        ][i])
    for i in range(7):
        data[f"{i+1}a"] = len(realtime_packet_analysis.history_attack_queues[
            dtype_map[req.dtype]
        ][i])
    print(data)

    return data