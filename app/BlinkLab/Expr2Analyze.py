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
import base64

from SmartMeshSDK.protocols.blink      import blink

#============================ network and experiment infor ======================================
dict_moteid_mac = {1: '00-17-0D-00-00-58-2B-4F', 2: '00-17-0D-00-00-31-CA-03', 3: '00-17-0D-00-00-38-06-D5', 4: '00-17-0D-00-00-31-C3-37', 5: '00-17-0D-00-00-38-00-63', 6: '00-17-0D-00-00-38-05-E9', 7: '00-17-0D-00-00-38-06-F0', 8: '00-17-0D-00-00-38-03-D9', 9: '00-17-0D-00-00-31-D5-20', 10: '00-17-0D-00-00-38-03-69', 11: '00-17-0D-00-00-30-3E-09', 12: '00-17-0D-00-00-38-06-C9', 13: '00-17-0D-00-00-38-03-CA', 14: '00-17-0D-00-00-31-CC-40', 15: '00-17-0D-00-00-58-2A-E8', 16: '00-17-0D-00-00-31-D4-7E', 17: '00-17-0D-00-00-38-06-AD', 18: '00-17-0D-00-00-31-D1-AC', 19: '00-17-0D-00-00-38-05-DA', 20: '00-17-0D-00-00-31-C6-A1', 21: '00-17-0D-00-00-38-06-67', 22: '00-17-0D-00-00-38-03-87', 23: '00-17-0D-00-00-38-04-25', 24: '00-17-0D-00-00-31-D5-69', 25: '00-17-0D-00-00-38-05-F1', 26: '00-17-0D-00-00-31-C9-F1', 27: '00-17-0D-00-00-38-04-3B', 28: '00-17-0D-00-00-31-C7-B0', 29: '00-17-0D-00-00-31-C3-19', 30: '00-17-0D-00-00-31-D5-3B', 31: '00-17-0D-00-00-31-C7-DE', 32: '00-17-0D-00-00-31-C9-E6', 33: '00-17-0D-00-00-31-D5-30', 34: '00-17-0D-00-00-31-D5-1F', 35: '00-17-0D-00-00-31-C1-A0', 36: '00-17-0D-00-00-31-CA-05', 37: '00-17-0D-00-00-31-CC-58', 38: '00-17-0D-00-00-31-D5-67', 39: '00-17-0D-00-00-31-C3-53', 40: '00-17-0D-00-00-31-CB-E5', 41: '00-17-0D-00-00-31-C1-C1', 42: '00-17-0D-00-00-31-CC-2E', 43: '00-17-0D-00-00-31-D1-D3', 44: '00-17-0D-00-00-31-C9-DA', 45: '00-17-0D-00-00-31-D1-32', 46: '00-17-0D-00-00-31-D5-86', 47: '00-17-0D-00-00-31-C1-A1', 48: '00-17-0D-00-00-31-C6-B8', 49: '00-17-0D-00-00-31-CB-E7', 50: '00-17-0D-00-00-31-CC-0F', 51: '00-17-0D-00-00-31-D1-A8', 52: '00-17-0D-00-00-31-D1-70', 53: '00-17-0D-00-00-31-D5-6A', 54: '00-17-0D-00-00-31-C3-71', 55: '00-17-0D-00-00-31-C1-AB', 56: '00-17-0D-00-00-31-C3-3E', 57: '00-17-0D-00-00-31-D5-01'} # for all 54 motes + 3 access points

dict_mac_room_name = {'00-17-0D-00-00-31-C3-37': 'A125', '00-17-0D-00-00-38-06-67': 'A110', '00-17-0D-00-00-31-CC-0F': 'A320', '00-17-0D-00-00-31-C3-71': 'A315', '00-17-0D-00-00-31-D5-3B': 'A310', '00-17-0D-00-00-31-C1-AB': 'A313', '00-17-0D-00-00-31-C6-B8': 'A304', '00-17-0D-00-00-31-CC-58': 'A208', '00-17-0D-00-00-31-D5-20': 'A101', '00-17-0D-00-00-38-05-F1': 'A115', '00-17-0D-00-00-30-3E-09': 'A120W', '00-17-0D-00-00-31-C7-B0': 'A215', '00-17-0D-00-00-31-D1-A8': 'A328', '00-17-0D-00-00-38-05-E9': 'A109', '00-17-0D-00-00-31-D5-86': 'A327', '00-17-0D-00-00-31-C9-E6': 'A224', '00-17-0D-00-00-38-03-69': 'A111', '00-17-0D-00-00-38-06-F0': 'A116', '00-17-0D-00-00-38-03-CA': 'A103', '00-17-0D-00-00-58-2A-E8': 'A116W', '00-17-0D-00-00-31-C9-F1': 'A223', '00-17-0D-00-00-31-CC-40': 'A220', '00-17-0D-00-00-31-C1-A0': 'A211', '00-17-0D-00-00-38-05-DA': 'A107', '00-17-0D-00-00-38-06-AD': 'A105', '00-17-0D-00-00-31-C3-3E': 'A322', '00-17-0D-00-00-31-D5-30': 'A226', '00-17-0D-00-00-31-C3-19': 'A216', '00-17-0D-00-00-31-CA-03': 'A126', '00-17-0D-00-00-31-CA-05': 'A205', '00-17-0D-00-00-31-D5-1F': 'A203', '00-17-0D-00-00-38-04-3B': 'A120', '00-17-0D-00-00-31-C3-53': 'A210', '00-17-0D-00-00-38-06-C9': 'A123', '00-17-0D-00-00-31-D5-01': 'A309', '00-17-0D-00-00-31-D5-6A': 'A307', '00-17-0D-00-00-31-C1-A1': 'A301', '00-17-0D-00-00-38-04-25': 'A118', '00-17-0D-00-00-31-D1-D3': 'A318', '00-17-0D-00-00-31-C7-DE': 'A213', '00-17-0D-00-00-31-D1-AC': 'A204', '00-17-0D-00-00-58-2B-4F': 'A124W', '00-17-0D-00-00-31-D4-7E': 'A221', '00-17-0D-00-00-31-D5-69': 'A225', '00-17-0D-00-00-38-03-D9': 'A121', '00-17-0D-00-00-38-06-D5': 'A113', '00-17-0D-00-00-38-03-87': 'A104', '00-17-0D-00-00-31-D5-67': 'A207', '00-17-0D-00-00-31-C6-A1': 'A218', '00-17-0D-00-00-38-00-63': 'A124', '00-17-0D-00-00-31-D1-32': 'A303', '00-17-0D-00-00-31-CC-2E': 'A326', '00-17-0D-00-00-31-D1-70': 'A311', '00-17-0D-00-00-31-C9-DA': 'A316', '00-17-0D-00-00-31-CB-E7': 'A306', '00-17-0D-00-00-31-CB-E5': 'A201', '00-17-0D-00-00-31-C1-C1': 'A324'} # for all 54 motes + 3 access points, mote location

dict_loc_id_name = {11: 'A101', 12: 'A102', 13: 'A103', 14: 'A104', 15: 'A105', 16: 'A106', 17: 'A107', 18: 'A108', 19: 'A109', 20: 'A110', 21: 'A111', 22: 'A112', 23: 'A113', 24: 'A114', 25: 'A115', 26: 'A116', 27: 'A117', 28: 'A118', 29: 'A119', 30: 'A120', 31: 'A121', 32: 'A122', 33: 'A123', 34: 'A124', 35: 'A125', 36: 'A126', 37: 'A127', 41: 'A201', 42: 'A202', 43: 'A203', 44: 'A204', 45: 'A205', 46: 'A206', 47: 'A207', 48: 'A208', 49: 'A209', 50: 'A210', 51: 'A211', 52: 'A212', 53: 'A213', 54: 'A214', 55: 'A215', 56: 'A216', 57: 'A217', 58: 'A218', 59: 'A219', 60: 'A220', 61: 'A221', 62: 'A222', 63: 'A223', 64: 'A224', 65: 'A225', 66: 'A226', 71: 'A301', 72: 'A302', 73: 'A303', 74: 'A304', 75: 'A305', 76: 'A306', 77: 'A307', 78: 'A308', 79: 'A309', 80: 'A310', 81: 'A311', 82: 'A312', 83: 'A313', 84: 'A314', 85: 'A315', 86: 'A316', 87: 'A317', 88: 'A318', 89: 'A319', 90: 'A320', 91: 'A321', 92: 'A322', 93: 'A323', 94: 'A324', 95: 'A325', 96: 'A326', 97: 'A327', 98: 'A328'} # for all room, tag locations

dict_tagloc_moteloc_distance = {tagloc:{moteloc: 0 for moteloc in dict_mac_room_name.values()} for tagloc in dict_loc_id_name.values()}


#dict_mapping_info = {}, there are 3240 cap gia tri trong 81 location test
# ['A102', 'A112', 3]

#============================ variables ======================================
dict_loc_data_packet = {loc_id: [] for loc_id in dict_loc_id_name} # {loc_id:[]}
dict_loc_list_neighbor = {loc_id: [] for loc_id in dict_loc_id_name} # {loc_id:[]}
dict_loc_neighbor_id = {}

# target = {roomid1: {mid1:[rssi1, rssi2, rssi3, rssi4], {mid2:[rssi1, rssi2, rssi3, rssi4]}, roomid1: {mid1:[rssi1, rssi2, rssi3, rssi4]}, }

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

def get_blink_data_vmgr(notif_msg):
    list_blink_data = []
    for a_msg in notif_msg:
            list_blink_data.append(a_msg['msg']['data_vmgr'])
    return list_blink_data

def proc_mgr_blink_mote(file_name):

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
    list_notif_blink_mgr = get_blink_data_vmgr(get_msg_type(file_name,'NOTIF'))
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

def proc_expr2_bink_data(vmrg_blink_data):
    dict_loc_neigh_id_rssi = {} # dictionary {loc_test: {loc_of_heard_mote : [rssi1, rssi2, rssi3]}, ...}
    dict_moteid_room = {} # {moteid: room}

    blink_decode = [base64.b64decode(blk_str) for blk_str in vmrg_blink_data]

#============================ processing data ======================================
    # get the values for each location test: {loc_id:[packet1, packet2, packet3]}
    for blk in blink_decode:
        blk_decode = [ord(b) for b in blk]
        dict_loc_data_packet[blk_decode[2]].append(blk)

    # decode blink data to payload, and neighbor we get rssi value, {loc_id:[[(id1, rssi1),(),(), ()]]}
    for loc_id in dict_loc_data_packet:
        list_neighbor = []
        for data in dict_loc_data_packet[loc_id]:
            blinkdata, blinkneighbors = blink.decode_blink(data)
            list_neighbor.append(blinkneighbors)
        dict_loc_list_neighbor[loc_id] = list_neighbor

    # get {loc_id: set of heard moteid}
    for loc_id in dict_loc_list_neighbor:
        set_neighbor_id = set()
        for packet in dict_loc_list_neighbor[loc_id]:
            for neighbor in packet:
                set_neighbor_id.add(neighbor[0])
        dict_loc_neighbor_id.update({loc_id:set_neighbor_id})

    # get {loc_id: {moteid: [rssi]}}
    for loc_id in dict_loc_list_neighbor:
        dict_neigh_id_rssi = {}
        for moteid in dict_loc_neighbor_id[loc_id]:
            dict_neigh_id_rssi.update({moteid:[]})
        dict_loc_neigh_id_rssi.update({loc_id: dict_neigh_id_rssi})

        for packet in dict_loc_list_neighbor[loc_id]:
            for neighbor in packet:
                if neighbor[0] in dict_loc_neighbor_id[loc_id]:
                    dict_loc_neigh_id_rssi[loc_id][neighbor[0]].append(neighbor[1])

    # create {moteid: room_name}, dict_mac_room_name, dict_moteid_mac
    for moteid in dict_moteid_mac:
        dict_moteid_room.update({moteid:dict_mac_room_name[dict_moteid_mac[moteid]]})

    # change the loc_id -> real location name of dict_loc_neigh_id_rssi
    for loc_id in dict_loc_list_neighbor:
        dict_loc_neigh_id_rssi[dict_loc_id_name[loc_id]] = dict_loc_neigh_id_rssi.pop(loc_id)
        for moteid in dict_loc_neighbor_id[loc_id]:
            dict_loc_neigh_id_rssi[dict_loc_id_name[loc_id]][dict_moteid_room[moteid]] = dict_loc_neigh_id_rssi[dict_loc_id_name[loc_id]].pop(moteid)

#============================ printing data ======================================

    print 'dict_loc_neigh_id_rssi', dict_loc_neigh_id_rssi
    print 'dict_tagloc_moteloc_distance', dict_tagloc_moteloc_distance
    for roomid in dict_loc_neigh_id_rssi:
        for k in dict_loc_neigh_id_rssi[roomid]:
            if len(dict_loc_neigh_id_rssi[roomid]) >0:
                print '|RoomID|', roomid, '|Mote|', k, '|Min|', min(dict_loc_neigh_id_rssi[roomid][k]), '|Max|', max(dict_loc_neigh_id_rssi[roomid][k])

#============================ visualizing data ======================================
    # create folder for the figure
    current_dir = os.getcwd()
    new_dir = current_dir + '\expr2_figure'
    if not os.path.exists(new_dir):
        os.makedirs(new_dir)

    print ' wait for ploting ...'

    #1, plot the rssi values distribution of each test location for each heard mote

    plt.suptitle('Distribution of RSSI values when blink mote is at room A102')
    labels = [mote for mote in dict_loc_neigh_id_rssi['A102']]
    plt.xlabel('Heard mote (location)', fontsize = 10)
    plt.ylabel('RSSI values (-dBm)', fontsize = 10)

    plt.boxplot([dict_loc_neigh_id_rssi['A102'][room] for room in labels])
    plt.xticks(range(1, len(labels) +1), labels)
    plt.show()

    #2, plot all location test
    real_expr_loc = [k for k in dict_loc_neigh_id_rssi if len(dict_loc_neigh_id_rssi[k]) >0]
    for loc in real_expr_loc:
        plt.suptitle('Distribution of RSSI values when blink mote is at room {}'.format(loc))
        labels = [mote for mote in dict_loc_neigh_id_rssi[loc]]
        plt.xlabel('Mote locations (room)', fontsize = 10)
        plt.ylabel('RSSI values (-dBm)', fontsize = 10)

        plt.boxplot([dict_loc_neigh_id_rssi[loc][room] for room in labels])
        plt.xticks(range(1, len(labels) +1), labels)

        plt.savefig('expr2_figure/1_dist_rssi_for_tag_room_{}_.png'.format(loc))
        plt.show()

#============================ main ============================================
def main():
    list_blink = get_blink_data_vmgr(get_msg_type('expr2_vmgr_log_sample.txt', 'NOTIF'))
    print 'list_blink', list_blink
    proc_expr2_bink_data(list_blink)
    raw_input('Press enter to finish')
if __name__=="__main__":
    main()



