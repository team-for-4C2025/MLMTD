from pydantic import BaseModel

class BlackThreshold(BaseModel):
    """
    黑名单 ip 设置
    """
    threshold: int = 10.0  # 黑阈值，默认 10.0