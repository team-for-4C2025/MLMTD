from src.packet_analysis import realtime_packet_analysis
from src.data_process import read_pcap

if __name__ == '__main__':
    packets = read_pcap(r"D:\code_repository\mtd\data\splited_pcap\xss\172.16.0.1-192.168.10.50.pcap")

    result_list = []
    realtime_packet_analysis.classifier_type = 'cnn'
    for packet in packets:
        result = realtime_packet_analysis.packet_hander(packet)
        if result is not None:
            result_list.append(result)
    for result in result_list:
        print(result)

    realtime_packet_analysis.store_log()

    attact_distribute = realtime_packet_analysis.get_attack_distribution(1)
    print(attact_distribute)