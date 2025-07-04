from pydantic import BaseModel

class ModifyPort(BaseModel):
    """
    修改监听端口
    """
    port: int