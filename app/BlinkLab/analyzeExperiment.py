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
def proc_mgr_blink(networksize, file_name): # OK

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
    list_rssi_of_all_mac = [] # all of rssi values (total rssi of all mac address) of the 1st experiment
    list_trans_time_all = [] # all of transmission time for first experiment
    len_mote_max = [] # all maximum discovered motes

    dict_len_mote = {} # number of neighbors that heard by tag, dict {networksize: list_len_mote}
    dict_packet_no = {} # number of packets that are sent to discover 10 motes, dict {network size: list_packet_no}
    dict_mac_key = {} # MAC addresses that are heard by tag and network size {45:[mac1, mac2, mac3], 40:[]}
    dict_netsize_mote_rssi = {} # dictionary, {network size: {mote's MAC address: list of rssi value}}
    dict_rssi_of_spec_mac = {} # dictionary of {MAC address: list of rssi value}
    dict_rssi_of_all_mac_for_each_size = {} # dictionary of {network size: list rssi value}
    dict_trans_time_for_each_size = {} # dictionary of {network size: list transmission time}
    dict_num_neighor_for_each_packet_each_size = {} # dictionary of {network size: list number of motes}

    print 'Wait for plotting...'

    for netsize in range(begin_size, end_size, size_step):
        num_neighbor = [] # number of discovered neighbor in each packet send
        rssi_value = [] # rssi_value of each discovered neighbors
        list_mac_key = [] # list of mote id and mac address

        data, neighbor, list_packet_no, list_len_mote, dict_mac_rssi = proc_mgr_blink(netsize,file_name)

        dict_netsize_mote_rssi.update({netsize:dict_mac_rssi})
        dict_len_mote.update({netsize:list_len_mote})
        len_mote_max.append(max(list_len_mote))
        dict_packet_no.update({netsize:list_packet_no})

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

        list_len_num_packet_discover_10_motes.append(len(dict_packet_no[netsize]))

        # All MACs have RSSI value
        for mac_key in dict_netsize_mote_rssi[netsize]:
            list_mac_key.append(mac_key)
        dict_mac_key.update({netsize:list_mac_key})

        #plt.plot(list_packet_no, list_len_mote, marker='.') # number of packets send and discovered neighbors
    for i in dict_trans_time_for_each_size.values():
        list_trans_time_all += i
    #print(dict_trans_time_for_each_size.values())

    #plt.plot(dict_packet_no[0], dict_len_mote[0],)
    #plt.plot(dict_packet_no[5], dict_len_mote[5],)
    #plt.plot(dict_packet_no[10], dict_len_mote[10],)
    #plt.plot(dict_packet_no[15], dict_len_mote[15],)
    #plt.plot(dict_packet_no[20], dict_len_mote[20],)
    #plt.plot(dict_packet_no[25], dict_len_mote[25],)
    #plt.plot(dict_packet_no[30], dict_len_mote[30],)
    #plt.plot(dict_packet_no[35], dict_len_mote[35],)
    #plt.plot(dict_packet_no[40], dict_len_mote[40],)
    #plt.plot(dict_packet_no[45], dict_len_mote[45],)

    #plt.plot(list_network_size, list_average_rssi_value, marker = 'o')

    #plt.legend(['0', '5', '10', '15', '20', '25', '30', '35', '40', '45'],title='Network size',  loc='lower right')

    #plt.xlabel('Network size (motes)', fontsize = 10)
    #plt.ylabel('RSSI (dBm)', fontsize = 10)
    #plt.suptitle('Average RSSI value for each network size ', fontsize = 12)

    #plt.plot(list_network_size, [list_len_mote], marker='o')
    #plt.suptitle('Maximum number of different discovered motes for each network size', fontsize = 12)
    #plt.xlabel('Network size (motes)', fontsize = 10)
    #plt.ylabel('Maximum number of different discovered motes (motes)', fontsize = 10)

    #plt.legend(['0', '5', '10', '15', '20', '25', '30', '35', '40', '45'],title='Network size',  loc='lower right')
    #plt.show()

    #plt.boxplot([dict_netsize_mote_rssi[45]['00-17-0d-00-00-31-c6-a1'], dict_netsize_mote_rssi[45]['00-17-0d-00-00-31-c6-a1'], dict_netsize_mote_rssi[45]['00-17-0d-00-00-31-d1-ac']])
    #plt.show()

    #dict_netsize_mote_rssi = {45:{'00-17-0d-00-00-31-d1-ac':[-29, -30, -28, -32]}}
    #dict_rssi_of_spec_mac = {'00-17-0d-00-00-31-cb-e7':[-29, -30, -28, -32], '00-17-0d-00-00-31-ca-03':[-22, -24 -25, -27], '00-17-0d-00-00-31-cc-2e':[-31, -29, -30, -34]}

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

    #for networksize in range(begin_size, end_size, size_step):
    #    plt.boxplot(dict_netsize_mote_rssi[networksize].values())
    #    plt.suptitle('RSSI value distribution for motes of network size: {}'.format(networksize), fontsize = 12)
    #    plt.xlabel('Mote', fontsize = 10)
    #    plt.ylabel('RSSI(dBm)', fontsize = 10)
    #    plt.show()
    #plt.xticks([1, 2, 3, 5, 6, 7, 8, 9, 10], ['0', '5', '10', '15', '20', '25', '30', '35', '40', '45'])

    #1.distribution of transmission time for each network size

    #print(dict_trans_time_for_each_size.values())
    #
    #plt.hist(dict_trans_time_for_each_size, label = '0')
    for networksize in range(begin_size, end_size, size_step):
        plt.hist(dict_trans_time_for_each_size[networksize], label = '{}'.format(networksize))
    #plt.hist(dict_trans_time_for_each_size[0], label = '0')
    #plt.hist(dict_trans_time_for_each_size[5], label = '5')
    #plt.hist(dict_trans_time_for_each_size[10], label = '10')
    #plt.hist(dict_trans_time_for_each_size[15], label = '15')
    #plt.hist(dict_trans_time_for_each_size[20], label = '20')
    #plt.hist(dict_trans_time_for_each_size[25], label = '25')
    #plt.hist(dict_trans_time_for_each_size[30], label = '30')
    #plt.hist(dict_trans_time_for_each_size[35], label = '35')
    #plt.hist(dict_trans_time_for_each_size[40], label = '40')
    #plt.hist(dict_trans_time_for_each_size[45], label = '45')
    #
        plt.suptitle('Transmission time distribution for network size: {}'.format(networksize), fontsize = 12)
        plt.xlabel('Transmission time (s)', fontsize = 10)
        plt.ylabel('Packets', fontsize = 10)
        plt.legend(title='Network size', loc='best')
        plt.show()

    #2.distribution of number of neighbor for each packet send for each network size

    #plt.boxplot([b for b in dict_rssi_of_spec_mac.values() if len(b) >=200])
    #plt.suptitle('Distribution of RSSI values of motes that have more than 200 values', fontsize = 12)
    #plt.xlabel('Mote', fontsize = 10)
    #plt.ylabel('RSSI (dBm)', fontsize = 10)
    ##plt.xticks([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], ['0', '5', '10', '15', '20', '25', '30', '35', '40', '45'])
    #plt.show()


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
    moteid = get_mac_moteid_for_size(0, 46, 5, 'blinkLab_final.txt')
    plot_experiment(0, 46, 5, 'blinkLab_final.txt')
    raw_input('Press enter to finish')
if __name__=="__main__":
    main()



