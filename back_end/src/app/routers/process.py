from fastapi import APIRouter
from ...packet_analysis import pcap_packet_analysis

router = APIRouter()


@router.get("/process")
def get_process() -> int:
    """
    获取进程信息

    :return: 进程信息
    :rtype: dict
    """
    if pcap_packet_analysis.total_size == 0:
        return 100
    # TODO: 是否能够正常工作
    print((pcap_packet_analysis.processed_size / pcap_packet_analysis.total_size) * 100)
    return (pcap_packet_analysis.processed_size / pcap_packet_analysis.total_size) * 100
