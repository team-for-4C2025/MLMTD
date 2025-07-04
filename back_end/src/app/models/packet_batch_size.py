from pydantic import BaseModel


class PacketBatchSize(BaseModel):
    """
    用于控制延迟
    """
    delay: int
