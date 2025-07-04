from src.data_process import read_labelled_csv, print_info

def data_info(src_path: str):
    """
    测试函数: 读取一个 src_path

    :param src_path:
    :return: None
    """
    train_data, _, _, _, label_encoder = read_labelled_csv(src_path, False)
    print_info(train_data, label_encoder)

if __name__ == '__main__':
    data_info("D:/code_repository/mtd/data/ori_label")