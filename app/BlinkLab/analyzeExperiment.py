#============================ adjust path =====================================

import sys
import os
if __name__ == "__main__":
    here = sys.path[0]
    sys.path.insert(0, os.path.join(here, '..', '..','libs'))
    sys.path.insert(0, os.path.join(here, '..', '..','external_libs'))


#============================ import =====================================

from matplotlib import pyplot as plt
import statistics as sta

import json
import copy


from SmartMeshSDK.protocols.blink      import blink

#============================ helpers ======================================

def get_msg_type(file_name, msg_type):
    list_msg = []

    with open(file_name,'r') as data_file:
        for line in data_file:
            line_dict = json.loads(line)
            if line_dict['type'] == msg_type:
                list_msg.append(line_dict)
    data_file.close()
    return list_msg

def get_blink_notif_mgr(notif_msg):
    list_blink_msg = []
    for a_msg in notif_msg:
        if a_msg['msg']['serialport'] == 'COM7' and a_msg['msg']['notifName'] == 'notifData' and a_msg['msg']['notifParams'][3] == 61616:
            list_blink_msg.append(a_msg)
    return list_blink_msg

def proc_expr1_mgr_data(file_name):

    dict_netsize_tranid_packetid = {net:{trans: [] for trans in range(20)} for net in range(0,46,5)}
    dict_netsize_tranid_num_mote = {net:{trans: [] for trans in range(20)} for net in range(0,46,5)}
    dict_netsize_packetid_num_mote = {net:{packetid: [] for packetid in range(10)} for net in range(0,46,5)}
    dict_netsize_packet_diff_mote = {net:{packetid: [] for packetid in range(10)} for net in range(0,46,5)}
    dict_netsize_trans_diff_mote = {net:{transid: [] for transid in range(20)} for net in range(0,46,5)}
    dict_netsize_averge_num_mote = {}

    set_diff_mote = set()
    list_average_num_mote_45 = []
    list_average_num_mote_all = []

    #=========================== clearing and processing data================
    list_notif_blink_mgr = get_blink_notif_mgr(get_msg_type(file_name,'NOTIF'))
    for msg in list_notif_blink_mgr:

        data = msg['msg']['notifParams'][5]
        dict_netsize_tranid_packetid[data[2]][data[3]].append(data[4])
        dict_netsize_tranid_num_mote[data[2]][data[3]].append(data[7])
        dict_netsize_packetid_num_mote[data[2]][data[4]].append(data[7])

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
        dict_netsize_trans_diff_mote[data[2]][data[3]].append(len(set_diff_mote))

        if (data[4] == 9):
            set_diff_mote = set()
        if data[2:5] in [[10,14,8], [15,6,8], [20,3,8], [20,19,8]]:
            set_diff_mote = set()

    # get all average value for all network size
    for netsize in range(0, 46, 5):
        list_average_num_mote_all = []
        for pkid in range(10):
            list_average_num_mote_all.append(sta.mean(dict_netsize_packet_diff_mote[netsize][pkid]))
            dict_netsize_averge_num_mote.update({netsize:list_average_num_mote_all})

    #========================= Print to check data =======================


    #=======================Plotting for all network size ================
    print 'wait for plotting ...'
    current_dir = os.getcwd()
    new_dir = current_dir + '\experiment_figure'
    if not os.path.exists(new_dir):
        os.makedirs(new_dir)

    #1, plot distribution of different discovered motes for network size 45 motes
    plt.suptitle('Distribution of discovered motes for 45 motes', fontsize = 12)
    plt.xlabel('Packets send', fontsize = 10)
    plt.ylabel('Discovered motes', fontsize = 10)

    plt.boxplot([dict_netsize_packet_diff_mote[45][packetid] for packetid in range(10)])
    plt.plot(range(1, 11), dict_netsize_averge_num_mote[45], marker = 'o')
    plt.savefig('experiment_figure/16_dist_cover_motes_for_45.png')
    plt.show()
    
    #2, plot distribution of different discovered motes for network size 45 motes
    for netsize in range(0, 46, 5):
        plt.suptitle('Distribution of discovered motes for {} motes'.format(netsize), fontsize = 12)
        plt.xlabel('Packets send', fontsize = 10)
        plt.ylabel('Discovered motes', fontsize = 10)
    
        plt.boxplot([dict_netsize_packet_diff_mote[netsize][packetid] for packetid in range(10)])
        plt.plot(range(1, 11), dict_netsize_averge_num_mote[netsize], marker = 'o')
        plt.savefig('experiment_figure/16_{0}_dist_discover_motes.png'.format(netsize))
        plt.show()

    #3, plot for all 4 subplot network size 5, 15, 25, 35, 45 and network size 10, 20, 30, 40
    # for network size 0, 5
    plt.suptitle('Distribution of discovered motes for each network size', fontsize = 10)
    plt.subplot(2,1,1)
    plt.ylabel('Discovered motes', fontsize = 8)
    plt.boxplot([dict_netsize_packet_diff_mote[0][packetid] for packetid in range(10)])
    plt.plot(range(1, 11), dict_netsize_averge_num_mote[0], marker = 'o')
    plt.legend(['0 motes'], fontsize = 7, loc = 'lower right')

    plt.subplot(2,1,2)
    plt.xlabel('Packets send', fontsize = 8)
    plt.ylabel('Discovered motes', fontsize = 8)
    plt.boxplot([dict_netsize_packet_diff_mote[5][packetid] for packetid in range(10)])
    plt.plot(range(1, 11), dict_netsize_averge_num_mote[5], marker = 'o')
    plt.legend(['5 motes'], fontsize = 7, loc = 'lower right')

    plt.savefig('experiment_figure/17_1_dist_discover_motes_size_0_5.png')
    plt.show()
    
    # for network size 15 to 45
    plt.suptitle('Distribution of discovered motes for each network size', fontsize = 10)
    plt.subplot(2,2,1)
    plt.ylabel('Discovered motes', fontsize = 8)
    plt.boxplot([dict_netsize_packet_diff_mote[15][packetid] for packetid in range(10)])
    plt.plot(range(1, 11), dict_netsize_averge_num_mote[15], marker = 'o')
    plt.legend(['15 motes'], fontsize = 7)
    
    plt.subplot(2,2,2)
    plt.boxplot([dict_netsize_packet_diff_mote[25][packetid] for packetid in range(10)])
    plt.plot(range(1, 11), dict_netsize_averge_num_mote[25], marker = 'o')
    plt.legend(['25 motes'], fontsize = 7)
    
    plt.subplot(2,2,3)
    plt.xlabel('Packets send', fontsize = 8)
    plt.ylabel('Discovered motes', fontsize = 8)
    plt.boxplot([dict_netsize_packet_diff_mote[35][packetid] for packetid in range(10)])
    plt.plot(range(1, 11), dict_netsize_averge_num_mote[35], marker = 'o')
    plt.legend(['35 motes'], fontsize = 7)
    
    plt.subplot(2,2,4)
    plt.xlabel('Packets send', fontsize = 8)
    plt.boxplot([dict_netsize_packet_diff_mote[45][packetid] for packetid in range(10)])
    plt.plot(range(1, 11), dict_netsize_averge_num_mote[45], marker = 'o')
    plt.legend(['45 motes'], fontsize = 7)
    
    plt.savefig('experiment_figure/17_2_dist_discover_motes_size_15_45.png')
    plt.show()
    
    # for network size 10 to 40
    plt.suptitle('Distribution of discovered motes for each network size', fontsize = 10)
    plt.subplot(2,2,1)
    plt.ylabel('Discovered motes', fontsize = 8)
    plt.boxplot([dict_netsize_packet_diff_mote[10][packetid] for packetid in range(10)])
    plt.plot(range(1, 11), dict_netsize_averge_num_mote[10], marker = 'o')
    plt.legend(['10 motes'], fontsize = 7)
    
    plt.subplot(2,2,2)
    plt.boxplot([dict_netsize_packet_diff_mote[20][packetid] for packetid in range(10)])
    plt.plot(range(1, 11), dict_netsize_averge_num_mote[20], marker = 'o')
    plt.legend(['20 motes'], fontsize = 7)
    
    plt.subplot(2,2,3)
    plt.xlabel('Packets send', fontsize = 8)
    plt.ylabel('Discovered motes', fontsize = 8)
    plt.boxplot([dict_netsize_packet_diff_mote[30][packetid] for packetid in range(10)])
    plt.plot(range(1, 11), dict_netsize_averge_num_mote[30], marker = 'o')
    plt.legend(['30 motes'], fontsize = 7)
    
    plt.subplot(2,2,4)
    plt.xlabel('Packets send', fontsize = 8)
    plt.boxplot([dict_netsize_packet_diff_mote[40][packetid] for packetid in range(10)])
    plt.plot(range(1, 11), dict_netsize_averge_num_mote[40], marker = 'o')
    plt.legend(['40 motes'], fontsize = 7)
    
    plt.savefig('experiment_figure/17_3_dist_discover_motes_size_10_40.png')
    plt.show()

def proc_expr1_sync_time(file_name):
    LIST_NETSIZE = range(11, 38) # depend on the network size and for testing, we use range(11,38), real experiment, we use range(0, 46,5)

    dict_hash_payload = {} # {hash: data}
    dict_hash_dn_blink = {} # {hash: time_dn_blink}
    dict_hash_tx_done = {} # {hash:time_tx_done}

    dict_hash_synctime = {} # {hash:synctime}
    dict_netsize_hash_synctime = {} # {netsize1:{hash1: time1, hash2:time2}, netsize2:{hash3: time3, hash4: time4}}
    dict_netsize_synctime = {} # {netsize1:[time1, time2, time3]}

    #=========================== clearing and processing data================
    for txdone in get_msg_type(file_name, 'NOTIF'):
        if txdone['msg']['txMsg'][1]['status'] == 0:
            dict_hash_tx_done.update({hash(tuple(txdone['msg']['payload'])): txdone['timestamp']})
        else:
            print 'Packet is sent failed:', txdone['msg']['payload']

    for dn_blink in get_msg_type(file_name, 'CMD'):
        dict_hash_dn_blink.update({hash(tuple(dn_blink['msg']['params']['payload'])): dn_blink['timestamp']})
        dict_hash_payload.update({hash(tuple(dn_blink['msg']['params']['payload'])): dn_blink['msg']['params']['payload']})

    for payload_hash in dict_hash_tx_done:
        dict_hash_synctime.update({payload_hash : dict_hash_tx_done[payload_hash] - dict_hash_dn_blink[payload_hash]})

    for payload in dict_hash_payload:
        dict_netsize_hash_synctime.update({dict_hash_payload[payload][0]:{}})
        dict_netsize_synctime.update({dict_hash_payload[payload][0]:[]})
    
    # get data for dict_netsize_hash_synctime

    for netsize in dict_netsize_hash_synctime:
        for h in dict_hash_synctime:
            if netsize == dict_hash_payload[h][0]:
                dict_netsize_hash_synctime[netsize].update({h:dict_hash_synctime[h]})

    # get data for dict_netsize_hash_synctime
    for netsize in dict_netsize_synctime:
        dict_netsize_synctime.update({netsize : dict_netsize_hash_synctime[netsize].values()})
    
    
    #=========================== print information ================
    for payload in dict_hash_synctime:
        if dict_hash_synctime[payload] > 6:
            print 'synctime is greater 6s:',  dict_hash_payload[payload], 'synctime is:', dict_hash_synctime[payload]

    #print 'dict_netsize_hash_synctime', dict_netsize_hash_synctime
    print 'dict_netsize_synctime', dict_netsize_synctime

    #=========================== visualizing data================
    print 'wait for plotting ...'
    current_dir = os.getcwd()
    new_dir = current_dir + '\experiment_figure'
    if not os.path.exists(new_dir):
        os.makedirs(new_dir)

    #1, all sync times for all packets
    plt.suptitle('Synctime for all network sizes', fontsize = 12)
    plt.ylabel('Time values(s)', fontsize = 12)
    plt.xlabel('Packet ID', fontsize = 12)

    plt.plot([i for i in dict_hash_synctime.values()])
    plt.savefig('experiment_figure/exp1_synctime_netsize.png')
    plt.show()
    
    #2, average sync times for each network size
    plt.suptitle('Average synctime for all network sizes', fontsize = 12)
    labels = [i for i in dict_netsize_hash_synctime]
    plt.ylabel('Time values(s)', fontsize = 12)
    plt.xlabel('Network size', fontsize = 12)

    plt.plot([sta.mean(dict_netsize_synctime[netsize]) for netsize in labels])
    plt.xticks(range(len(labels)), labels)
    plt.savefig('experiment_figure/exp1_synctime_netsize.png')
    plt.show()
    

#============================ main ============================================
def main():
    #proc_expr1_mgr_data('blinkLab_final.txt')
    proc_expr1_sync_time('expr2_blink_log_sample.txt')
    raw_input('\n\nPress enter to finish! \n\n')
if __name__=="__main__":
    main()



