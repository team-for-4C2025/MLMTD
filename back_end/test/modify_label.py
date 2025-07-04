from src.data_process import modify_label

if __name__ == '__main__':
    map_dict = {
        'BENIGN': 'benign',
        'Bot': 'bot',
        'DDoS': 'ddos',
        'PortScan': 'portscan',
        'Infiltration': 'infiltration',
        'Brute Force': 'brute_force',
        'XSS': 'xss',
        'Sql Injection': 'injection',
        'FTP - Patator': 'patator',
        'SSH - Patator': 'patator',
        'DoS slowloris': 'dos',
        'DoS Slowhttptest': 'dos',
        'DoS Hulk': 'dos',
        'DoS GoldenEye': 'dos',
        'Heartbleed': 'heartbleed'
    }

    modify_label("D:/code_repository/mtd/data/ori_label", map_dict)