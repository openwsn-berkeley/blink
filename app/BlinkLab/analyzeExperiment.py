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

    list_len_mote = []
    list_packet_no = []

    set_moteid = set()

    packet_no = 0
    interrupt_list = 0

    dict_mac_rssi = {}
    #netsize_mote_rssi = {}

# blink_neighbor = [(1, -17), (11, -17), (9, -21), (10, -25)]


    list_notif_blink_mgr = get_blink_notif_mgr(get_msg_type(file_name,'NOTIF')) #list all blink notif mgr
    #netsize_mote_rssi.update({networksize:{}})

    for msg in list_notif_blink_mgr:
        data = msg['msg']['notifParams'][5] # payload of blink pakcet

        if data[2] == networksize:
            payload = ''.join([chr(p) for p in data])
            blink_data, blink_neighbor = blink.decode_blink(payload)# decode blink payload

            list_neighbor.append(blink_neighbor) # create neigbor [(moteid, rssi)] list, list_neighbor[0][0]
            list_payload.append(blink_data.encode('hex')) # create blink payload list, 200 msg, there are 200 packets, list_payload[0]

            for moteid, rssi_value in blink_neighbor:
                set_moteid.add(moteid) # create set of moteid value
            packet_no += 1 # number of packets are in creased

            if not interrupt_list:
                list_len_mote.append(len(set_moteid))
                list_packet_no.append(packet_no)

            #if len(set_moteid) >= 10: # number of packets send to, so tag can hear 10 different motes
                #interrupt_list += 1

    # get MAC address and list of RSSI value for each network size
    # mote_rssi = {0:{1:[-22, -25, -24, ...], 2:[], 3:[]}, 5:{1:[], 2:[], 3:[]}}

    all_mac_id = get_mac_moteid_for_size(0, 46, 5, 'blinkLab_final.txt')# network size and MAC address
    
    for mote_id in set_moteid:
        list_rssi = []
        for i in list_neighbor: # ok
            for j in i:
             # all mote ids that are heard by tag
                if j[0] == mote_id:
                    list_rssi.append(j[1])
        dict_mac_rssi.update({all_mac_id[networksize][mote_id]:list_rssi})
    
    
    #print(netsize_mote_rssi)

    return list_payload, list_neighbor, list_packet_no, list_len_mote, dict_mac_rssi

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
    list_len_num_packet = []
    list_delta_time = []
    list_num_neighbor = []
    list_rssi_value = []
    all_rssi = []

    dict_len_mote = {} # number of neighbors that heard by tag
    dict_packet_no = {} # number of packets that are sent to discover 10 motes
    dict_mac_key = {} # MAC addresses that are heard by tag and network size
    netsize_mote_rssi = {} # network size and mote's MAC address, rssi value

    print 'Wait for plotting...'

    for netsize in range(begin_size, end_size, size_step):
        num_neighbor = []
        rssi_value = []
        list_mac_key = []

        data, neighbor, list_packet_no, list_len_mote, dict_mac_rssi = proc_mgr_blink(netsize,file_name)
        
        netsize_mote_rssi.update({netsize:dict_mac_rssi}) # ok
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

        list_len_num_packet.append(len(dict_packet_no[netsize]))
        
        # All MACs have RSSI value
        for mac_key in netsize_mote_rssi[netsize]:
            list_mac_key.append(mac_key)
        dict_mac_key.update({netsize:list_mac_key}) # OK


        #print(len(proc_tag_blink(netsize,file_name))) # number of blink notif
        
        #plt.plot(list_packet_no, list_len_mote, marker='o')
        #plt.xlabel('Number of packets send', fontsize = 10)
        #plt.ylabel('Number of discovered neighbors', fontsize = 10)
        #plt.suptitle('Packet send and number of neighbors network size: {}'.format(netsize), fontsize = 15)
        #plt.show()

    #plt.plot(dict_packet_no[10], dict_len_mote[10], marker='o')
    #plt.plot(dict_packet_no[15], dict_len_mote[15], marker='o')
    #plt.plot(dict_packet_no[20], dict_len_mote[20], marker='o')
    #plt.plot(dict_packet_no[25], dict_len_mote[25], marker='o')
    #plt.plot(dict_packet_no[30], dict_len_mote[30], marker='o')
    #plt.plot(dict_packet_no[35], dict_len_mote[35], marker='o')
    #plt.plot(dict_packet_no[40], dict_len_mote[40], marker='o')
    #plt.plot(dict_packet_no[45], dict_len_mote[45], marker='o')
    
    #plt.plot(list_network_size, list_len_mote, marker='o')
    #plt.legend(['10', '15', '20', '25', '30', '35', '40', '45'], loc='lower right')

    #plt.xlabel('Number of packets send', fontsize = 10)
    #plt.ylabel('Number of network(motes)', fontsize = 10)
    #plt.suptitle('Number of packets send to discover 10 different neighbors', fontsize = 15)

    #plt.plot(list_network_size, list_len_num_packet, marker='o')

    #plt.show()

    plt.boxplot([netsize_mote_rssi[45]['00-17-0d-00-00-31-c6-a1'], netsize_mote_rssi[45]['00-17-0d-00-00-31-c6-a1'], netsize_mote_rssi[45]['00-17-0d-00-00-31-d1-ac']])
    plt.show()
    
    #netsize_mote_rssi = {45:{'00-17-0d-00-00-31-d1-ac':[-29, -30, -28, -32]}}
    print(netsize_mote_rssi[0]) 
    print(netsize_mote_rssi[5]) 

    for i in range(begin_size, end_size, size_step):
        for mac in dict_mac_key[i]:
            print(netsize_mote_rssi[i][mac])
            all_rssi += netsize_mote_rssi[i][mac]
    plt.boxplot(all_rssi)
    print(all_rssi)
    plt.show()




    # plot network size and number of neighbors that are heared in the blink packet
    #plt.plot(list_network_size, list_num_neighbor, marker='o')
    #plt.xlabel('Network size(motes)', fontsize = 10)
    #plt.ylabel('Number of neighbors(motes)', fontsize = 10)
    #plt.suptitle('Number of neighbors and network size', fontsize = 15)
    #plt.show()

    # plot network size and number of packet send to reach 10 neighbors

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
                    moteid_mac[netsize].update({msg_mote['msg']['res'][2]:'-'.join(['%02x'%b for b in msg_mote['msg']['res'][1]])})
        else:
            for msg_mote in list_cmd_getmoteconfig:
                if time_stamp[netsize] < msg_mote['timestamp']:
                    moteid_mac[netsize].update({msg_mote['msg']['res'][2]:'-'.join(['%02x'%b for b in msg_mote['msg']['res'][1]])}) # change MAC address from list to string '00-17-0d-00-00-31-c9-6a'

    return moteid_mac

#============================ main ============================================
def main():
    moteid = get_mac_moteid_for_size(0, 46, 5, 'blinkLab_final.txt')
    plot_experiment(0, 46, 5, 'blinkLab_final.txt')
    raw_input('Press enter to finish')
if __name__=="__main__":
    main()



