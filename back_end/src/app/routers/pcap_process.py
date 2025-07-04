from fastapi import APIRouter
from ..models import ModifyPath
from ...packet_analysis import pcap_packet_analysis

router = APIRouter()

@router.post("/pcap_process")
def pcap_process(req: ModifyPath):
    """
    修改端口

    :param req: pcap 的路径
    :type req: ModifyPath
    :return: None
    """

    pcap_packet_analysis.pcap_analysis(req.path)