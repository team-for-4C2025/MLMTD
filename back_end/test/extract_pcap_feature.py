from src.data_process import extract_labelled_feature
from src.data_process import multi_thread_process

if __name__ == "__main__":
    multi_thread_process(
        extract_labelled_feature,
        r'D:\code_repository\mtd\data\splited_pcap',
        r'D:\code_repository\mtd\data\features'
    )
