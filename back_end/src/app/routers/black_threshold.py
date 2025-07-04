from fastapi import APIRouter
from ..models import BlackThreshold
from ...config import config

router = APIRouter()

blackThreshold = 0.1


@router.get("/black_threshold")
def get_blackthreshold() -> float:
    """
    返回什么什么东西
    """
    # 保留两位小数
    return round(config.black_threshold * 100)


@router.post("/black_threshold")
def post_classification(req: BlackThreshold) -> bool:
    """
    更新黑名单阈值

    :param req: 黑名单阈值
    :return: 是否成功
    """
    config.modify('black_threshold', req.threshold / 100)
    return True
