from pydantic import BaseModel

class ModifyIP(BaseModel):
    """
    这个类用于修改IP地址的请求参数
    
    true 表示添加, false 表示删除
    """
    op_type: bool  # true 表示添加, false 表示删除
    ip: str