from pydantic import BaseModel

class ModifyPath(BaseModel):
    """
    修改的文件路径
    """
    path: str