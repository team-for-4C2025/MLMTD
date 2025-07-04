from fastapi import APIRouter
from ..models import ModifyPath
from ...config import config

router = APIRouter()

@router.get("/logpath")
def get_respath() -> str:
    """
    返回 pcap 文件保存路径
    """
    return config.log_path

@router.post("/logpath")
def post_modify_logpath(req: ModifyPath) -> bool:
    """
    修改日志路径

    :param req:
    :rtype: bool
    """
    config.modify('logpath', req)
    return True