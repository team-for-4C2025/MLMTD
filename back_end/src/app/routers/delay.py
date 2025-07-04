from fastapi import APIRouter
from ..models import PacketBatchSize
from ...config import config

router = APIRouter()

@router.get('/delay')
def get_delay() -> int:
    """
    获取多少包进行一次检测
    """
    return config.packet_batch_size

@router.post("/delay")
def post_modify_delay(req: PacketBatchSize) -> bool:
    """
    修改延迟

    :param req: 包检测的间隔
    :type req: int
    :return: 修改结果
    :rtype: bool
    """
    if req.delay > 0:
        config.packet_batch_size = req.delay
        return True
    return False