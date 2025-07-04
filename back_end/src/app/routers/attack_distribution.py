from fastapi import APIRouter
from ...packet_analysis import realtime_packet_analysis

router = APIRouter()


@router.get("/atype")
def get_attack_distribution() -> dict:
    """
    获取攻击类型列表

    :return: 攻击类型列表
    :rtype: dict
    """
    return realtime_packet_analysis.get_attack_distribution(0)
