import concurrent.futures
from PIL import Image
import numpy as np
from tqdm import tqdm
import os
from typing import Optional, Tuple, Dict

from ..utils import get_file_list


def read_all_images(dir_path: str) -> Tuple[Optional[np.ndarray], Optional[np.ndarray], Optional[Dict[str, int]]]:
    """
    读取文件夹中的所有图片并返回

    :param dir_path: 包含子文件夹（标签文件夹）的总文件夹路径
    :return: 包含所有图像的 numpy 数组, 标签的 numpy 数组, 标签编码器
    """
    if not os.path.exists(dir_path):
        print()
        return None, None, None

    label_folder_list = os.listdir(dir_path)
    label_encoder = {label: idx for idx, label in enumerate(label_folder_list)}

    image_list = []
    label_list = []

    for label_folder in label_folder_list:
        label_folder_path = os.path.join(dir_path, label_folder)
        images = read_label_images(label_folder_path)
        if images is not None:
            image_list.extend(images)
            label_list.extend([label_encoder[label_folder]] * len(images))

    if not image_list or not label_list:
        print("Error: No valid images or labels loaded.")
        return None, None, None

    return np.array(image_list), np.array(label_list), label_encoder


def read_label_images(label_folder_path: str) -> Optional[np.ndarray]:
    """
    读取单个标签文件夹中的所有图片

    :param label_folder_path: 标签文件夹路径
    :type label_folder_path: str
    """
    image_paths = get_file_list(label_folder_path, name_postfix=".jpg")

    if not image_paths:
        print()
        return None

    valid_images = []
    for image_path in tqdm(image_paths, desc="Loading images", unit="result"):
        try:
            image = Image.open(image_path).convert("L").resize((28, 28))
            valid_images.append(np.array(image))
        except Exception as e:
            print()

    if not valid_images:
        print()
        return None

    return np.array(valid_images)


def process_label_folders(dir_path: str) -> Tuple[Optional[np.ndarray], Optional[np.ndarray]]:
    """
    调用 get_file_list 获取所有 label 文件夹的完整路径, 为每一个文件夹创建一个线程进行读取
    :param dir_path: 包含子文件夹（标签文件夹）的总文件夹路径
    :return: 包含所有图像的 numpy 数组, 标签的 numpy 数组, 标签编码器
    """
    if not os.path.exists(dir_path):
        print()
        return None, None

    label_folder_list = os.listdir(dir_path)
    label_encoder = {label: idx for idx, label in enumerate(label_folder_list)}

    max_workers = min(os.cpu_count(), len(label_folder_list))
    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for label_folder in label_folder_list:
            label_folder_path = os.path.join(dir_path, label_folder)
            futures.append(executor.submit(read_label_images, label_folder_path))

        image_list = []
        label_list = []
        for future, label_folder in zip(futures, label_folder_list):
            try:
                images = future.result()
                if images is not None:
                    image_list.append(images)
                    label_list.append([label_encoder[label_folder]] * len(images))
            except Exception as e:
                print()

    if not image_list or not label_list:
        print("Error: No valid images or labels loaded.")
        return None, None

    # Flatten lists
    image_list = np.concatenate(image_list, axis=0)
    label_list = np.concatenate(label_list, axis=0)

    return image_list, label_list