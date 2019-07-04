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

def proc_mgr_blink_mote(file_name):
    dict_netsize_tranid_packetid = {net:{trans: [] for trans in range(20)} for net in range(0,46,5)} # {net:{transid:[pkid]}}
    dict_netsize_tranid_num_mote = {net:{trans: [] for trans in range(20)} for net in range(0,46,5)} # {net:{transid:[num_motes]}}
    dict_netsize_packetid_num_mote = {net:{packetid: [] for packetid in range(10)} for net in range(0,46,5)} # {netsize:{pkid:[num_mote]}}
    dict_netsize_packet_diff_mote = {net:{packetid: [] for packetid in range(10)} for net in range(0,46,5)} # {netsize:{pk:[diff_mote]}}
    dict_netsize_averge_num_mote = {} # {netsize:[average_num_motes]}

    set_diff_mote = set() # all different discovered motes
    list_average_num_mote_45 = [] # list of all average discovered motes for each packet send of network size 45 motes
    list_average_num_mote_all = [] # list of all average discovered motes for each packet send of all network size

    list_notif_blink_mgr = get_blink_notif_mgr(get_msg_type(file_name,'NOTIF')) #list all blink notif mgr
    
    #===== for tracing
    list_trace_set_moteid = []
    list_trace_moteid = []

    # create the figure folder
    current_dir = os.getcwd()
    new_dir = current_dir + '\experiment_figure'
    if not os.path.exists(new_dir):
        os.makedirs(new_dir)

    for msg in list_notif_blink_mgr:
        # example data: data = [148, 3, 45, 0, 0, 149, 13, 4, 0, 1, 233, 0, 41, 230, 0, 16, 228, 0, 25, 228]
        data = msg['msg']['notifParams'][5] # payload of blink packet
        dict_netsize_tranid_packetid[data[2]][data[3]].append(data[4])
        dict_netsize_tranid_num_mote[data[2]][data[3]].append(data[7])
        dict_netsize_packetid_num_mote[data[2]][data[4]].append(data[7])

        # get the different mote id
        if data[7] == 1:
            set_diff_mote.add(data[9])
            list_trace_moteid.append(data[9])
        elif data[7] == 2:
            set_diff_mote.add(data[9])
            set_diff_mote.add(data[12])
            list_trace_moteid.append(data[9])
            list_trace_moteid.append(data[12])
        elif data[7] == 3:
            set_diff_mote.add(data[9])
            set_diff_mote.add(data[12])
            set_diff_mote.add(data[15])
            list_trace_moteid.append(data[9])
            list_trace_moteid.append(data[12])
            list_trace_moteid.append(data[15])
        else:
            set_diff_mote.add(data[9])
            set_diff_mote.add(data[12])
            set_diff_mote.add(data[15])
            set_diff_mote.add(data[18])
            list_trace_moteid.append(data[9])
            list_trace_moteid.append(data[12])
            list_trace_moteid.append(data[15])
            list_trace_moteid.append(data[18])

        dict_netsize_packet_diff_mote[data[2]][data[4]].append(len(set_diff_mote)) # packet id and number of different motes
        list_trace_set_moteid.append(set_diff_mote)

        # reset set_diff_mote after each transactions, mean packetid == 9.
        # Error: size 10(trans=14, pkid=8), 15(trans=6, pkid=8), 20(trans=3, pkid=8), 20(trans=19, pkid=8), 
        if (data[4] == 9):
            set_diff_mote = set()
        if data[2:5] in [[10,14,8], [15,6,8], [20,3,8], [20,19,8]]: # packetid final of this packet is 8 not is 9
            set_diff_mote = set()

    # get all average value for all network size
    for netsize in range(0, 46, 5):
        list_average_num_mote_all = []
        for pkid in range(10):
            list_average_num_mote_all.append(sta.mean(dict_netsize_packet_diff_mote[netsize][pkid]))
            dict_netsize_averge_num_mote.update({netsize:list_average_num_mote_all})

    #========================================== Print to check data ===================================
    print 'data size 25 motes', (dict_netsize_packet_diff_mote[25])
    print 'average size 25 motes', (dict_netsize_averge_num_mote[25])
    print 'list_trace_moteid', (list_trace_moteid)
    print 'list_trace_set_moteid', (list_trace_set_moteid)
    print 'dict_netsize_packet_diff_mote', (dict_netsize_packet_diff_mote)
    
    #===================================Plotting for all network size ===================================
    #1, plot distribution of different discovered motes for network size 45 motes
    plt.suptitle('Distribution of discovered motes for 45 motes', fontsize = 12)
    #labels = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    #plt.xticks(range(1, 11), labels, fontsize = 10)
    plt.xlabel('Packets send', fontsize = 10)
    plt.ylabel('Discovered motes', fontsize = 10)

    plt.boxplot([dict_netsize_packet_diff_mote[45][packetid] for packetid in range(10)])
    plt.plot(range(1, 11), dict_netsize_averge_num_mote[45], marker = 'o')
    plt.savefig('experiment_figure/16_dist_cover_motes_for_45.png')
    plt.show()
    
    #2, plot distribution of different discovered motes for network size 45 motes
    for netsize in range(0, 46, 5):
        plt.suptitle('Distribution of discovered motes for {} motes'.format(netsize), fontsize = 12)
        #labels = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
        #plt.xticks(range(1, 11), labels, fontsize = 10)
        plt.xlabel('Packets send', fontsize = 10)
        plt.ylabel('Discovered motes', fontsize = 10)
    
        plt.boxplot([dict_netsize_packet_diff_mote[netsize][packetid] for packetid in range(10)])
        plt.plot(range(1, 11), dict_netsize_averge_num_mote[netsize], marker = 'o')
        plt.savefig('experiment_figure/16_{0}_dist_cover_motes.png'.format(netsize))
        plt.show()

#============================ main ============================================
def main():
    #plot_experiment(0, 46, 5, 'blinkLab_final.txt')
    proc_mgr_blink_mote('blinkLab_final.txt')
    raw_input('Press enter to finish')
if __name__=="__main__":
    main()



