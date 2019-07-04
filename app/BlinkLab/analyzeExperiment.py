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
import copy


from SmartMeshSDK.protocols.blink      import blink

#============================ helpers =========================================
#1, The script presents the relation between network size and number of packet that receives 10 different motes
#2, The script different network size with number of mote increase

# get message from log file
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

# decode blink packet then return list neighbor, payload, number of packets send, number of motes and rssi value
def proc_mgr_blink(networksize, discover_10, file_name):

    list_neighbor = []
    list_netsize = []
    list_payload = []
    all_data = [] # all raw blink data

    list_num_packet = [] # list of number of packets send
    list_num_mote = [] # list of number of motes

    set_moteid = set() # set of different mote id

    packet_no = 0
    count_10_neighbors = 0

    dict_mac_rssi = {}

    # blink_neighbor = [[(1, -17), (11, -17), (9, -21), (10, -25)], [(9, -21), (10, -25)]]

    list_notif_blink_mgr = get_blink_notif_mgr(get_msg_type(file_name,'NOTIF')) #list all blink notif mgr

    for msg in list_notif_blink_mgr:
        all_data.append(msg['msg']['notifParams'][5]) # payload of blink packet
        
        data = msg['msg']['notifParams'][5] # payload of blink packet
        #dict_netsize_tranid_mote[data[2]][data[3]].append(data[7])
        
        if data[2] == networksize:
            #num_neigbors = data[7] # number of discoverd motes
            # data[2] is net size
            # data[3] is tran id,
            # data[4] is packet id
            payload = ''.join([chr(p) for p in data])
            blink_data, blink_neighbor = blink.decode_blink(payload)# decode blink payload

            list_neighbor.append(blink_neighbor) # create neigbor [(moteid, rssi)] list, list_neighbor[0][0]
            list_payload.append(blink_data.encode('hex')) # create blink payload list, 200 msg, there are 200 packets, list_payload[0]

            for moteid, rssi_value in blink_neighbor:
                set_moteid.add(moteid) # create set of moteid value
            packet_no += 1 # number of packets are in creased
            if discover_10:
                if not count_10_neighbors:
                    list_num_mote.append(len(set_moteid))
                    list_num_packet.append(packet_no)

                if len(set_moteid) >= 10: # number of packets send to, so tag can hear 10 different motes
                    count_10_neighbors += 1
            else:
                list_num_mote.append(len(set_moteid))
                list_num_packet.append(packet_no)
    # get MAC address and list of RSSI value for each network size
    # mote_rssi = {0:{1:[-22, -25, -24, ...], 2:[], 3:[]}, 5:{1:[], 2:[], 3:[]}}
    print dict_netsize_tranid_mote
    all_mac_id = get_mac_moteid_for_size(0, 46, 5, 'blinkLab_final.txt')# network size and MAC address

    for mote_id in set_moteid:
        list_rssi = []
        for i in list_neighbor:
            for j in i:
             # all mote ids that are heard by tag
                if j[0] == mote_id:
                    list_rssi.append(j[1])
        dict_mac_rssi.update({all_mac_id[networksize][mote_id]:list_rssi})

    return list_payload, list_neighbor, list_num_packet, list_num_mote, dict_mac_rssi
def proc_mgr_blink_mote(file_name):

    dict_netsize_tranid_packet = {net:{trans: [] for trans in range(20)} for net in range(0,46,5)} # the dictionary {net1: {tran1: [0, 1,2, 3,4, 5,], tran2 : [0, 1,2, 9], tran3: [0, 1,2,9]}, net2: {tran1:[], tran2: [], tran3:[]}, net3:{}}
    dict_netsize_tranid_mote = {net:{trans: [] for trans in range(20)} for net in range(0,46,5)} 
    # the dictionary {net1: {num_motes: [2, 4,3, 3,4, 3,], tran2 : [4, 1,2, 3], tran3: [3, 1,2,4]}, net2: {tran1:[], tran2: [], tran3:[]}, net3:{}}
    dict_netsize_packet_num_mote = {net:{packetid: [] for packetid in range(10)} for net in range(0,46,5)} # {netsize:{pk:[num_mote]}}
    dict_netsize_packet_diff_mote = {net:{packetid: [] for packetid in range(10)} for net in range(0,46,5)} # {netsize:{pk:[diff_mote]}}

    set_diff_mote = set()
    
    list_average_num_mote = []


    list_notif_blink_mgr = get_blink_notif_mgr(get_msg_type(file_name,'NOTIF')) #list all blink notif mgr

    for msg in list_notif_blink_mgr:
        
        data = msg['msg']['notifParams'][5] # payload of blink packet
        dict_netsize_tranid_mote[data[2]][data[3]].append(data[7])
        dict_netsize_tranid_packet[data[2]][data[3]].append(data[4])
        dict_netsize_packet_num_mote[data[2]][data[4]].append(data[7])
        
        transid = data[3]

        if data[7] == 1:
            set_diff_mote.add(data[9])
        elif data[7] == 2:
            set_diff_mote.add(data[9])
            set_diff_mote.add(data[12])
        elif data[7] == 3:
            set_diff_mote.add(data[9])
            set_diff_mote.add(data[12])
            set_diff_mote.add(data[15])
        else:
            set_diff_mote.add(data[9])
            set_diff_mote.add(data[12])
            set_diff_mote.add(data[15])
            set_diff_mote.add(data[18])

        dict_netsize_packet_diff_mote[data[2]][data[4]].append(len(set_diff_mote))

        if data[4] == 9:
            set_diff_mote = set()
            
        #if data[3] 
    # 3 value is oK

    #print 'num:', dict_netsize_tranid_mote
    #print 'packet:', dict_netsize_tranid_packet
    #print 'packet:', dict_netsize_packet_num_mote
    print 'diff_mote:', dict_netsize_packet_diff_mote
    
    list_average_num_mote.append(sta.mean(dict_netsize_packet_diff_mote[45][0]))
    list_average_num_mote.append(sta.mean(dict_netsize_packet_diff_mote[45][1]))
    list_average_num_mote.append(sta.mean(dict_netsize_packet_diff_mote[45][2]))
    list_average_num_mote.append(sta.mean(dict_netsize_packet_diff_mote[45][3]))
    list_average_num_mote.append(sta.mean(dict_netsize_packet_diff_mote[45][4]))
    list_average_num_mote.append(sta.mean(dict_netsize_packet_diff_mote[45][5]))
    list_average_num_mote.append(sta.mean(dict_netsize_packet_diff_mote[45][6]))
    list_average_num_mote.append(sta.mean(dict_netsize_packet_diff_mote[45][7]))
    list_average_num_mote.append(sta.mean(dict_netsize_packet_diff_mote[45][8]))
    list_average_num_mote.append(sta.mean(dict_netsize_packet_diff_mote[45][9]))
    
    print list_average_num_mote
    
    # plot
    #plt.suptitle('Distribution of number of neighbor for each packet', fontsize = 12)
    #labels = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    #plt.xticks(range(1, 11), labels, fontsize = 10)
    #plt.ylabel('Discovered mote', fontsize = 10)
    #
    #plt.boxplot([dict_netsize_packet_num_mote[45][packetid] for packetid in range(10)])
    #plt.show() 
    
    
    # plot discovered different motes
    plt.suptitle('Distribution discovered motes', fontsize = 12)
    #labels = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    #plt.xticks(range(1, 11), labels, fontsize = 10)
    plt.xlabel('Packet send', fontsize = 10)
    plt.ylabel('Discovered mote', fontsize = 10)

    plt.boxplot([dict_netsize_packet_diff_mote[45][packetid] for packetid in range(10)])
    
    # plot discovered different motes
    #plt.suptitle('Distribution discovered motes', fontsize = 12)
    #labels = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    #plt.xticks(range(1, 11), labels, fontsize = 10)
    #plt.ylabel('Discovered mote', fontsize = 10)

    plt.plot(range(1, 11), list_average_num_mote, marker = 'o')
    plt.show()
    



# decode blink data in manager and mapping rxTime and issueTime between Tag and Mgr
def proc_tag_blink(networksize, file_name):

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

    list_network_size = [] # all network size from 0 to 45
    list_len_num_packet_discover_10_motes = [] # length of number of packet send, so that tag can discover 10 different neighbors
    list_average_delta_time = [] # list of average of transmission time
    list_average_num_neighbor = [] # list of average of discovered neighbor for each packet send
    list_average_rssi_value = [] # list of avaerage rssi value of each network size
    list_all_trans_time = [] # all of transmission time for first experiment
    list_max_discover_motes = [] # all maximum motes which discovered motes

    dict_netsize_num_neighbor = {} # number of neighbors that heard by tag, dict {networksize: list_num_mote}
    dict_netsize_packet_no = {} # number of packets that are sent to discover 10 motes, dict {network size: list_num_packet}

    dict_netsize_num_neighbor_10 = {} # number of neighbors that heard by tag, dict {networksize: list_num_mote}
    dict_netsize_packet_no_10 = {} # number of packets that are sent to discover 10 motes, dict {network size: list_num_packet}

    dict_mac_key = {} # MAC addresses that are heard by tag and network size {45:[mac1, mac2, mac3], 40:[]}
    dict_netsize_mac_rssi_tmp = {} # temporaty dictionary, {network size: {mote's MAC address: list of rssi value}}
    dict_netsize_mac_rssi = {} # dictionary, {network size: {mote's MAC address: list of rssi value}}
    dict_all_mac_rssi = {} # dictionary of {MAC address: list of rssi value} FOR TEST [POIPOIPOI]
    dict_netsize_rssi = {} # dictionary of {network size: list rssi value}
    dict_netsize_trans_time = {} # dictionary of {network size: list transmission time}
    dict_netsize_num_neighor_for_each_packet = {} # dictionary of {network size: list number of motes}

    # create new folder to save plotted figures

    current_dir = os.getcwd()
    new_dir = current_dir + '\ploted_figure'
    if not os.path.exists(new_dir):
        os.makedirs(new_dir)


#==========================================processing data ======================================
    for netsize in range(begin_size, end_size, size_step):
        num_neighbor = [] # number of discovered neighbor in each packet send
        rssi_value = [] # rssi_value of each discovered neighbors
        list_mac_key = [] # list of mote id and mac address

        data, neighbor, list_num_packet, list_num_mote, dict_mac_rssi = proc_mgr_blink(netsize, False, file_name)
        data, neighbor, list_packet_no_10, list_len_mote_10, dict_mac_rssi = proc_mgr_blink(netsize, True, file_name)

        list_max_discover_motes.append(max(list_num_mote))
        dict_netsize_mac_rssi_tmp.update({netsize:dict_mac_rssi})
        dict_netsize_packet_no.update({netsize:list_num_packet})
        dict_netsize_num_neighbor.update({netsize:list_num_mote})

        dict_netsize_packet_no_10.update({netsize:list_packet_no_10})
        dict_netsize_num_neighbor_10.update({netsize:list_len_mote_10})

        for i in neighbor:
            num_neighbor.append(len(i))
            for j in range(len(i)):
                rssi_value.append(i[j][1]) # get the rssi value

        list_network_size.append(netsize)
        list_average_num_neighbor.append(sta.mean(num_neighbor))
        list_average_delta_time.append(sta.mean(proc_tag_blink(netsize,file_name)))
        list_average_rssi_value.append(sta.mean(rssi_value))
        dict_netsize_trans_time.update({netsize:proc_tag_blink(netsize,file_name)})
        dict_netsize_num_neighor_for_each_packet.update({netsize : num_neighbor})

        list_len_num_packet_discover_10_motes.append(len(dict_netsize_packet_no_10[netsize]))

        # All MACs have RSSI value
        for mac_key in dict_netsize_mac_rssi_tmp[netsize]:
            list_mac_key.append(mac_key)
        dict_mac_key.update({netsize:list_mac_key})

    for time_values in dict_netsize_trans_time.values():
        list_all_trans_time += time_values

#================== changing dict_all_mac_rssi
    dict_netsize_mac_rssi = copy.deepcopy(dict_netsize_mac_rssi_tmp)

    for netsize in range(begin_size, end_size, size_step):
        list_rssi_of_all_mac_for_each_size = []
        for mac in dict_netsize_mac_rssi_tmp[netsize]:

            list_rssi_of_all_mac_for_each_size += dict_netsize_mac_rssi[netsize][mac]
            mac_rssi = dict_netsize_mac_rssi_tmp[netsize][mac]

            if mac in dict_all_mac_rssi:
                dict_all_mac_rssi[mac].extend(mac_rssi) # poipoipoi dict_netsize_mac_rssi_tmp

            else:
                dict_all_mac_rssi.update({mac:mac_rssi}) 

        dict_netsize_rssi.update({netsize:list_rssi_of_all_mac_for_each_size}) 

#====================================== Print data ===========================
    #print'Maximum discovered motes: ', list_max_discover_motes
    #print'Average transmission time: ', list_average_delta_time
    #print'Average neighbors of each packet send: ', list_average_num_neighbor
    #print'Average RSSI value: ', list_average_rssi_value
    #print'Mote ID and MAC address for each network size: ', dict_mac_key
    #print'RSSI value of each network size: ', dict_netsize_rssi

    #print'Transmission time for whole: ', list_all_trans_time

    #print'All netsize:', dict_netsize_rssi
    #print'size_mac:', dict_mac_key
    #print'specific_mac:', dict_all_mac_rssi


#====================================== Below for plotting ===========================
    print 'Wait for plotting...'

# list_num_mote -> dict_netsize_num_neighbor, list_max_discover_motes, 
# plot figure for network size 10 to 45 motes, change 10 discovered motes affect figure 6, 5    

#1, Average transmission time to network size 
    plt.suptitle('Average transmission time for each network size', fontsize = 12)
    plt.xlabel('Network size (motes)', fontsize = 10)
    plt.ylabel('Transmission time(s)', fontsize = 10)

    plt.plot(list_network_size, list_average_delta_time, marker = '.')
    plt.savefig('ploted_figure/1_aver_transmission_time.png')
    plt.show()

#2, Average discovered neighbor of each packet send 
    plt.suptitle('Average number of motes of each packet send for each network size', fontsize = 12)
    plt.xlabel('Network size (motes)', fontsize = 10)
    plt.ylabel('Average number of motes (motes)', fontsize = 10)
    
    plt.plot(list_network_size, list_average_num_neighbor, marker = '.')
    plt.savefig('ploted_figure/2_aver_number_of_neighbor.png')
    plt.show()
    
    
#3, Average RSSI value to network size 
    plt.suptitle('Average of RSSI value for each network size', fontsize = 12)
    plt.xlabel('Network size (motes)', fontsize = 10)
    plt.ylabel('RSSI(dBm)', fontsize = 10)
    
    plt.plot(list_network_size, list_average_rssi_value, marker = '.')
    plt.savefig('ploted_figure/3_average_rssi_value.png')
    plt.show()
    
#4, Maximum number of motes that are discovered for each network size  
    plt.suptitle('Maximum number of discovered motes for each network size', fontsize = 12)
    plt.xlabel('Network size (motes)', fontsize = 10)
    plt.ylabel('Number of discovered motes (motes)', fontsize = 10)
    
    plt.plot(list_network_size, list_max_discover_motes, marker = '.')
    plt.savefig('ploted_figure/4_maximum_number_of_motes.png')
    plt.show()
    
#5, Packets send to discover more than 10 motes for each network size  
    # plot figure for network size 10 to 45 motes, change 10 discovered motes affect figure 6, 5    
    plt.suptitle('Number of discovered motes for each network size until 10 motes', fontsize = 12)
    plt.xlabel('Number of packets send (packets)', fontsize = 10)
    plt.ylabel('Number of discovered motes (motes)', fontsize = 10)
    
    plt.plot(dict_netsize_packet_no_10[10], dict_netsize_num_neighbor_10[10], marker = '.')
    plt.plot(dict_netsize_packet_no_10[15], dict_netsize_num_neighbor_10[15], marker = '.')
    plt.plot(dict_netsize_packet_no_10[20], dict_netsize_num_neighbor_10[20], marker = '.')
    plt.plot(dict_netsize_packet_no_10[25], dict_netsize_num_neighbor_10[25], marker = '.')
    plt.plot(dict_netsize_packet_no_10[30], dict_netsize_num_neighbor_10[30], marker = '.')
    plt.plot(dict_netsize_packet_no_10[35], dict_netsize_num_neighbor_10[35], marker = '.')
    plt.plot(dict_netsize_packet_no_10[40], dict_netsize_num_neighbor_10[40], marker = '.')
    plt.plot(dict_netsize_packet_no_10[45], dict_netsize_num_neighbor_10[45], marker = '.')

    plt.legend(['10', '15','20','25','30','35','40','45'], title = 'Network size', loc = 'lower right')
    plt.savefig('ploted_figure/5_1_number_ofmotes_until_10_motes.png')
    plt.show()

    # plot figure for network size 0 to 45 motes
    plt.suptitle('Number of discovered motes for each network size until 10 motes', fontsize = 12)
    plt.xlabel('Number of packets send (packets)', fontsize = 10)
    plt.ylabel('Number of discovered motes (motes)', fontsize = 10)

    plt.plot(dict_netsize_packet_no_10[0], dict_netsize_num_neighbor_10[0], marker = '.')
    plt.plot(dict_netsize_packet_no_10[5], dict_netsize_num_neighbor_10[5], marker = '.')
    plt.plot(dict_netsize_packet_no_10[10], dict_netsize_num_neighbor_10[10], marker = '.')
    plt.plot(dict_netsize_packet_no_10[15], dict_netsize_num_neighbor_10[15], marker = '.')
    plt.plot(dict_netsize_packet_no_10[20], dict_netsize_num_neighbor_10[20], marker = '.')
    plt.plot(dict_netsize_packet_no_10[25], dict_netsize_num_neighbor_10[25], marker = '.')
    plt.plot(dict_netsize_packet_no_10[30], dict_netsize_num_neighbor_10[30], marker = '.')
    plt.plot(dict_netsize_packet_no_10[35], dict_netsize_num_neighbor_10[35], marker = '.')
    plt.plot(dict_netsize_packet_no_10[40], dict_netsize_num_neighbor_10[40], marker = '.')
    plt.plot(dict_netsize_packet_no_10[45], dict_netsize_num_neighbor_10[45], marker = '.')
    
    plt.legend(['0','5', '10', '15','20','25','30','35','40','45'], title = 'Network size', loc = 'lower right')
    plt.savefig('ploted_figure/5_2_number_ofmotes_until_10_motes.png')
    plt.show()
    #
    # plot multiple diagrams on the same figure
    #== plot for network size from 10 to 25 motes
    plt.suptitle('Number of discovered motes for each network size until 10 motes', fontsize = 10)
    
    plt.subplot(2,2,1)
    plt.ylabel('Number of motes (motes)', fontsize = 8)
    plt.plot(dict_netsize_packet_no_10[10], dict_netsize_num_neighbor_10[10], marker = '.')
    plt.legend(['10 motes'], fontsize = 7)
    
    plt.subplot(2,2,2)
    plt.plot(dict_netsize_packet_no_10[15], dict_netsize_num_neighbor_10[15], marker = '.')
    plt.legend(['15 motes'], fontsize = 7)
    
    plt.subplot(2,2,3)
    plt.xlabel('Number of packets (packets)', fontsize = 8)
    plt.ylabel('Number of motes (motes)', fontsize = 8)
    
    plt.plot(dict_netsize_packet_no_10[20], dict_netsize_num_neighbor_10[20], marker = '.')
    plt.legend(['20 motes'], fontsize = 7)
    
    plt.subplot(2,2,4)
    plt.xlabel('Number of packets (packets)', fontsize = 8)
    plt.plot(dict_netsize_packet_no_10[25], dict_netsize_num_neighbor_10[25], marker = '.')
    plt.legend(['25 motes'], fontsize = 7)
    
    plt.savefig('ploted_figure/5_3_number_of_packets_until_10_motes.png')
    plt.show()
    
    ##== plot for network size from 30 to 45 motes
    plt.suptitle('Number of discovered motes for each network size until 10 motes', fontsize = 10)
    
    plt.subplot(2,2,1)
    plt.ylabel('Number of motes (motes)', fontsize = 8)
    plt.plot(dict_netsize_packet_no_10[30], dict_netsize_num_neighbor_10[30], marker = '.')
    plt.legend(['30 motes'], fontsize = 7)
    
    plt.subplot(2,2,2)
    plt.plot(dict_netsize_packet_no_10[35], dict_netsize_num_neighbor_10[35], marker = '.')
    plt.legend(['35 motes'], fontsize = 7)
    
    plt.subplot(2,2,3)
    plt.xlabel('Number of packets (packets)', fontsize = 8)
    plt.ylabel('Number of motes (motes)', fontsize = 8)
    plt.plot(dict_netsize_packet_no_10[40], dict_netsize_num_neighbor_10[40], marker = '.')
    plt.legend(['40 motes'], fontsize = 7)
    
    plt.subplot(2,2,4)    
    plt.xlabel('Number of packets (packets)', fontsize = 8)
    plt.plot(dict_netsize_packet_no_10[45], dict_netsize_num_neighbor_10[45], marker = '.')
    plt.legend(['45 motes'], fontsize = 7)
    
    plt.savefig('ploted_figure/5_4_number_of_packet_size10_1000.png')
    plt.show()
#6, Maximum number of packets send to make sure tag can discover more than 10 motes for each network size  
    # plot only for network size 10 to 45 motes, discovered 10 motes
    plt.suptitle('Number of packets send to discover 10 motes for each network size', fontsize = 12)
    plt.xlabel('Network size (motes)', fontsize = 10)
    plt.ylabel('Number of packets send (packets)', fontsize = 10)
    
    plt.plot(list_network_size[2:], list_len_num_packet_discover_10_motes[2:], marker = '.')
    plt.savefig('ploted_figure/6_number_of_packets_send_until_10_motes.png')
    plt.show()
    
#7, Number of discovered motes and number of packets send for each network size 
    plt.suptitle('Number of discovered motes for each network size', fontsize = 12)
    plt.xlabel('Number of packets send (packets)', fontsize = 10)
    plt.ylabel('Number of discovered motes (motes)', fontsize = 10)

    plt.plot(dict_netsize_packet_no[0], dict_netsize_num_neighbor[0], marker = '.')
    plt.plot(dict_netsize_packet_no[5], dict_netsize_num_neighbor[5], marker = '.')
    plt.plot(dict_netsize_packet_no[10], dict_netsize_num_neighbor[10], marker = '.')
    plt.plot(dict_netsize_packet_no[15], dict_netsize_num_neighbor[15], marker = '.')
    plt.plot(dict_netsize_packet_no[20], dict_netsize_num_neighbor[20], marker = '.')
    plt.plot(dict_netsize_packet_no[25], dict_netsize_num_neighbor[25], marker = '.')
    plt.plot(dict_netsize_packet_no[30], dict_netsize_num_neighbor[30], marker = '.')
    plt.plot(dict_netsize_packet_no[35], dict_netsize_num_neighbor[35], marker = '.')
    plt.plot(dict_netsize_packet_no[40], dict_netsize_num_neighbor[40], marker = '.')
    plt.plot(dict_netsize_packet_no[45], dict_netsize_num_neighbor[45], marker = '.')
    
    plt.legend(['0','5', '10', '15','20','25','30','35','40','45'], title = 'Network size', loc = 'lower right')
    plt.savefig('ploted_figure/7_number_of_discovered_motes_for_200_packets_send.png')
    plt.show()

#8, Distribution of transmission time for whole experiment 
    # using kdeplot to present the distribution of transmisson time for whole network
    plt.suptitle('Transmission time distribution for whole experiment')
    plt.xlabel('Transmission time (s)')
    plt.ylabel('Ratio', fontsize = 10)

    sns.kdeplot([b for x in dict_netsize_trans_time.values() for b in x], label = 'transmission time')
    plt.savefig('ploted_figure/8_1_transmisson_time_distribution.png')
    plt.show()

    # using hist to present the distribution of transmisson time for whole network
    plt.suptitle('Transmission time distribution for whole experiment')
    plt.xlabel('Transmission time (s)', fontsize = 10)
    plt.ylabel('Packets', fontsize = 10)

    plt.hist([b for x in dict_netsize_trans_time.values() for b in x])
    plt.legend(labels = ['transmission time'], fontsize = 10)
    plt.savefig('ploted_figure/8_2_transmission_time_distribution.png')
    plt.show()
    
#9, #Distribution of transmission time for each network size 
    #== using KDE plot
    plt.suptitle('Transmission time distribution for each network size', fontsize =12)
    plt.xlabel('Transmission time (s)', fontsize = 10)
    plt.ylabel('Ratio', fontsize = 10)

    sns.kdeplot(dict_netsize_trans_time[0], label = '0')
    sns.kdeplot(dict_netsize_trans_time[5], label = '5')
    sns.kdeplot(dict_netsize_trans_time[10], label = '10')
    sns.kdeplot(dict_netsize_trans_time[15], label = '15')
    sns.kdeplot(dict_netsize_trans_time[20], label = '20')
    sns.kdeplot(dict_netsize_trans_time[25], label = '25')
    sns.kdeplot(dict_netsize_trans_time[30], label = '30')
    sns.kdeplot(dict_netsize_trans_time[35], label = '35')
    sns.kdeplot(dict_netsize_trans_time[40], label = '40')
    sns.kdeplot(dict_netsize_trans_time[45], label = '45')

    plt.legend(title = 'Network size')
    plt.savefig('ploted_figure/9_1_transmission_time_distribution.png')
    plt.show()

    #== using hist plot
    plt.suptitle('Transmission time distribution for each network size', fontsize =12)
    plt.xlabel('Transmission time (s)', fontsize = 10)
    plt.ylabel('Packets', fontsize = 10)

    plt.hist(dict_netsize_trans_time[0])
    plt.hist(dict_netsize_trans_time[5])
    plt.hist(dict_netsize_trans_time[10])
    plt.hist(dict_netsize_trans_time[15])
    plt.hist(dict_netsize_trans_time[20])
    plt.hist(dict_netsize_trans_time[25])
    plt.hist(dict_netsize_trans_time[30])
    plt.hist(dict_netsize_trans_time[35])
    plt.hist(dict_netsize_trans_time[40])
    plt.hist(dict_netsize_trans_time[45])

    plt.legend(['0','5', '10', '15','20','25','30','35','40','45'], title = 'Network size', fontsize = 10)
    plt.savefig('ploted_figure/9_2_transmission_time_dsitribution.png')
    plt.show()

#10, Distribution of transmission time for each network size (separately) 
    # using subplot for 2 or 4 diagram
    #=== for num_motes = 0 to 5
    plt.suptitle('Distribution of transmission time of each network size (motes)', fontsize = 10)

    plt.subplot(2,1,1)
    plt.ylabel('Packets', fontsize = 8)
    plt.hist(dict_netsize_trans_time[0])
    plt.legend(['0 mote'], fontsize = 7)

    plt.subplot(2,1,2)
    plt.xlabel('Transmission time (s)', fontsize = 8)
    plt.ylabel('Packets', fontsize = 8)
    plt.hist(dict_netsize_trans_time[5])
    plt.legend(['5 motes'], fontsize = 7)

    plt.savefig('ploted_figure/10_1_transmission_time_distribution.png')
    plt.show()

    #=== for num_motes = 10 to 25
    plt.suptitle('Distribution of transmission time for each network size(motes)', fontsize = 10)
    plt.subplot(2,2,1)
    plt.ylabel('Packets', fontsize = 8)
    plt.hist(dict_netsize_trans_time[10])
    plt.legend(['10 motes'], fontsize = 7)

    plt.subplot(2,2,2)
    plt.hist(dict_netsize_trans_time[15])
    plt.legend(['15 motes'], fontsize = 7)

    plt.subplot(2,2,3)
    plt.xlabel('Transmission time (s)', fontsize = 8)
    plt.ylabel('Packets', fontsize = 8)
    plt.hist(dict_netsize_trans_time[20])
    plt.legend(['20 motes'], fontsize = 7)

    plt.subplot(2,2,4)
    plt.xlabel('Transmission time (s)', fontsize = 8)
    plt.hist(dict_netsize_trans_time[25])
    plt.legend(['25 motes'], fontsize = 7)

    plt.savefig('ploted_figure/10_2_transmission_time_distribution_size_10_25.png')
    plt.show()
    
    #=== for num_motes = 30 to 45
    plt.suptitle('Distribution of transmission time for each network size(motes)', fontsize = 10)
    plt.subplot(2,2,1)
    plt.ylabel('Packets', fontsize = 8)
    plt.hist(dict_netsize_trans_time[30])
    plt.legend(['30 motes'], fontsize = 7)

    plt.subplot(2,2,2)
    plt.hist(dict_netsize_trans_time[35])
    plt.legend(['35 motes'], fontsize = 7)
    
    
    plt.subplot(2,2,3)
    plt.xlabel('Transmission time (s)', fontsize = 8)
    plt.ylabel('Packets', fontsize = 8)
    plt.hist(dict_netsize_trans_time[40])
    plt.legend(['40 motes'], fontsize = 7)

    plt.subplot(2,2,4)
    plt.xlabel('Transmission time (s)', fontsize = 8)
    plt.hist(dict_netsize_trans_time[45])
    plt.legend(['45 motes'], fontsize = 7)

    plt.savefig('ploted_figure/10_3_transmission_time_distribution_size_30_45.png')
    plt.show()
    
    #plot separately each figure
    for netsize in range(begin_size, end_size, size_step):
        plt.suptitle('Transmission time distribution of network size: {}'.format(netsize), fontsize = 12)
        plt.xlabel('Transmssion time (s)', fontsize = 10)
        plt.ylabel('Packets', fontsize = 10)

        plt.hist(dict_netsize_trans_time[netsize])
        plt.legend(['{} motes'.format(netsize)], title = 'Network size', fontsize = 10)
        plt.savefig('ploted_figure/10_size{}_average_transmission_time.png'.format(netsize))
        plt.show()
    
#11, Distribution of RSSI value for whole experiment 
    plt.suptitle('Distribution of RSSI value of whole experiment', fontsize = 12)
    plt.xticks([1], ['All values'], fontsize = 10)
    plt.ylabel('RSSI(dBm)', fontsize = 10)

    plt.boxplot([i for x in dict_netsize_rssi.values() for i in x])
    plt.savefig('ploted_figure/11_RSSI_distribution_whole_experiment.png')
    plt.show()
    
#12, Distribution of RSSI value for each network size 
    # plot all distribution of network size in one figure
    plt.suptitle('Distribution of RSSI value of each network size', fontsize = 12)
    plt.xlabel('Nework size (motes)', fontsize = 10)
    plt.ylabel('RSSI (dBm)', fontsize = 10)
    plt.xticks([1,2,3,4,5,6,7,8,9,10], ['0','5', '10', '15','20','25','30','35','40','45'])

    plt.boxplot([dict_netsize_rssi[netsize] for netsize in range(begin_size, end_size, size_step)])
    plt.savefig('ploted_figure/12_RSS_distribution_for_each_size.png')
    plt.show()

#13, Distribution of RSSI value for each network size (separately) 
    # for network size 0, 5
    plt.subplot(2,1,1)
    labels = [mac[18:] for mac in dict_netsize_mac_rssi[0]]
    plt.xticks(range(1, 1+ len(labels)), labels, rotation = 'vertical', fontsize = 7)
    plt.ylabel('RSSI(dBm)', fontsize = 8)
    plt.boxplot(dict_netsize_mac_rssi[0].values())
    plt.legend(['0'], fontsize = 7)

    plt.subplot(2,1,2)
    labels = [mac[18:] for mac in dict_netsize_mac_rssi[5]]
    plt.suptitle('Distribution of RSSI value for motes of each network size (motes)', fontsize = 10)
    plt.xticks(range(1, 1+ len(labels)), labels, rotation = 'vertical', fontsize = 7)
    plt.ylabel('RSSI(dBm)', fontsize = 8)
    plt.boxplot(dict_netsize_mac_rssi[5].values())
    plt.legend(['5'], fontsize = 7)

    plt.savefig('ploted_figure/13_1_RSSI_distribution_each_size_0_5.png')
    plt.show()
    
    # for network size 10 to 25
    plt.suptitle('Distribution of RSSI value for motes of each network size (motes)', fontsize = 10)
    plt.subplot(2,2,1)
    labels = [mac[18:] for mac in dict_netsize_mac_rssi[10]]
    plt.xticks(range(1, 1+ len(labels)), labels, rotation = 'vertical', fontsize = 7)
    plt.ylabel('RSSI(dBm)', fontsize = 8)
    plt.boxplot(dict_netsize_mac_rssi[10].values())
    plt.legend(['10'], fontsize = 7)
    
    plt.subplot(2,2,2)
    labels = [mac[18:] for mac in dict_netsize_mac_rssi[15]]
    plt.xticks(range(1, 1+ len(labels)), labels, rotation = 'vertical', fontsize = 7)
    plt.boxplot(dict_netsize_mac_rssi[15].values())
    plt.legend(['15'], fontsize = 7)
    
    plt.subplot(2,2,3)
    labels = [mac[18:] for mac in dict_netsize_mac_rssi[20]]
    plt.xticks(range(1, 1+ len(labels)), labels, rotation = 'vertical', fontsize = 7)
    plt.ylabel('RSSI(dBm)', fontsize = 8)
    plt.boxplot(dict_netsize_mac_rssi[20].values())
    plt.legend(['20'], fontsize = 7)
    
    plt.subplot(2,2,4)
    labels = [mac[18:] for mac in dict_netsize_mac_rssi[25]]
    plt.xticks(range(1, 1+ len(labels)), labels, rotation = 'vertical', fontsize = 7)
    plt.boxplot(dict_netsize_mac_rssi[25].values())
    plt.legend(['25'], fontsize = 7)
    
    plt.savefig('ploted_figure/13_2_RSSI_distribution_size_10_25.png')
    plt.show()
    
    # for network size 30 to 45
    plt.suptitle('Distribution of RSSI value for motes of each network size (motes)', fontsize = 10)
    plt.subplot(2,2,1)
    labels = [mac[18:] for mac in dict_netsize_mac_rssi[30]]
    plt.xticks(range(1, 1+ len(labels)), labels, rotation = 'vertical', fontsize = 7)
    plt.ylabel('RSSI(dBm)', fontsize = 8)
    plt.boxplot(dict_netsize_mac_rssi[30].values())
    plt.legend(['30'], fontsize = 7)

    plt.subplot(2,2,2)
    labels = [mac[18:] for mac in dict_netsize_mac_rssi[35]]
    plt.xticks(range(1, 1+ len(labels)), labels, rotation = 'vertical', fontsize = 7)
    plt.boxplot(dict_netsize_mac_rssi[35].values())
    plt.legend(['35'], fontsize = 7)

    plt.subplot(2,2,3)
    labels = [mac[18:] for mac in dict_netsize_mac_rssi[40]]
    plt.xticks(range(1, 1+ len(labels)), labels, rotation = 'vertical', fontsize = 7)
    plt.ylabel('RSSI(dBm)', fontsize = 8)
    plt.boxplot(dict_netsize_mac_rssi[40].values())
    plt.legend(['40'], fontsize = 7)

    plt.subplot(2,2,4)
    labels = [mac[18:] for mac in dict_netsize_mac_rssi[45]]
    plt.xticks(range(1, 1+ len(labels)), labels, rotation = 'vertical', fontsize = 7)
    plt.boxplot(dict_netsize_mac_rssi[45].values())
    plt.legend(['45'], fontsize = 7)

    plt.savefig('ploted_figure/13_3_RSSI_distribution_size_30_45.png')
    plt.show()

    # boxplot for each network size
    for networksize in range(begin_size, end_size, size_step):
        plt.suptitle('Distribution of RSSI value for motes of network size: {}'.format(networksize), fontsize = 12)
        labels = [label[18:] for label in dict_netsize_mac_rssi[networksize]]
        plt.xticks(range(1, 1+len(labels)), labels, rotation = 'vertical', fontsize = 9)
        plt.ylabel('RSSI (dBm)', fontsize = 10)
        plt.boxplot(dict_netsize_mac_rssi[networksize].values())

        plt.savefig('ploted_figure/13_size{}_RSSI_dis_for_motes_size.png'.format(networksize))
        plt.show()

#14, Distribution of RSSI value for specific MAC address 

    # plot distribution of RSSI value of all motes
    plt.suptitle('RSSI value distribution of all motes', fontsize = 12)
    labels = [label[18:] for label in dict_all_mac_rssi]
    plt.xticks(range(1, 1+len(labels)), labels, rotation = 'vertical', fontsize = 8)
    plt.ylabel('RSSI(dBm)', fontsize = 10)
    
    plt.boxplot([b for b in dict_all_mac_rssi.values()])
    plt.savefig('ploted_figure/14_1_RSSI_dis_MAC.png')
    plt.show()

    # plot distribution of RSSI value for manager
    plt.suptitle('RSSI value distribution of manager', fontsize = 12)
    plt.xticks([1], ['3b-ff'], rotation = 'vertical', fontsize = 9)
    plt.ylabel('RSSI(dBm)', fontsize = 10)
    
    plt.boxplot(dict_all_mac_rssi['00-17-0d-00-00-30-3b-ff'])
    plt.savefig('ploted_figure/14_2_RSSI_dis_manager.png')
    plt.show()

    # plot distribution of RSSI value of all motes that have more than 1000 RSSI value
    plt.suptitle('RSSI value distribution of motes that have more than 1000 RSSI values', fontsize = 12)
    labels = [mac[18:] for mac in dict_all_mac_rssi if len(dict_all_mac_rssi[mac]) > 1000]
    plt.xticks(range(1, 1+len(labels)), labels, rotation = 'vertical', fontsize = 9)
    plt.ylabel('RSSI(dBm)', fontsize = 10)

    plt.boxplot([rssi_list for rssi_list in dict_all_mac_rssi.values() if len(rssi_list) > 1000])
    plt.savefig('ploted_figure/14_3_RSSI_dis_more_1000_values.png')
    plt.show()

    # plot distribution of RSSI value of all motes that have more than 500 RSSI value
    plt.suptitle('RSSI value distribution of motes that have more than 500 RSSI values', fontsize = 12)
    labels = [mac[18:] for mac in dict_all_mac_rssi if len(dict_all_mac_rssi[mac]) > 500]
    plt.xticks(range(1, 1+len(labels)), labels, rotation = 'vertical', fontsize = 9)
    plt.ylabel('RSSI(dBm)', fontsize = 10)
    
    plt.boxplot([rssi_list for rssi_list in dict_all_mac_rssi.values() if len(rssi_list) > 500])
    plt.savefig('ploted_figure/14_4_RSSI_dis_more_500_values.png')
    plt.show()
    
    # plot distribution of RSSI value of all motes that have more than 200 RSSI value
    plt.suptitle('RSSI value distribution of motes that have more than 200 RSSI values', fontsize = 12)
    labels = [mac[18:] for mac in dict_all_mac_rssi if len(dict_all_mac_rssi[mac]) > 200]
    plt.xticks(range(1, 1+len(labels)), labels, rotation = 'vertical', fontsize = 9)
    plt.ylabel('RSSI(dBm)', fontsize = 10)
    
    plt.boxplot([rssi_list for rssi_list in dict_all_mac_rssi.values() if len(rssi_list) > 200])
    plt.savefig('ploted_figure/14_5_RSSI_dis_more_200_values.png')
    plt.show()
    
    # plot distribution of RSSI value of all motes that have less than 200 RSSI value
    plt.suptitle('RSSI value distribution of motes that have less than 200 RSSI values', fontsize = 12)
    labels = [mac[18:] for mac in dict_all_mac_rssi if len(dict_all_mac_rssi[mac]) <= 200]
    plt.xticks(range(1, 1+len(labels)), labels, rotation = 'vertical', fontsize = 9)
    plt.ylabel('RSSI(dBm)', fontsize = 10)
    
    plt.boxplot([rssi_list for rssi_list in dict_all_mac_rssi.values() if len(rssi_list) <= 200])
    plt.savefig('ploted_figure/14_6_RSSI_dis_less_200_values.png')
    plt.show()
    

#15, Distribution of number of discovered neighbors for each packet send 
    plt.suptitle('Distribution of number of discovered neighbors for each packet send', fontsize = 12)
    plt.xlabel('Network size (motes)', fontsize = 10)
    plt.ylabel('Number of discovered neighbors (motes)', fontsize = 10)
    plt.xticks([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], ['0', '5', '10', '15', '20', '25', '30', '35', '40', '45'])
    
    plt.boxplot([dict_netsize_num_neighor_for_each_packet[netsize] for netsize in range(begin_size, end_size, size_step)])
    plt.savefig('ploted_figure/15_discovered_number_dis_per_packet.png')
    plt.show()

#function will get all MAC address and mote IDs for each network size experiment
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

        # moteid_mac = {0:{}, 5:{}, 10:{}, 15:{}, 20:{}, 25:{}}
        for msg_size in list_msg_networksize:
            if msg_size['msg']['networksize'] == netsize:
                time_stamp[netsize] = msg_size['timestamp']

    for netsize in range(begin_size, end_size, size_step):
        moteid_mac.update({netsize:{}}) # create moteid_mac dictionary with netsize keys

        if netsize != begin_size:
            for msg_mote in list_cmd_getmoteconfig:

                if time_stamp[netsize] < msg_mote['timestamp'] < time_stamp[netsize-size_step]:
                    moteid_mac[netsize].update({msg_mote['msg']['res'][2]:'-'.join(['%02x'%b for b in msg_mote['msg']['res'][1]])})
        else:
            for msg_mote in list_cmd_getmoteconfig:
                if time_stamp[netsize] < msg_mote['timestamp']:
                    moteid_mac[netsize].update({msg_mote['msg']['res'][2]:'-'.join(['%02x'%b for b in msg_mote['msg']['res'][1]])})

    return moteid_mac

#============================ main ============================================
def main():
    #plot_experiment(0, 46, 5, 'blinkLab_final.txt')
    proc_mgr_blink_mote('blinkLab_final.txt')
    raw_input('Press enter to finish')
if __name__=="__main__":
    main()



