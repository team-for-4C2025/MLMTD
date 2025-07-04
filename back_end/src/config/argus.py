import os
from typing import Set
from ..app.models import ModifyIP
import json

label_encoder = {
    "dos": 0,
    "brute_force": 1,
    "infiltration": 2,
    "injection": 3,
    "benign": 4,
    "ddos": 5,
    "bot": 6,
    "FTP-Patator": 7,
    "xss": 8,
    "portscan": 9,
    "SSH-Patator": 10,
    "black_ip": 11,
}

label_encoder_len = 11

# 获取当前文件所在目录
current_dir = os.path.dirname(os.path.abspath(__file__))
# 构建项目根目录路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))

# 构建绝对路径
cnn_classifier_path = os.path.join(project_root, "mtd", "model", "cnn.pth")
xgboost_classifier_path = os.path.join(project_root, "mtd", "model", "xgboost.joblib")
temp_folder_path = os.path.join(project_root, "mtd", "temp")
config_path = os.path.join(project_root, "mtd", "config.json")
default_log_path = os.path.join(project_root, "mtd", "log.json")
default_pcap_result_path = os.path.join(
    project_root, "mtd", "pcap_analysis_result.json"
)
default_black_threshold = 0.1
html_path = os.path.join(
    project_root, "mtd", "assets", "index.html"
)


def print_help():
    help_text = """
    Configuration Options:
    - black_ip: Set of IP addresses to be blacklisted.
    - white_ip: Set of IP addresses to be whitelisted.
    - black_threshold: Threshold for blacklisting (integer).
    - pcap_result_path: Path for log files (string).
    - port: Set of ports (integer).
    """
    print(help_text)


class Config:
    """
    保存和加载一些参数
    """

    black_ip: Set[str] = set()
    white_ip: Set[str] = set()
    black_threshold: float = 0.0  # 表示没有延迟
    pcap_result_path: str = default_pcap_result_path
    log_path: str = default_log_path
    port: int = 8080
    packet_batch_size = 10
    start_sniff = False
    gui = False

    def __init__(self):
        """
        从配置文件中读取上面的值
        """
        try:
            with open(config_path, "r") as f:
                data = json.load(f)
                self.black_ip = set(data.get("black_ip", []))
                self.white_ip = set(data.get("white_ip", []))
                self.black_threshold = data.get("black_threshold", 0.0)
                self.pcap_result_path = data.get(
                    "pcap_result_path", default_pcap_result_path
                )
                self.log_path = data.get("log_path", default_log_path)
                self.port = data.get("port", 8080)
                self.packet_batch_size = data.get("packet_batch_size", 10)
        except FileNotFoundError:
            print(
                f"config file {config_path} unfound. Creating and initializing with default data"
            )
            self.clear_config()
        except json.JSONDecodeError:
            print(f"error occurred in config file {config_path}. using default data")
            self.clear_config()

    def modify(self, argu_name: str = "black_ip", value=None) -> bool:
        """
        进行修改, 并及时写入
        black_ip,
        white_ip,
        black_threshold,
        pcap_result_path,
        log_path,
        port,
        packet_batch_size

        :param argu_name: 配置名称, 包含:
        :param value: 要设置的新值
        :return:
        """
        if argu_name == "black_ip":
            if isinstance(value, ModifyIP):
                if value.op_type:
                    if value.ip in self.black_ip:
                        return False

                    self.black_ip.add(value.ip)
                else:
                    if value.ip in self.black_ip:
                        self.black_ip.remove(value.ip)
            return False
        elif argu_name == "white_ip":
            if isinstance(value, ModifyIP):
                if value.op_type:
                    if value.ip in self.white_ip:
                        return False

                    self.white_ip.add(value.ip)
                else:
                    if value.ip in self.white_ip:
                        self.white_ip.remove(value.ip)
            return False
        elif argu_name == "black_threshold":
            if isinstance(value, float):
                self.black_threshold = value
            else:
                print()
        elif argu_name == "pcap_result_path":
            if isinstance(value, str):
                self.pcap_result_path = value
            else:
                print()
                return False
        elif argu_name == "log_path":
            if isinstance(value, str):
                self.log_path = value
            else:
                print()
                return False
        elif argu_name == "port":
            if isinstance(value, int):
                self.port = value
            else:
                print()
                return False
        elif argu_name == "packet_batch_size":
            if isinstance(value, int):
                self.packet_batch_size = value
            else:
                return False
        else:
            print()
            return False

        self.write_config()
        return True

    def write_config(self):
        """
        写入配置文件
        """
        config_data = {
            "black_ip": list(self.black_ip),
            "white_ip": list(self.white_ip),
            "black_threshold": self.black_threshold,
            "packet_batch_size": self.packet_batch_size,
            "pcap_result_path": self.pcap_result_path,
            "log_path": self.log_path,
            "port": self.port,
        }
        try:
            with open(config_path, "w") as f:
                json_str = json.dumps(config_data, indent=4)
                f.write(json_str)
            print("config file updated")
        except FileNotFoundError:
            print()
        except Exception as e:
            print()

    @staticmethod
    def clear_config():
        """
        将当前参数重新设置并写入配置文件:

        :return:
        """
        default_data = {
            "black_ip": list(),
            "white_ip": list(),
            "black_threshold": default_black_threshold,
            "packet_batch_size": 10,
            "pcap_result_path": default_pcap_result_path,  # 使用初始的空字符串
            "log_path": default_log_path,
            "port": 8080,
        }
        try:
            with open(config_path, "w") as f:
                json_str = json.dumps(default_data, indent=4)
                f.write(json_str)
            print("config file updated")
        except FileNotFoundError:
            print()
        except Exception as e:
            print()


config = Config()
