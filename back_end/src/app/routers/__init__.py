from .nrate import router as nrate_router
from .attack_distribution import router as atype_router
from .port import router as port_router
from .delay import router as delay_router
from .logpath import router as logpath_router
from .respath import router as respath_router
from .history_attack_distribution import router as classification_router
from .history import router as history_router
from .process import router as process_router
from .white_ip import router as whiteip_router
from .black_ip import router as blackip_router
from .black_threshold import router as blackthreshold_router
from .maliciousrate import router as maliciousrate_router
from .model import router as model_router
from .pcap_process import router as pcap_process_router

routers = [
    nrate_router,
    atype_router,
    port_router,
    delay_router,
    logpath_router,
    respath_router,
    classification_router,
    history_router,
    blackthreshold_router,
    process_router,
    maliciousrate_router,
    model_router,
    blackip_router,
    maliciousrate_router,
    whiteip_router,
    pcap_process_router
]

def include_routers(app):
    """
    处理路由

    :param app:
    :return:
    """
    for router in routers:
        app.include_router(router)