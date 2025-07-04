from src.packet_analysis import PcapPacketAnalyzer

if __name__ == '__main__':
    pcap_packet_analyzer = PcapPacketAnalyzer()
    distribute = pcap_packet_analyzer.pcap_analysis(
        r"D:\code_repository\data\splited_pcap\brute_force\172.16.0.1-192.168.10.50.pcap")
    print(distribute)
