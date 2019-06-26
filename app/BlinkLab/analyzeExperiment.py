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
def proc_mgr_blink(networksize, discover_10, file_name): # OK

    list_neighbor = []
    list_netsize = []
    list_payload = []

    list_packet_no = [] # list of number of packets send
    list_len_mote = [] # list of number of motes

    set_moteid = set() # set of different mote id

    packet_no = 0
    interrupt_list = 0

    dict_mac_rssi = {}

    # blink_neighbor = [[(1, -17), (11, -17), (9, -21), (10, -25)], [(9, -21), (10, -25)]]

    list_notif_blink_mgr = get_blink_notif_mgr(get_msg_type(file_name,'NOTIF')) #list all blink notif mgr

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
            if discover_10:
                if not interrupt_list:
                    list_len_mote.append(len(set_moteid))
                    list_packet_no.append(packet_no)

                if len(set_moteid) >= 10: # number of packets send to, so tag can hear 10 different motes
                    interrupt_list += 1
            else:
                list_len_mote.append(len(set_moteid))
                list_packet_no.append(packet_no)
                

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

    list_network_size = [] # all network size from 0 to 45
    list_len_num_packet_discover_10_motes = [] # length of number of packet send, so that tag can discover 10 different neighbors
    list_average_delta_time = [] # list of average of transmission time
    list_average_num_neighbor = [] # list of average of discovered neighbor for each packet send
    list_average_rssi_value = [] # list of avaerage rssi value of each network size
    list_rssi_of_all_mac = [] # all of RSSI value (total rssi of all mac address) of the 1st experiment
    list_trans_time_all = [] # all of transmission time for first experiment
    len_mote_max = [] # all maximum motes which discovered motes

    dict_len_mote = {} # number of neighbors that heard by tag, dict {networksize: list_len_mote}
    dict_packet_no = {} # number of packets that are sent to discover 10 motes, dict {network size: list_packet_no}
    
    dict_len_mote_10 = {} # number of neighbors that heard by tag, dict {networksize: list_len_mote}
    dict_packet_no_10 = {} # number of packets that are sent to discover 10 motes, dict {network size: list_packet_no}
    
    
    dict_mac_key = {} # MAC addresses that are heard by tag and network size {45:[mac1, mac2, mac3], 40:[]}
    dict_netsize_mote_rssi = {} # dictionary, {network size: {mote's MAC address: list of rssi value}}
    dict_rssi_of_spec_mac = {} # dictionary of {MAC address: list of rssi value}
    dict_rssi_of_all_mac_for_each_size = {} # dictionary of {network size: list rssi value}
    dict_trans_time_for_each_size = {} # dictionary of {network size: list transmission time}
    dict_num_neighor_for_each_packet_each_size = {} # dictionary of {network size: list number of motes}
    
    # create new folder to save plotted figures

    current_dir = os.getcwd()
    new_dir = current_dir + '\ploted_figure'
    if not os.path.exists(new_dir):
        os.makedirs(new_dir)

#==========================================processing datat ======================================
    for netsize in range(begin_size, end_size, size_step):
        num_neighbor = [] # number of discovered neighbor in each packet send
        rssi_value = [] # rssi_value of each discovered neighbors
        list_mac_key = [] # list of mote id and mac address

        data, neighbor, list_packet_no, list_len_mote, dict_mac_rssi = proc_mgr_blink(netsize, False, file_name)
        data, neighbor, list_packet_no_10, list_len_mote_10, dict_mac_rssi = proc_mgr_blink(netsize, True, file_name)

        dict_netsize_mote_rssi.update({netsize:dict_mac_rssi})
        dict_len_mote.update({netsize:list_len_mote})
        len_mote_max.append(max(list_len_mote))
        dict_packet_no.update({netsize:list_packet_no})
        
        dict_packet_no_10.update({netsize:list_packet_no_10})
        dict_len_mote_10.update({netsize:list_len_mote_10})

        for i in neighbor:
            num_neighbor.append(len(i))
            for j in range(len(i)):
                rssi_value.append(i[j][1]) # get the rssi value

        list_network_size.append(netsize)
        list_average_num_neighbor.append(sta.mean(num_neighbor))
        list_average_delta_time.append(sta.mean(proc_tag_blink(netsize,file_name)))
        list_average_rssi_value.append(sta.mean(rssi_value))
        dict_trans_time_for_each_size.update({netsize:proc_tag_blink(netsize,file_name)})
        dict_num_neighor_for_each_packet_each_size.update({netsize : num_neighbor})

        list_len_num_packet_discover_10_motes.append(len(dict_packet_no_10[netsize]))

        # All MACs have RSSI value
        for mac_key in dict_netsize_mote_rssi[netsize]:
            list_mac_key.append(mac_key)
        dict_mac_key.update({netsize:list_mac_key})

        #plt.plot(list_packet_no, list_len_mote, marker='.') # number of packets send and discovered neighbors
    for i in dict_trans_time_for_each_size.values():
        list_trans_time_all += i

    for i in range(begin_size, end_size, size_step):
        list_rssi_of_all_mac_for_each_size = []
        for mac in dict_mac_key[i]:

            list_rssi_of_all_mac += dict_netsize_mote_rssi[i][mac]
            list_rssi_of_all_mac_for_each_size += dict_netsize_mote_rssi[i][mac]
            if mac in dict_rssi_of_spec_mac:
                dict_rssi_of_spec_mac[mac] += dict_netsize_mote_rssi[i][mac]
            else:
                dict_rssi_of_spec_mac.update({mac:dict_netsize_mote_rssi[i][mac]})
        dict_rssi_of_all_mac_for_each_size.update({i:list_rssi_of_all_mac_for_each_size})

#====================================== Print data ===========================
    #print'Maximum discovered motes: ', len_mote_max
    #print'Average transmission time: ', list_average_delta_time
    #print'Average neighbors of each packet send: ', list_average_num_neighbor
    #print'Average RSSI value: ', list_average_rssi_value
    #print'Mote ID and MAC address for each network size: ', dict_mac_key
    #print'RSSI value of each network size: ', dict_rssi_of_all_mac_for_each_size

    print'Transmission time for whole: ', list_trans_time_all
    
#====================================== Below for plotting ===========================
    print 'Wait for plotting...'

# list_len_mote -> dict_len_mote, len_mote_max, 

#1, Average transmission time to network size
    plt.plot(list_network_size, list_average_delta_time, marker = '.')
    plt.suptitle('Average transmission time for each network size', fontsize = 12)
    plt.xlabel('Network size (motes)', fontsize = 10)
    plt.ylabel('Transmission time(s)', fontsize = 10)
    
    plt.savefig('ploted_figure/1_aver_transmission_time.png')
    plt.show()
    
    
#2, Average discovered neighbor of each packet send [OK]
    plt.plot(list_network_size, list_average_num_neighbor, marker = '.')
    plt.suptitle('Average number of motes of each packet send for each network size', fontsize = 12)
    plt.xlabel('Network size (motes)', fontsize = 10)
    plt.ylabel('Average number of motes (motes)', fontsize = 10)
    
    plt.savefig('ploted_figure/2_aver_number_of_neighbor.png')
    plt.show()
    
    
#3, Average RSSI value to network size [OK]
    plt.plot(list_network_size, list_average_rssi_value, marker = '.')
    plt.suptitle('Average of RSSI value for each network size', fontsize = 12)
    plt.xlabel('Network size (motes)', fontsize = 10)
    plt.ylabel('RSSI(dBm)', fontsize = 10)
    
    plt.savefig('ploted_figure/3_average_rssi_value.png')
    plt.show()
    
#4, Maximum number of motes that are discovered for each network size [OK] 
    plt.plot(list_network_size, len_mote_max, marker = '.')
    plt.suptitle('Maximum number of discovered motes for each network size', fontsize = 12)
    plt.xlabel('Network size (motes)', fontsize = 10)
    plt.ylabel('Number of discovered motes (motes)', fontsize = 10)
    
    plt.savefig('ploted_figure/4_maximum_number_of_motes.png')
    plt.show()
    
#5, Packets send to discover more than 10 motes for each network size [OK] 
    # plot figure for network size 10 to 45 motes, change 10 discovered motes affect figure 6, 5    
    plt.plot(dict_packet_no_10[10], dict_len_mote_10[10], marker = '.')
    plt.plot(dict_packet_no_10[15], dict_len_mote_10[15], marker = '.')
    plt.plot(dict_packet_no_10[20], dict_len_mote_10[20], marker = '.')
    plt.plot(dict_packet_no_10[25], dict_len_mote_10[25], marker = '.')
    plt.plot(dict_packet_no_10[30], dict_len_mote_10[30], marker = '.')
    plt.plot(dict_packet_no_10[35], dict_len_mote_10[35], marker = '.')
    plt.plot(dict_packet_no_10[40], dict_len_mote_10[40], marker = '.')
    plt.plot(dict_packet_no_10[45], dict_len_mote_10[45], marker = '.')
    
    
    plt.suptitle('Number of discovered motes for each network size until 10 motes', fontsize = 12)
    plt.xlabel('Number of packets send (packets)', fontsize = 10)
    plt.ylabel('Number of discovered motes (motes)', fontsize = 10)
    
    plt.legend(['10', '15','20','25','30','35','40','45'], title = 'Network size', loc = 'lower right')
    
    plt.savefig('ploted_figure/5_1_number_ofmotes_until_10_motes.png')
    plt.show()
    
    # plot figure for network size 0 to 45 motes
    plt.plot(dict_packet_no_10[0], dict_len_mote_10[0], marker = '.')
    plt.plot(dict_packet_no_10[5], dict_len_mote_10[5], marker = '.')
    plt.plot(dict_packet_no_10[10], dict_len_mote_10[10], marker = '.')
    plt.plot(dict_packet_no_10[15], dict_len_mote_10[15], marker = '.')
    plt.plot(dict_packet_no_10[20], dict_len_mote_10[20], marker = '.')
    plt.plot(dict_packet_no_10[25], dict_len_mote_10[25], marker = '.')
    plt.plot(dict_packet_no_10[30], dict_len_mote_10[30], marker = '.')
    plt.plot(dict_packet_no_10[35], dict_len_mote_10[35], marker = '.')
    plt.plot(dict_packet_no_10[40], dict_len_mote_10[40], marker = '.')
    plt.plot(dict_packet_no_10[45], dict_len_mote_10[45], marker = '.')
    
    plt.suptitle('Number of discovered motes for each network size until 10 motes', fontsize = 12)
    plt.xlabel('Number of packets send (packets)', fontsize = 10)
    plt.ylabel('Number of discovered motes (motes)', fontsize = 10)
    
    plt.legend(['0','5', '10', '15','20','25','30','35','40','45'], title = 'Network size', loc = 'lower right')
    plt.savefig('ploted_figure/5_2_number_ofmotes_until_10_motes.png')
    plt.show()
    #
    # plot multiple diagrams on the same figure
    #== plot for network size from 10 to 25 motes
    plt.subplot(2,2,1)
    plt.plot(dict_packet_no_10[10], dict_len_mote_10[10], marker = '.')
    #plt.xlabel('')
    plt.ylabel('Number of motes (motes)', fontsize = 8)
    plt.legend(['10 motes'], fontsize = 7)
    
    plt.subplot(2,2,2)
    plt.plot(dict_packet_no_10[15], dict_len_mote_10[15], marker = '.')
    #plt.xlabel('')
    #plt.ylabel('Number of motes (motes)', fontsize = 8)
    plt.legend(['15 motes'], fontsize = 7)
    
    plt.subplot(2,2,3)
    plt.plot(dict_packet_no_10[20], dict_len_mote_10[20], marker = '.')
    plt.xlabel('Number of packets (packets)', fontsize = 8)
    plt.ylabel('Number of motes (motes)', fontsize = 8)
    plt.legend(['20 motes'], fontsize = 7)
    
    
    plt.subplot(2,2,4)
    plt.plot(dict_packet_no_10[25], dict_len_mote_10[25], marker = '.')
    plt.xlabel('Number of packets (packets)', fontsize = 8)
    #plt.ylabel('Number of motes (motes)', fontsize = 8)
    plt.legend(['25 motes'], fontsize = 7)
    
    plt.suptitle('Number of discovered motes for each network size until 10 motes', fontsize = 10)
    plt.savefig('ploted_figure/5_3_number_of_packets_until_10_motes.png')
    plt.show()
    
    ##== plot for network size from 30 to 45 motes
    plt.subplot(2,2,1)
    plt.plot(dict_packet_no_10[30], dict_len_mote_10[30], marker = '.')
    #plt.xlabel('')
    plt.ylabel('Number of motes (motes)', fontsize = 8)
    plt.legend(['30 motes'], fontsize = 7)
    
    plt.subplot(2,2,2)
    plt.plot(dict_packet_no_10[35], dict_len_mote_10[35], marker = '.')
    #plt.xlabel('')
    #plt.ylabel('Number of motes (motes)', fontsize = 8)
    plt.legend(['35 motes'], fontsize = 7)
    
    plt.subplot(2,2,3)
    plt.plot(dict_packet_no_10[40], dict_len_mote_10[40], marker = '.')
    plt.xlabel('Number of packets (packets)', fontsize = 8)
    plt.ylabel('Number of motes (motes)', fontsize = 8)
    plt.legend(['40 motes'], fontsize = 7)
    
    plt.subplot(2,2,4)    
    plt.plot(dict_packet_no_10[45], dict_len_mote_10[45], marker = '.')
    plt.xlabel('Number of packets (packets)', fontsize = 8)
    #plt.ylabel('Number of motes (motes)', fontsize = 8)
    plt.legend(['45 motes'], fontsize = 7)
    
    plt.suptitle('Number of discovered motes for each network size until 10 motes', fontsize = 10)
    plt.savefig('ploted_figure/5_4_number_of_packet_size10_1000.png')
    plt.show()
#6, Maximum number of packets send to make sure tag can discover more than 10 motes for each network size [OK] 
    # plot only for network size 10 to 45 motes, discovered 10 motes
    
    plt.plot(list_network_size[2:], list_len_num_packet_discover_10_motes[2:], marker = '.')
    plt.suptitle('Number of packets send to discover 10 motes for each network size', fontsize = 12)
    plt.xlabel('Network size (mote)', fontsize = 10)
    plt.ylabel('Number of packets send (packets)', fontsize = 10)
    
    plt.savefig('ploted_figure/6_number_of_packets_send_until_10_motes.png')
    plt.show()
    
#7, Number of discovered motes and number of packets send for each network size [OK] - anh huong
    plt.plot(dict_packet_no[0], dict_len_mote[0], marker = '.')
    plt.plot(dict_packet_no[5], dict_len_mote[5], marker = '.')
    plt.plot(dict_packet_no[10], dict_len_mote[10], marker = '.')
    plt.plot(dict_packet_no[15], dict_len_mote[15], marker = '.')
    plt.plot(dict_packet_no[20], dict_len_mote[20], marker = '.')
    plt.plot(dict_packet_no[25], dict_len_mote[25], marker = '.')
    plt.plot(dict_packet_no[30], dict_len_mote[30], marker = '.')
    plt.plot(dict_packet_no[35], dict_len_mote[35], marker = '.')
    plt.plot(dict_packet_no[40], dict_len_mote[40], marker = '.')
    plt.plot(dict_packet_no[45], dict_len_mote[45], marker = '.')
    
    
    plt.suptitle('Number of discovered motes for each network size', fontsize = 12)
    plt.xlabel('Number of packets send (packets)', fontsize = 10)
    plt.ylabel('Number of discovered motes (motes)', fontsize = 10)
    
    plt.legend(['0','5', '10', '15','20','25','30','35','40','45'], title = 'Network size', loc = 'lower right')
    plt.savefig('ploted_figure/7_number_of_discovered_motes_for_200_packets_send.png')
    plt.show()
    
    
    
#8, Distribution of transmission time for whole experiment [half OK, check sns.kdeplot legend]
    # using kdeplot to present the distribution of transmisson time for whole network
    sns.kdeplot([b for x in dict_trans_time_for_each_size.values() for b in x], label = 'transmission time')
    plt.suptitle('Transmission time distribution for whole experiment')
    plt.xlabel('Transmission time (s)')
    plt.ylabel('Ratio', fontsize = 10)

    
    plt.savefig('ploted_figure/8_1_transmisson_time_distribution.png')
    plt.show()
    
    # using hist to present the distribution of transmisson time for whole network
    plt.hist([b for x in dict_trans_time_for_each_size.values() for b in x])
    plt.suptitle('Transmission time distribution for whole experiment')
    plt.xlabel('Transmission time (s)', fontsize = 10)
    plt.ylabel('Packets', fontsize = 10)
    
    plt.legend(labels = ['transmission time'], fontsize = 10)
    
    plt.savefig('ploted_figure/8_2_transmission_time_distribution.png')
    plt.show()
    
#9, #Distribution of transmission time for each network size [half OK]
    #== using KDE plot
    sns.kdeplot(dict_trans_time_for_each_size[0], label = '0')
    sns.kdeplot(dict_trans_time_for_each_size[5], label = '5')
    sns.kdeplot(dict_trans_time_for_each_size[10], label = '10')
    sns.kdeplot(dict_trans_time_for_each_size[15], label = '15')
    sns.kdeplot(dict_trans_time_for_each_size[20], label = '20')
    sns.kdeplot(dict_trans_time_for_each_size[25], label = '25')
    sns.kdeplot(dict_trans_time_for_each_size[30], label = '30')
    sns.kdeplot(dict_trans_time_for_each_size[35], label = '35')
    sns.kdeplot(dict_trans_time_for_each_size[40], label = '40')
    sns.kdeplot(dict_trans_time_for_each_size[45], label = '45')
    
    plt.suptitle('Transmission time distribution for each network size', fontsize =12)
    plt.xlabel('Transmission time (s)', fontsize = 10)
    plt.ylabel('Ratio', fontsize = 10)
    plt.legend(title = 'Network size')

    plt.savefig('ploted_figure/9_1_transmission_time_distribution.png')
    plt.show()
    
    
    #== using hist plot
    plt.hist(dict_trans_time_for_each_size[0])
    plt.hist(dict_trans_time_for_each_size[5])
    plt.hist(dict_trans_time_for_each_size[10])
    plt.hist(dict_trans_time_for_each_size[15])
    plt.hist(dict_trans_time_for_each_size[20])
    plt.hist(dict_trans_time_for_each_size[25])
    plt.hist(dict_trans_time_for_each_size[30])
    plt.hist(dict_trans_time_for_each_size[35])
    plt.hist(dict_trans_time_for_each_size[40])
    plt.hist(dict_trans_time_for_each_size[45])
    
    plt.suptitle('Transmission time distribution for each network size', fontsize =12)
    plt.xlabel('Transmission time (s)', fontsize = 10)
    plt.ylabel('Packets', fontsize = 10)
    plt.legend(['0','5', '10', '15','20','25','30','35','40','45'], title = 'Network size', fontsize = 10)
    #plt.xticks([1,2,3,4,5,6,7,8,9,10], ['0','5', '10', '15','20','25','30','35','40','45'])
    
    plt.savefig('ploted_figure/9_2_transmission_time_dsitribution.png')
    plt.show()
    
#10, Distribution of transmission time for each network size (separately) [OK]
    # using subplot for 2 or 4 diagram
    #=== for num_motes = 0 to 5
    plt.subplot(2,1,1)
    plt.hist(dict_trans_time_for_each_size[0])
    plt.ylabel('Packets', fontsize = 8)
    plt.legend(['0 mote'], fontsize = 7)
    
    plt.subplot(2,1,2)
    plt.hist(dict_trans_time_for_each_size[5])
    plt.xlabel('Transmission time (s)', fontsize = 8)
    plt.ylabel('Packets', fontsize = 8)
    plt.legend(['5 motes'], fontsize = 7)
    
    plt.suptitle('Distribution of transmission time of each network size (motes)', fontsize = 10)
    plt.savefig('ploted_figure/10_1_transmission_time_distribution.png')
    plt.show()
    
    #=== for num_motes = 10 to 25
    plt.subplot(2,2,1)
    plt.hist(dict_trans_time_for_each_size[10])
    plt.ylabel('Packets', fontsize = 8)
    plt.legend(['10 motes'], fontsize = 7)
    
    plt.subplot(2,2,2)
    plt.hist(dict_trans_time_for_each_size[15])
    plt.legend(['15 motes'], fontsize = 7)
    
    
    plt.subplot(2,2,3)
    plt.hist(dict_trans_time_for_each_size[20])
    plt.xlabel('Transmission time (s)', fontsize = 8)
    plt.ylabel('Packets', fontsize = 8)
    plt.legend(['20 motes'], fontsize = 7)
    
    
    plt.subplot(2,2,4)
    plt.hist(dict_trans_time_for_each_size[25])
    plt.xlabel('Transmission time (s)', fontsize = 8)
    plt.legend(['25 motes'], fontsize = 7)
    
    plt.suptitle('Distribution of transmission time for each network size(motes)', fontsize = 10)
    
    plt.savefig('ploted_figure/10_2_transmission_time_distribution_size_10_25.png')
    plt.show()
    
    #=== for num_motes = 30 to 45
    plt.subplot(2,2,1)
    plt.hist(dict_trans_time_for_each_size[30])
    plt.ylabel('Packets', fontsize = 8)
    plt.legend(['30 motes'], fontsize = 7)
    
    plt.subplot(2,2,2)
    plt.hist(dict_trans_time_for_each_size[35])
    plt.legend(['35 motes'], fontsize = 7)
    
    
    plt.subplot(2,2,3)
    plt.hist(dict_trans_time_for_each_size[40])
    plt.xlabel('Transmission time (s)', fontsize = 8)
    plt.ylabel('Packets', fontsize = 8)
    plt.legend(['40 motes'], fontsize = 7)
    
    
    plt.subplot(2,2,4)
    plt.hist(dict_trans_time_for_each_size[45])
    plt.xlabel('Transmission time (s)', fontsize = 8)
    plt.legend(['45 motes'], fontsize = 7)
    
    plt.suptitle('Distribution of transmission time for each network size(motes)', fontsize = 10)
    plt.savefig('ploted_figure/10_3_transmission_time_distribution_size_30_45.png')
    plt.show()
    
    #plot separately each figure
    for netsize in range(begin_size, end_size, size_step):
        plt.hist(dict_trans_time_for_each_size[netsize])
        plt.suptitle('Transmission time distribution of network size: {}'.format(netsize), fontsize = 12)
        plt.xlabel('Transmssion time (s)', fontsize = 10)
        plt.ylabel('Packets', fontsize = 10)
        plt.legend(['{} motes'.format(netsize)], title = 'Network size', fontsize = 10)
        
        plt.savefig('ploted_figure/10_size{}_average_transmission_time.png'.format(netsize))
        plt.show()
    
#11, Distribution of RSSI value for whole experiment [OK]
    plt.boxplot([i for x in dict_rssi_of_all_mac_for_each_size.values() for i in x])
    plt.suptitle('Distribution of RSSI value of whole experiment', fontsize = 12)
    plt.xlabel('All value', fontsize = 10)
    plt.ylabel('RSSI(dBm)', fontsize = 10)
    
    plt.savefig('ploted_figure/11_RSSI_distribution_whole_experiment.png')
    plt.show()
    
    
    
#12, Distribution of RSSI value for each network size [OK]
    # plot all distribution of network size in one figure
    
    plt.boxplot([dict_rssi_of_all_mac_for_each_size[netsize] for netsize in range(begin_size, end_size, size_step)])
    plt.suptitle('Distribution of RSSI value of each network size', fontsize = 12)
    
    plt.xlabel('Nework size (motes)', fontsize = 10)
    plt.ylabel('RSSI (dBm)', fontsize = 10)
    plt.xticks([1,2,3,4,5,6,7,8,9,10], ['0','5', '10', '15','20','25','30','35','40','45'])
    
    plt.savefig('ploted_figure/12_RSS_distribution_for_each_size.png')
    plt.show()
    
    
    
    
    
#13, Distribution of RSSI value for each network size (separately) [OK]
    # for network size 0, 5
    plt.subplot(2,1,1)
    plt.boxplot(dict_netsize_mote_rssi[0].values())
    plt.ylabel('RSSI(dBm)', fontsize = 8)
    plt.legend(['0'], fontsize = 7)
    
    plt.subplot(2,1,2)
    plt.boxplot(dict_netsize_mote_rssi[5].values())
    plt.suptitle('Distribution of RSSI value for mote of each network size (motes)', fontsize = 10)
    plt.legend(['5'], fontsize = 7)
    plt.xlabel('Motes', fontsize = 8)
    plt.ylabel('RSSI(dBm)', fontsize = 8)
    
    plt.savefig('ploted_figure/13_1_RSSI_distribution_each_size_0_5.png')
    plt.show()
    
    # for network size 10 to 25
    plt.subplot(2,2,1)
    plt.boxplot(dict_netsize_mote_rssi[10].values())
    plt.ylabel('RSSI(dBm)', fontsize = 8)
    plt.legend(['10'], fontsize = 7)
    
    plt.subplot(2,2,2)
    plt.boxplot(dict_netsize_mote_rssi[15].values())
    plt.legend(['15'], fontsize = 7)
    
    plt.subplot(2,2,3)
    plt.boxplot(dict_netsize_mote_rssi[20].values())
    plt.legend(['20'], fontsize = 7)
    plt.xlabel('Motes', fontsize = 8)
    plt.ylabel('RSSI(dBm)', fontsize = 8)
    
    
    plt.subplot(2,2,4)
    plt.boxplot(dict_netsize_mote_rssi[25].values())
    plt.suptitle('Distribution of RSSI value for mote of each network size (motes)', fontsize = 10)
    plt.xlabel('Motes', fontsize = 8)
    plt.legend(['25'], fontsize = 7)
    
    plt.savefig('ploted_figure/13_2_RSSI_distribution_size_10_25.png')
    plt.show()
    
    # for network size 30 to 45
    plt.subplot(2,2,1)
    plt.boxplot(dict_netsize_mote_rssi[30].values())
    plt.ylabel('RSSI(dBm)', fontsize = 8)
    plt.legend(['30'], fontsize = 7)
    
    plt.subplot(2,2,2)
    plt.boxplot(dict_netsize_mote_rssi[35].values())
    plt.legend(['35'], fontsize = 7)
    
    plt.subplot(2,2,3)
    plt.boxplot(dict_netsize_mote_rssi[40].values())
    plt.xlabel('Motes', fontsize = 8)
    plt.ylabel('RSSI(dBm)', fontsize = 8)
    plt.legend(['40'], fontsize = 7)
    
    plt.subplot(2,2,4)
    plt.boxplot(dict_netsize_mote_rssi[45].values())
    plt.suptitle('Distribution of RSSI value for mote of each network size (motes)', fontsize = 10)
    plt.xlabel('Motes', fontsize = 8)
    plt.legend(['45'], fontsize = 7)
    
    plt.savefig('ploted_figure/13_3_RSSI_distribution_size_30_45.png')
    plt.show()
    
    # boxplot for each network size
    for networksize in range(begin_size, end_size, size_step):
        plt.boxplot(dict_netsize_mote_rssi[networksize].values())
        plt.suptitle('Distribution of RSSI value for motes of network size: {}'.format(networksize), fontsize = 12)
        plt.xlabel('Motes', fontsize = 10)
        plt.ylabel('RSSI (dBm)', fontsize = 10)
    
        plt.savefig('ploted_figure/13_size{}_RSSI_dis_for_motes_size.png'.format(networksize))
        plt.show()
    
#14, Distribution of RSSI value for specific MAC address [OK]
    
    # plot distribution of RSSI value of all motes
    plt.boxplot([b for b in dict_rssi_of_spec_mac.values()])
    
    plt.suptitle('RSSI value distribution of all motes', fontsize = 12)
    plt.xlabel('Motes', fontsize = 10)
    plt.ylabel('RSSI(dBm)', fontsize = 10)
    
    plt.savefig('ploted_figure/14_1_RSSI_dis_MAC.png')
    plt.show()
    
    # plot distribution of RSSI value for manager
    plt.boxplot(dict_rssi_of_spec_mac['00-17-0d-00-00-30-3b-ff'])
    
    plt.suptitle('RSSI value distribution of manager', fontsize = 12)
    plt.xlabel('Motes', fontsize = 10)
    plt.ylabel('RSSI(dBm)', fontsize = 10)
    
    plt.savefig('ploted_figure/14_2_RSSI_dis_manager.png')
    plt.show()
    
    # plot distribution of RSSI value of all motes that have more than 200 RSSI value
    plt.boxplot([b for b in dict_rssi_of_spec_mac.values() if len(b) >200])
    
    plt.suptitle('RSSI value distribution of motes that have more than 200 RSSI value', fontsize = 12)
    plt.xlabel('Motes', fontsize = 10)
    plt.ylabel('RSSI(dBm)', fontsize = 10)
    
    plt.savefig('ploted_figure/14_3_RSSI_dis_more_200_values.png')
    plt.show()
    
    # plot distribution of RSSI value of all motes that have more than 500 RSSI value
    plt.boxplot([b for b in dict_rssi_of_spec_mac.values() if len(b) > 500])
    
    plt.suptitle('RSSI value distribution of motes that have more than 500 RSSI value', fontsize = 12)
    plt.xlabel('Motes', fontsize = 10)
    plt.ylabel('RSSI(dBm)', fontsize = 10)
    
    plt.savefig('ploted_figure/14_4_RSSI_dis_more_500_values.png')
    plt.show()
    
#15, Distribution of number of discovered neighbors for each packet send [OK]
    
    plt.boxplot([dict_num_neighor_for_each_packet_each_size[netsize] for netsize in range(begin_size, end_size, size_step)])
    
    plt.suptitle('Distribution of number of discovered neighbors for each packet send', fontsize = 12)
    plt.xlabel('Network size (motes)', fontsize = 10)
    plt.ylabel('Number of discovered neighbors (motes)', fontsize = 10)
    
    plt.xticks([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], ['0', '5', '10', '15', '20', '25', '30', '35', '40', '45'])
    plt.savefig('ploted_figure/15_discovered_number_dis_per_packet.png')
    plt.show()

# function will get all MAC address and mote IDs for each network size experiment
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
    plot_experiment(0, 46, 5, 'blinkLab_final.txt')
    raw_input('Press enter to finish')
if __name__=="__main__":
    main()



