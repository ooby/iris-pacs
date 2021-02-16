#!/usr/bin/env python3
#-*- coding: utf-8 -*-
import configparser
import os
import socket
import sys
from pynetdicom import AllStoragePresentationContexts, build_context


DEFAULT_CONTEXTS = [
        '1.2.840.10008.1.1',
        '1.2.840.10008.5.1.4.1.1.2',
        '1.2.840.10008.5.1.4.1.1.7',
        '1.2.840.10008.5.1.4.1.1.7.1',
        '1.2.840.10008.5.1.4.1.1.7.2',
        '1.2.840.10008.5.1.4.1.1.7.3',
        '1.2.840.10008.5.1.4.1.1.7.4'
        ]


def is_valid_ipv4(address):
    '''Check for valid IPv4 address'''
    try:
        socket.inet_pton(socket.AF_INET, address)
    except AttributeError:
        try:
            socket.inet_aton(address)
        except socket.error:
            return False
        return address.count('.') == 3
    except socket.error:
        return False
    return True


def main():
    '''Main'''
    print(' - IRIS-PACS configuration tool:')

    print('Choose work mode [1: PACS-server (by default), 2: DICOM-gateway]: ')
    work_mode = answer = 1
    answer = input()
    if answer.isdigit() and int(answer) in (1, 2):
        work_mode = int(answer)
    
    gw_target_address = None
    if int(work_mode) == 2:
        print('Enter DICOM-gateway target IP address (xxx.xxx.xxx.xxx):')
        gw_target_address = input()
        if is_valid_ipv4(gw_target_address):
            gw_target_address = str(gw_target_address)
        else:
            print('Entered address is not valid ipv4')
            sys.exit(0)
    
    gw_target_port = None
    if int(work_mode) == 2:
        gw_target_port = 104
        print('Enter DICOM-gateway target IP port (default: 104):')
        answer = input()
        if answer.isdigit():
            gw_target_port = int(answer)

    print('Enter storage presentation contexts config variant [1: Basic (by default), 2: Full]: ')
    variant = answer = 1
    answer = input()
    if answer.isdigit() and int(answer) in (1, 2):
        variant = int(answer)

    print('Enter IRIS-PACS port (default: 104):')
    port = 104
    answer = input()
    if answer.isdigit():
        port = int(answer)

    print('Enter MongoDB server IP address (xxx.xxx.xxx.xxx):')
    answer = input()
    if is_valid_ipv4(answer):
        db_address = str(answer)
    else:
        print('Entered address is not valid ipv4')
        sys.exit(0)

    print('Enter MongoDB server port (default: 27017):')
    db_port = 27017
    answer = input()
    if answer.isdigit():
        db_port = int(answer)

    print('Enter RabbitMQ server IP address (xxx.xxx.xxx.xxx):')
    answer = input()
    if is_valid_ipv4(answer):
        mq_address = str(answer)
    else:
        print('Entered address is not valid ipv4')
        sys.exit(0)

    print('Enter RabbitMQ server port (default: 5672):')
    mq_port = 5672
    answer = input()
    if answer.isdigit():
        mq_port = int(answer)

    print('\n')
    print(f'Work mode: {work_mode}')
    if gw_target_address:
        print(f'DICOM-gateway target address: {gw_target_address}')
    if gw_target_port:
        print(f'DICOM-gateway target port: {gw_target_port}')
    print(f'Storage presentation contexts config variant: {variant}')
    print(f'IRIS-PACS port: {port}')
    print(f'MongoDB server IP address: {db_address}')
    print(f'MongoDB server port: {db_port}')
    print(f'RabbitMQ server IP address: {mq_address}')
    print(f'RabbitMQ server port: {mq_port}')

    config = configparser.ConfigParser()
    if work_mode == 1:
        config['IRIS-PACS'] = {'port': port, 'mode': work_mode}
    else:
        config['IRIS-PACS'] = {
            'port': port,
            'mode': work_mode
            }
        config['GW-TARGET'] = {
            'address': gw_target_address,
            'port': gw_target_port
        }
    config['MongoDB'] = {
            'address': db_address,
            'port': db_port
            }
    config['RabbitMQ'] = {
            'address': mq_address,
            'port': mq_port
            }
    if variant == 1:
        config['SupportedContexts'] = {'presentationcontexts': DEFAULT_CONTEXTS}
    else:
        ctx = [cx.abstract_syntax for cx in AllStoragePresentationContexts]
        config['SupportedContexts'] = {'presentationcontexts': ctx}

    config_file_name = os.path.join(os.path.abspath('..'), 'config.ini')
    with open(config_file_name, 'w') as config_file:
        config.write(config_file)
    print(f'Your configuration was written in: {config_file_name}')


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
