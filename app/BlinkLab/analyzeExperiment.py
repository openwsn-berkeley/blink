#============================ adjust path =====================================

import sys
import os
if __name__ == "__main__":
    here = sys.path[0]
    sys.path.insert(0, os.path.join(here, '..', '..','libs'))
    sys.path.insert(0, os.path.join(here, '..', '..','external_libs'))


#============================ import =====================================

from matplotlib import pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns
import statistics as sta

import json


from SmartMeshSDK.protocols.blink      import blink

#============================ helpers =========================================

# get message on the log file
def get_msg_type(file_name, msg_type):
    list_msg = []

    with open(file_name,'r') as data_file:
        for line in data_file:
            line_dict = json.loads(line)
            if line_dict['type'] == msg_type:
                list_msg.append(line_dict)
    data_file.close()
    return list_msg

# get all blink noftif in manager 1
def get_blink_notif_mgr(notif_msg):
    list_blink_msg = []
    for a_msg in notif_msg:
        if a_msg['msg']['serialport'] == 'COM7' and a_msg['msg']['notifName'] == 'notifData' and a_msg['msg']['notifParams'][3] == 61616:
            list_blink_msg.append(a_msg)
    return list_blink_msg

# get all blink command of tag
def get_blink_cmd_tag(cmd_msg):
    list_cmd_msg = []
    for a_msg in cmd_msg:
        if a_msg['msg']['cmd'] == 'dn_blink':
            list_cmd_msg.append(a_msg)
    return list_cmd_msg

# decode blink packet relate to network size and RSSI value
def proc_mgr_blink(networksize): # OK
    list_neighbor = []
    list_data = []
# 1, present the relation between network size and RSSI value
# 2, present the relation between network size and number of neighbor
# neighbor = [(1, -17), (11, -17), (9, -21), (10, -25)]
# RSSI[0][3] = a[0][3][1]
    list_notif_blink_mgr = get_blink_notif_mgr(get_msg_type('blinkLab_suc.txt','NOTIF'))
    for msg in list_notif_blink_mgr:
        data = msg['msg']['notifParams'][5] # OK: payload of blink pakcet
        if data[2] == networksize:
            payload = ''.join([chr(p) for p in data])
            blink_data, blink_neighbor = blink.decode_blink(payload)
            list_neighbor.append(blink_neighbor) # OK
            list_data.append(blink_data) # OK
    return list_data, list_neighbor
    

# decode blink data in manager and mapping rxTime and issueTime between Tag and Mgr
def proc_tag_blink(networksize): # OK

    list_delta = []
    
    list_notif_blink_mgr = get_blink_notif_mgr(get_msg_type('blinkLab_suc.txt','NOTIF'))
    list_blink_cmd_tag = get_blink_cmd_tag(get_msg_type('blinkLab_suc.txt','CMD'))
    
    # compare payload id in both side manager and tag
    for msg_mgr in list_notif_blink_mgr:
        data = msg_mgr['msg']['notifParams'][5]
        for msg_tag in list_blink_cmd_tag:
            if data[2] == networksize and data[2:5] == msg_tag['msg']['params']['payload']:
                delta = msg_mgr['timestamp'] - msg_tag['timestamp']
                list_delta.append(delta)
                if delta <= 0:
                    raise Exception('Delta should be greater than 0')
    return(list_delta)

# 3, present the relation between network size and txDone-issueTime
# 4, present the relation between network size and rxTime - txTime

def plot_data():
    # OK
    list_network_size = []
    list_delta_time = []
    list_num_neighbor = []
    for netsize in range(0, 46, 5):
        num_neighbor = []
        
        data, neighbor = proc_mgr_blink(netsize)

        for i in neighbor:
            num_neighbor.append(len(i))

        list_network_size.append(netsize)
        list_num_neighbor.append(sta.mean(num_neighbor))
        list_delta_time.append(sta.mean(proc_tag_blink(netsize)))

        # data = ['\x00\x00\x00', '\x00\x00\x01', '\x00\x00\x02', '\x00\x00\x03', '\x00\x00\x04', '\x00\x00\x05']
        print(list_num_neighbor)
    
    # plot network size and number of neighbors
    plt.plot(list_network_size, list_num_neighbor, marker='o')
    plt.xlabel('Network size', fontsize = 10)
    plt.ylabel('Number of neighbors', fontsize = 10)
    plt.suptitle('Number of neighbors and network size', fontsize = 15)
    plt.show()
    
    # plot network size and time
    plt.plot(list_network_size, list_delta_time, marker='o')
    plt.xlabel('Network size', fontsize = 10)
    plt.ylabel('Transmission time', fontsize = 10)
    plt.suptitle('Transmission time and network size', fontsize = 15)
    plt.show()

plot_data()

raw_input('Press enter to finish')




