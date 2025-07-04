from fastapi import APIRouter
from ..models import ModifyPath
from ...config import config

router = APIRouter()

@router.get("/respath")
def get_respath():
    """
    修改静态 pcap 文件
    """
    return config.pcap_result_path

@router.post("/respath")
def post_modify_respath(req: ModifyPath) -> bool:
    """
    修改静态 pcap 文件存储路径, 
    # WARNING: 已经废弃了

    :param req: 新的响应路径
    :type req: ModifyPath
    :return: 修改结果
    :rtype: bool
    """

    return config.modify('pcap_result_path', req.path)