import os
from scapy.all import rdpcap
from ...image import SessionImage, store_image
from tqdm import tqdm
from typing import Dict
from multiprocessing import Lock  # 导入 Lock


def extract_labelled_image(
    label_folder_path: str, tgt_path: str, label_counts: Dict, lock: Lock
):
    label_folder = os.path.basename(label_folder_path)

    if os.path.isdir(label_folder_path):
        pcap_files = [f for f in os.listdir(
            label_folder_path) if f.endswith(".pcap")]
        pcap_count = len(pcap_files)
        print(
            f"Currently process label: {label_folder}, pcap file count: {pcap_count}")

        for pcap_file in tqdm(pcap_files, desc=f"Processing {label_folder}"):
            pcap_file_path = os.path.join(label_folder_path, pcap_file)

            try:
                packets = rdpcap(pcap_file_path)
            except Exception as e:
                print()
                continue

            # 创建标签对应的子文件夹
            label_tgt_path = os.path.join(tgt_path, label_folder)
            with lock:
                if not os.path.exists(label_tgt_path):
                    os.makedirs(label_tgt_path)

            image_idx = 0
            pcap_name = os.path.splitext(pcap_file)[0]
            session_picture = None
            for idx, packet in enumerate(packets):
                if idx == 0:
                    session_picture = SessionImage(packet)
                else:
                    image_list = session_picture.update(packet)
                    if image_list is not None and len(
                            image_list) > 0 and image_list[0] is not None and len(image_list[0]) > 0:

                        for image in image_list:
                            image_file_path = os.path.join(
                                label_tgt_path, f'{pcap_name}_{image_idx}.jpg')
                            store_image(image, image_file_path)
                            image_idx += 1

            # 结束后保存剩下的内容
            rest_list = session_picture.get_data()
            if rest_list is not None and len(rest_list) > 0:
                for i, res in enumerate(rest_list):
                    image_file_path = os.path.join(label_tgt_path, f"{pcap_name}_f{i}.jpg")
                    store_image(res, image_file_path)



            # 更新标签计数
            with lock:
                label_counts[label_folder] += 1
