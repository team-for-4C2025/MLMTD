from fastapi import APIRouter
from ..models import ModifyIP
from ...config import config

router = APIRouter()

@router.get("/whiteip")
def get_white_ip() -> list:
    """
    获取白名单 IP

    :return: 白名单 IP 列表
    :rtype: list
    """
    return config.white_ip

@router.post("/whiteip")
def post_white_ip(req: ModifyIP) -> bool:
    """
    添加白名单 IP

    :param req: IP
    :type req: str
    :return: 添加结果
    :rtype: bool
    """

    return config.modify('white_ip', req)