from fastapi import APIRouter
from ...packet_analysis import realtime_packet_analysis
import random

ipdict = {}

router = APIRouter()


@router.get("/maliciousrate")
def post_maliciousrate() -> dict:
    """
    返回恶意流量占比

    :return: 修改结果
    :rtype: bool
    """

    benign_queue = realtime_packet_analysis.history_attack_queues[0][6]
    attack_queue = realtime_packet_analysis.history_attack_queues[0][6]

    traffic_dict = {}
    for flow_id, attack_rate, _, _ in attack_queue:
        if flow_id not in traffic_dict:
            traffic_dict[flow_id] = attack_rate
        traffic_dict[flow_id] += attack_rate
        traffic_dict[flow_id] %= 1

    for flow_id, _ in benign_queue:
        if flow_id not in traffic_dict:
            traffic_dict[flow_id] = 0

    return traffic_dict
