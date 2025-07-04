from fastapi import APIRouter
from ..models import ModifyPort
from ...config import config

router = APIRouter()

@router.get("/port")
def get_port() -> int:
    """
    获取当前端口
    """
    return config.port

@router.post("/port")
def post_modify_port(req: ModifyPort) -> bool:
    """
    修改端口

    :param req: 新的端口
    :type req: int
    :return: 修改结果
    :rtype: bool
    """

    return config.modify('port', req.port)