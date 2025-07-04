import ipaddress
from fastapi import APIRouter

from ..models import ModifyIP
from ...config import config

router = APIRouter()

@router.get("/blackip")
def get_blackip() -> set:
    """
    获取黑名单 IP

    :return: 黑名单 IP 列表
    :rtype: set
    """
    return config.black_ip

@router.post("/blackip")
def post_blackip(req: ModifyIP) -> bool:
    """
    添加黑名单 IP

    :param req: IP
    :type req: str
    :return: 添加结果
    :rtype: bool
    """

    return config.modify('black_ip', req)