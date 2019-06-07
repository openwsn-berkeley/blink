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
#1, The script presents the relation between network size and number of packet that receives 10 different motes
#2, The script different network size with number of mote increase



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
def get_cmd_mgr_tag(cmd_msg, cmd_name):
    list_cmd_msg = []
    for a_msg in cmd_msg:
        if a_msg['msg']['cmd'] == cmd_name:
            list_cmd_msg.append(a_msg)
    return list_cmd_msg

# decode blink packet then return list neighbor and payload
list_index = []
def proc_mgr_blink(networksize, file_name): # OK

    list_neighbor = []
    list_netsize = []
    list_payload = []
    set_moteid = set()
    list_len_mote = []
    list_packet_no = []
    packet_no = 0

# blink_neighbor = [(1, -17), (11, -17), (9, -21), (10, -25)]


    list_notif_blink_mgr = get_blink_notif_mgr(get_msg_type(file_name,'NOTIF')) #list all blink notif mgr

    for msg in list_notif_blink_mgr:
        data = msg['msg']['notifParams'][5] # payload of blink pakcet

        if data[2] == networksize:
            payload = ''.join([chr(p) for p in data])
            blink_data, blink_neighbor = blink.decode_blink(payload)# decode blink payload

            list_neighbor.append(blink_neighbor) # create neigbor(moteid, rssi) list
            list_payload.append(blink_data) # create blink payload list

            for moteid, rssi_value in blink_neighbor:
                set_moteid.add(moteid) # create set of moteid value
            packet_no += 1

            list_len_mote.append(len(set_moteid))
            
            list_packet_no.append(packet_no)

    return list_payload, list_neighbor, list_packet_no, list_len_mote

# decode blink data in manager and mapping rxTime and issueTime between Tag and Mgr
def proc_tag_blink(networksize, file_name): # OK

    list_delta_time = []
    
    list_notif_blink_mgr = get_blink_notif_mgr(get_msg_type(file_name,'NOTIF'))
    list_blink_cmd_tag = get_cmd_mgr_tag(get_msg_type(file_name,'CMD'), 'dn_blink')
    
    # compare payload id in both side manager and tag
    for msg_mgr in list_notif_blink_mgr:
        data = msg_mgr['msg']['notifParams'][5]
        for msg_tag in list_blink_cmd_tag:
            if data[2] == networksize and data[2:5] == msg_tag['msg']['params']['payload']:
                delta = msg_mgr['timestamp'] - msg_tag['timestamp']
                list_delta_time.append(delta)
                if delta <= 0:
                    raise Exception('Delta should be greater than 0')
    return list_delta_time # 4, present the relation between network size and rxTime - txTime



def plot_experiment(begin_size, end_size, size_step, file_name):

    list_network_size = []
    list_delta_time = []
    list_num_neighbor = []
    list_rssi_value = []
    dict_len_mote = {}
    dict_packet_no = {}

    print 'Wait for plotting...'

    for netsize in range(begin_size, end_size, size_step):
        num_neighbor = []
        rssi_value = []
        data, neighbor, list_packet_no, list_len_mote = proc_mgr_blink(netsize,file_name)

        dict_len_mote.update({netsize:list_len_mote})
        dict_packet_no.update({netsize:list_packet_no})

        for i in neighbor:
            num_neighbor.append(len(i))
            for j in range(len(i)):
                rssi_value.append(i[j][1]) # get the rssi value

        list_network_size.append(netsize)
        list_num_neighbor.append(sta.mean(num_neighbor))
        list_delta_time.append(sta.mean(proc_tag_blink(netsize,file_name)))
        list_rssi_value.append(sta.mean(rssi_value))

        #print(len(proc_tag_blink(netsize,file_name))) # number of blink notif
        
        plt.plot(list_packet_no, list_len_mote, marker='o')
        plt.xlabel('Number of packets send', fontsize = 10)
        plt.ylabel('Number of discovered neighbors', fontsize = 10)
        plt.suptitle('Packet send and number of neighbors network size: {}'.format(netsize), fontsize = 15)
        plt.show()
    
    

    # plot network size and number of neighbors that are heared in the blink packet
    #plt.plot(list_network_size, list_num_neighbor, marker='o')
    #plt.xlabel('Network size(motes)', fontsize = 10)
    #plt.ylabel('Number of neighbors(motes)', fontsize = 10)
    #plt.suptitle('Number of neighbors and network size', fontsize = 15)
    #plt.show()

    # plot network size and number of packet send to reach 10 neighbors
    print(dict_len_mote)
    print(dict_packet_no)

    

# define get all MAC address and mote ID for each network experiment

def get_mac_moteid_for_size(begin_size, end_size, size_step, file_name):
    #1. get all msg networksize in the data file
    #2. get timestamp for each network size (using dictionary)
    #3. create a dictionary of network size and moteid, mac address
    #a dictionary moteid_mac = {5:{1:'M1', 2:'M2', 3:'M3', 4:'M4', 5:'M5'}, 10:{1:'N1', 2:'N2', 3:'N10'}}

    time_stamp = {}
    moteid_mac = {}
    
    list_msg_networksize = get_msg_type(file_name, 'NETWORKSIZE')
    list_cmd_getmoteconfig = get_cmd_mgr_tag(get_msg_type(file_name, 'CMD'), 'dn_getMoteConfig')


    for netsize in range(begin_size, end_size, size_step):
        moteid_mac.update({netsize:{}}) # create moteid_mac dictionary with netsize keys
        # moteid_mac = {0:{}, 5:{}, 10:{}, 15:{}, 20:{}, 25:{}}
        for msg_size in list_msg_networksize:
            if msg_size['msg']['networksize'] == netsize:
                time_stamp[netsize] = msg_size['timestamp']

    for netsize in range(begin_size, end_size, size_step):

        if netsize != begin_size:
            for msg_mote in list_cmd_getmoteconfig:
            
                if time_stamp[netsize] < msg_mote['timestamp'] < time_stamp[netsize-size_step]:
                    moteid_mac[netsize].update({msg_mote['msg']['res'][2]:msg_mote['msg']['res'][1]})
        else:
            for msg_mote in list_cmd_getmoteconfig:
                if time_stamp[netsize] < msg_mote['timestamp']:
                    moteid_mac[netsize].update({msg_mote['msg']['res'][2]: msg_mote['msg']['res'][1]})

    return moteid_mac

#============================ main ============================================
def main():
    moteid = get_mac_moteid_for_size(10, 46, 5, 'blinkLab_final.txt')
    plot_experiment(10, 46, 5, 'blinkLab_final.txt')
    raw_input('Press enter to finish')
if __name__=="__main__":
    main()



