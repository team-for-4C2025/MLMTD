from pydantic import BaseModel

class Model(BaseModel):
    """
    这个类用于修改IP地址的请求参数
    """
    model: str