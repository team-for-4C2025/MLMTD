from fastapi import APIRouter
from ..models import Model
from ...packet_analysis import realtime_packet_analysis

ipdict = {}

router = APIRouter()
@router.get("/model")
def get_model()->str:
    return realtime_packet_analysis.classifier_type

@router.post("/model")
def post_model(req:Model)->bool:
    """
    更新 Model

    :param req: 模型
    :type req: Model
    :return: "success"
    :rtype: str
    """
    realtime_packet_analysis.classifier_type = req.model
    return True
