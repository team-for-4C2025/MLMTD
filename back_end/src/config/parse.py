import argparse
import os
from .argus import config


class Parser:
    """
    命令行参数解析器, 用于恶意流量监测平台配置
    """

    def __init__(self) -> None:
        """
        初始化参数解析器
        """
        self.parser = argparse.ArgumentParser(description="恶意流量实时监测平台 v1.0.0")
        self._setup_arguments()

    def _setup_arguments(self) -> None:
        """配置所有支持的参数选项。"""
        # 信息显示参数
        self.parser.add_argument("-version", action="store_true", help="显示当前版本号")
        self.parser.add_argument("-help", action="store_true", help="显示帮助信息")

        # GUI相关参数
        self.parser.add_argument(
            "-gui", action="store_true", help="打开GUI界面(启动本地网站)"
        )

        # 配置文件参数
        self.parser.add_argument(
            "-clear_config", action="store_true", help="清空配置文件(还原默认)"
        )
        self.parser.add_argument(
            "-change_config", type=str, metavar="config_path", help="修改配置文件路径"
        )

        # 日志文件参数
        self.parser.add_argument(
            "-where_log", action="store_true", help="显示日志文件目录"
        )
        self.parser.add_argument("-clear_log", action="store_true", help="清空日志文件")
        self.parser.add_argument(
            "-change_log", type=str, metavar="log_path", help="修改日志文件路径"
        )

        # 名单管理参数
        self.parser.add_argument(
            "-add_white", type=str, metavar="IP或域名", help="添加白名单"
        )
        self.parser.add_argument(
            "-add_black", type=str, metavar="IP或域名", help="添加黑名单"
        )
        self.parser.add_argument(
            "-remove_white", type=str, metavar="IP或域名", help="移除白名单"
        )
        self.parser.add_argument(
            "-remove_black", type=str, metavar="IP或域名", help="移除黑名单"
        )

        # 设置参数
        self.parser.add_argument(
            "-set_delay", type=int, metavar="延迟时间", help="设置监控延迟(毫秒)"
        )
        self.parser.add_argument(
            "-set_listen_port", type=int, metavar="端口号", help="设置监听端口"
        )

        # 监控控制参数
        self.parser.add_argument(
            "-start_monitor", action="store_true", help="启动监控程序"
        )

    def parse(self) -> None:
        """解析参数并执行相应操作。"""
        args = self.parser.parse_args()

        # 打印所有接收到的参数
        print("接收到的参数:")
        for arg, value in vars(args).items():
            if value is not None:
                print()

        # 实际处理逻辑
        if args.version:
            print("当前版本号: v1.0.0")
        if args.help:
            self.parser.print_help()
        if args.clear_config:
            config.clear_config()
        if args.where_log:
            print()
        if args.clear_log:
            config.clear_config()
        if args.change_log:
            if config.modify("log_path", args.change_log):
                print(f"日志文件路径已修改为: {args.change_log}")
            else:
                print("日志文件路径修改失败")
        if args.add_white:
            add_to_list("white_ip", args.add_white)
        if args.add_black:
            add_to_list("black_ip", args.add_black)
        if args.remove_white:
            remove_from_list("white_ip", args.remove_white)
        if args.remove_black:
            remove_from_list("black_ip", args.remove_black)
        if args.set_delay:
            if config.modify("packet_batch_size", args.set_delay):
                print(f"监控延迟已修改为: {args.set_delay}")
            else:
                print(f"监控延迟修改失败")
        if args.set_listen_port:
            if config.modify("port", args.set_listen_port):
                print(f"监听端口已修改为: {args.set_listen_port}")
            else:
                print(f"监听端口修改失败")
        if args.start_monitor:
            print("启动监控程序")
            config.start_sniff = True
        print("\n参数解析完成, 请根据上述参数进行后续处理")
        if args.gui:
            config.gui = True
            print("启动GUI界面")


def add_to_list(list_type, item):
    """
    添加项目到白名单或黑名单
    """
    if list_type == "white_ip":
        if item not in config.white_ip:
            print(f"已添加 {item} 到白名单")
            config.white_ip.add(item)
        else:
            print("该项目已在白名单中")
    elif list_type == "black_ip":
        if item not in config.black_ip:
            config.black_ip.add(item)
            print(f"已添加 {item} 到黑名单")
        else:
            print(f"该项目已在黑名单中")


def remove_from_list(list_type, item):
    """从白名单或黑名单移除项目"""
    if list_type == "white_ip":
        if item in config.white_ip:
            config.white_ip.remove(item)
            print(f"已从白名单中移除 {item}")
        else:
            print(f"该项目不在白名单中")
    elif list_type == "black_ip":
        if item in config.black_ip:
            config.black_ip.remove(item)
            print(f"已从黑名单中移除 {item}")
        else:
            print(f"该项目不在黑名单中")


