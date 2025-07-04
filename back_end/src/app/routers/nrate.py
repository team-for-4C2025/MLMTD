from fastapi import APIRouter
from ...packet_analysis import realtime_packet_analysis

router = APIRouter()


@router.get("/nrate")
def get_nrate() -> dict:
    """
    获得 1 - 攻击率: 
    为什么是 1 - 攻击率呢? 不是攻击率呢?
    因为没时间改了

    :return: 1 - 攻击率
    :rtype: dict
    """

    return {
        "nrate" : realtime_packet_analysis.normal_rate() * 100,
        "upload_traffic": realtime_packet_analysis.upload_traffic,
        "download_traffic": realtime_packet_analysis.download_traffic,
    }
    
