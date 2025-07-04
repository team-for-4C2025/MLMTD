from src.packet_analysis import realtime_packet_analysis
from src.config import *
from src.app import *
from src.app.routers import *
import threading
import time
from scapy.all import AsyncSniffer

def log():
    """
    日常保存日志
    """
    while True:
        time.sleep(1)
        realtime_packet_analysis.store_log()

def start_sniffing():
    """
    启动抓包监听线程
    """
    print("🚀 正在启动抓包监听...")
    try:
        sniffer = AsyncSniffer(
            iface="eth0",  # ⚠️ 如不是 eth0，请用 `ip a` 查看网卡名
            prn=realtime_packet_analysis.packet_handler,
            store=False
        )
        sniffer.start()
        print("✅ 抓包线程已启动")
    except Exception as e:
        print(f"❌ 抓包启动失败: {e}")


def run_server():
    """
    启动 Web GUI 服务
    """
    include_routers(app)
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == '__main__':
    parser = Parser()
    parser.parse()

    # 启动日志线程
    if config.gui:
        run_server()

    # # 启动抓包线程
    if config.start_sniff:
        thread1 = threading.Thread(target=log)
        thread1.start()
        thread2 = threading.Thread(target=start_sniffing)
        thread2.start()
