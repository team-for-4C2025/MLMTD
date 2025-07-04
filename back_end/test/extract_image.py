from src.data_process import extract_labelled_image, multi_thread_process

if __name__ == '__main__':
    multi_thread_process(
        extract_labelled_image,
        r"D:\code_repository\mtd\data\splited_pcap",
        r"D:\code_repository\mtd\data\image",
    )