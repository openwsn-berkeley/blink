#!/usr/bin/python

#============================ adjust path =====================================

import sys
import os
if __name__ == "__main__":
    here = sys.path[0]
    sys.path.insert(0, os.path.join(here, '..', '..','libs'))
    sys.path.insert(0, os.path.join(here, '..', '..','external_libs'))
    
#============================ imports =========================================

import time
import threading
import json
import datetime

from SmartMeshSDK.IpMgrConnectorSerial  import IpMgrConnectorSerial
from SmartMeshSDK.IpMoteConnector       import IpMoteConnector
from SmartMeshSDK.IpMgrConnectorMux     import IpMgrSubscribe
from SmartMeshSDK.protocols.blink       import blink


from SmartMeshSDK.utils                 import AppUtils, \
                                               FormatUtils
from SmartMeshSDK.ApiException          import APIError, \
                                                ConnectionError,  \
                                                CommandTimeoutError

#============================ defines =========================================

SERIALPORT_MGR_1        = 'COM7'
SERIALPORT_MGR_2        = 'COM15'
SERIALPORT_TAG          = 'COM11'
ALLMOTES                = [
    [0, 23, 13, 0, 0, 49, 198, 161], 
    [0, 23, 13, 0, 0, 49, 193, 171], 
    [0, 23, 13, 0, 0, 49, 204, 15], 
    [0, 23, 13, 0, 0, 49, 195, 71], 
    [0, 23, 13, 0, 0, 49, 213, 59], 
    [0, 23, 13, 0, 0, 49, 201, 230], 
    [0, 23, 13, 0, 0, 49, 202, 3], 
    [0, 23, 13, 0, 0, 49, 209, 95], 
    [0, 23, 13, 0, 0, 49, 213, 103], 
    [0, 23, 13, 0, 0, 49, 213, 106], 
    [0, 23, 13, 0, 0, 49, 213, 48], 
    [0, 23, 13, 0, 0, 49, 202, 5], 
    [0, 23, 13, 0, 0, 49, 204, 46], 
    [0, 23, 13, 0, 0, 49, 193, 161], 
    [0, 23, 13, 0, 0, 49, 209, 112], 
    [0, 23, 13, 0, 0, 49, 213, 1], 
    [0, 23, 13, 0, 0, 49, 204, 64], 
    [0, 23, 13, 0, 0, 49, 201, 218], 
    [0, 23, 13, 0, 0, 49, 201, 241], 
    [0, 23, 13, 0, 0, 49, 213, 32], 
    [0, 23, 13, 0, 0, 49, 209, 172], 
    [0, 23, 13, 0, 0, 49, 198, 184], 
    [0, 23, 13, 0, 0, 49, 195, 55], 
    [0, 23, 13, 0, 0, 49, 194, 249], 
    [0, 23, 13, 0, 0, 49, 204, 88], 
    [0, 23, 13, 0, 0, 49, 195, 83], 
    [0, 23, 13, 0, 0, 49, 203, 229], 
    [0, 23, 13, 0, 0, 49, 209, 50], 
    [0, 23, 13, 0, 0, 49, 193, 160],  
    [0, 23, 13, 0, 0, 49, 195, 113], 
    [0, 23, 13, 0, 0, 49, 209, 211], 
    [0, 23, 13, 0, 0, 49, 193, 193], 
    [0, 23, 13, 0, 0, 49, 195, 62], 
    [0, 23, 13, 0, 0, 49, 213, 31], 
    [0, 23, 13, 0, 0, 49, 209, 168], 
    [0, 23, 13, 0, 0, 49, 195, 25], 
    [0, 23, 13, 0, 0, 49, 199, 222], 
    [0, 23, 13, 0, 0, 49, 203, 231], 
    [0, 23, 13, 0, 0, 49, 204, 89], 
    [0, 23, 13, 0, 0, 49, 198, 146], 
    [0, 23, 13, 0, 0, 49, 213, 105], 
    [0, 23, 13, 0, 0, 49, 199, 219], 
    [0, 23, 13, 0, 0, 49, 213, 134], 
    [0, 23, 13, 0, 0, 49, 213, 50], 
    [0, 23, 13, 0, 0, 49, 195, 10],
]

TAG_EUI = [0, 23, 13, 0, 0, 56, 7, 12]

#============================ helpers =========================================

fileLock = threading.RLock() 
mgr1 = IpMgrConnectorSerial.IpMgrConnectorSerial()
mgr2 = IpMgrConnectorSerial.IpMgrConnectorSerial()
tag = IpMoteConnector.IpMoteConnector()
NotifEventDone = threading.Event()
idx = 0
issueTime = 0
payLoadBlink = 'Hello'

def printAndLog(msg_type, msg, firstline = False):
    global fileLock
    print msg_type, msg
    if firstline:
        filemode = 'a'
    else:
        filemode = 'a'
    with fileLock:
        with open('blinkLab.json', filemode) as f:
            f.write(
                json.dumps({
                    'timestamp': time.time(),
                    'type'     : msg_type,
                    'msg'      : msg,
                })+ '\n'
            )
   
def handle_mgr_notif(notifName, notifParams):  
    mac_address = '-'.join(['%02x'%b for b in notifParams.macAddress])
    payload     = ''.join([chr(b) for b in notifParams.data])
    listRSSI = []
    listNeighbor = []
    moteID = {}
    moteID = getAllMote(mgr1)
    try: 
        printAndLog('MGRNOTIF', {'notifName': notifName, 'notifParams': notifParams})
        data, neighbors = blink.decode_blink(payload)
        if data:
            #print '\nBlink packet received from {0}'.format(mac_address)
            RxTime = datetime.datetime.now()

            for neighbor_id, rssi in neighbors:
                print '    --> Neighbor ID = {0},  RSSI = {1}'.format(neighbor_id, rssi)
                # for dump information
                listRSSI.append(rssi)
                listNeighbor.append(neighbor_id) 
                           
            if len(listNeighbor) == 1:
                mgrBlinkInfo = {'MgrRxTime': '{}'.format(RxTime), 'Payload':'{}'.format(data),'TagAddress': '{0}'.format(mac_address), 'HeardMote': [{'MoteID': '{0}'.format(listNeighbor[0]), 'MAC':moteID[listNeighbor[0]], 'RSSI': '{0}'.format(listRSSI[0])}]}
            elif len(listNeighbor) == 2:
                mgrBlinkInfo = {'MgrRxTime': '{}'.format(RxTime), 'Payload':'{}'.format(data),'TagAddress': '{0}'.format(mac_address), 'HeardMote': [{'MoteID': '{0}'.format(listNeighbor[0]), 'MAC':moteID[listNeighbor[0]], 'RSSI': '{0}'.format(listRSSI[0])},{'MoteID': '{0}'.format(listNeighbor[1]), 'MAC':moteID[listNeighbor[1]], 'RSSI': '{0}'.format(listRSSI[1])}]}
            elif len(listNeighbor) == 3:
                mgrBlinkInfo = {'MgrRxTime': '{}'.format(RxTime), 'Payload':'{}'.format(data),'TagAddress': '{0}'.format(mac_address), 'HeardMote': [{'MoteID': '{0}'.format(listNeighbor[0]), 'MAC':moteID[listNeighbor[0]], 'RSSI': '{0}'.format(listRSSI[0])},{'MoteID': '{0}'.format(listNeighbor[1]), 'MAC':moteID[listNeighbor[1]], 'RSSI': '{0}'.format(listRSSI[1])},{'MoteID': '{0}'.format(listNeighbor[2]), 'MAC':moteID[listNeighbor[2]], 'RSSI': '{0}'.format(listRSSI[2])}]}
            else:
                mgrBlinkInfo = {'MgrRxTime': '{}'.format(RxTime), 'Payload':'{}'.format(data),'TagAddress': '{0}'.format(mac_address), 'HeardMote': [{'MoteID': '{0}'.format(listNeighbor[0]), 'MAC':moteID[listNeighbor[0]], 'RSSI': '{0}'.format(listRSSI[0])},{'MoteID': '{0}'.format(listNeighbor[1]), 'MAC':moteID[listNeighbor[1]], 'RSSI': '{0}'.format(listRSSI[1])},{'MoteID': '{0}'.format(listNeighbor[2]), 'MAC':moteID[listNeighbor[2]], 'RSSI': '{0}'.format(listRSSI[2])},{'MoteID': '{0}'.format(listNeighbor[3]), 'MAC':moteID[listNeighbor[3]], 'RSSI': '{0}'.format(listRSSI[3])}]}
                                 
            if not neighbors:
                print '    --> Neighbors = n/a'            
            print '    --> Data Sent = {0}\n\n'.format(data.encode("hex"))
            # print and log Bink data to blinkLab.txt file            
            printAndLog('MGRBLINK', mgrBlinkInfo)
            
    except Exception as err:
        print err

# ---- Get all MAC address and ID
def getAllMote(mgrconnector):
    currentMac     = (0,0,0,0,0,0,0,0) # start getMoteConfig() iteration with the 0 MAC address
    continueAsking = True
    moteIDMac = {}
    moteIDMac[1] = 'Manager'
    
    while continueAsking:
        try:
            res = mgrconnector.dn_getMoteConfig(currentMac,True)
        except APIError:
            continueAsking = False
        else:
            if ((not res.isAP) and (res.state in [0,1,4])):
                moteIDMac[res.moteId] = '{}'.format(FormatUtils.formatMacString(res.macAddress)) 
            currentMac = res.macAddress
    return moteIDMac
    #######


# Processing data in Blink mote
def handle_mote_notif(mynotif):
    global issueTime
    global payLoadBlink
    # Check for txDone notification, then print status information
    printAndLog('TAGNOTIF', mynotif)
    if mynotif[0]==['txDone']:
        #txDoneTime = datetime.datetime.now()
        for key, value in mynotif[1].items():
            if key == "status":
                if value == 0:
                    txDoneTime = datetime.datetime.now()
                    blinkSide = {'IssueTime': '{}'.format(issueTime), 'TxDoneTime': '{}'.format(txDoneTime), 'TxDoneTime-IssueTime':'{}'.format(txDoneTime-issueTime), 'Payload':'{}'.format(payLoadBlink)}
                    print ('\n     txDone Status = {0}, Blink packet successfully sent\n'.format(value))
                    printAndLog('TAGBLINK', blinkSide)
                else:
                    print ('\n     txDone Status = {0}, Error, Blink packet NOT sent\n'.format(value))
                NotifEventDone.set()
    
def mote_disconnection():
    print 'Mote was disconnected\n'

#============================ classes =========================================

class BlinkLab(threading.Thread):
    
    def __init__(self):
        
        # log
        printAndLog('START', '', firstline = True)
        
        # init the parent
        threading.Thread.__init__(self)
        self.name            = 'BlinkLab'
        self.start()
        
    #======================== public ==========================================
    
    def run(self):
        global idx
        
        # connect to manager 1 (manager log data for experiment)
        self.mgr1 = mgr1
        self.mgr1.connect({'port': SERIALPORT_MGR_1})
        print 'connect manager 1 done!'

        # connect to manager 2 (manager keeps motes)
        self.mgr2 = mgr2
        self.mgr2.connect({'port': SERIALPORT_MGR_2})
        print 'connect manager 2 done!'
        
        # connect to tag
        self.tag = tag
        self.tag.connect({'port': SERIALPORT_TAG})
        print 'connect tag done!'

        print 'first network id of manager 1: {}'.format(self.mgr1.dn_getNetworkConfig().networkId)
        print 'first network id of manager 2: {}'.format(self.mgr2.dn_getNetworkConfig().networkId)
        print 'first network of tag: {}'.format(self.tag.dn_getParameter_networkId().networkId)
        
        # run experiment for different network size for test 5 motes maximum
        for networksize in range(45,-1,-5):
            idx += 1
            print '\n\nrun experiment {} motes index {}!!!'.format(networksize, idx)
            self.runExperimentForSize(networksize)

        print 'after experiment network id of manager 1: {}'.format(self.mgr1.dn_getNetworkConfig().networkId)
        print 'after experiment network id id of manager 2: {}'.format(self.mgr2.dn_getNetworkConfig().networkId)
        print 'after experiment network id id of tag: {}'.format(self.tag.dn_getParameter_networkId().networkId)         

        # set default configuration after experiment
        self.setDefaultConfig()
    #======================== private ==========================================
    def runExperimentForSize(self,networksize):
        global idx
        global issueTime
        global payLoadBlink
        res1 = self.mgr1.dn_getNetworkInfo()
        res2 = self.mgr2.dn_getNetworkInfo()
        
        # create the mote list that is will be deleted from manager 1 for each experiment
        if networksize == 45:
            del_mote_list = []
        else:
            del_mote_list = [ALLMOTES[i] for i in range((idx -2)*5, (idx-1)*5)]

        # detach 5 motes in the manager 1 for each experiment
        for m in del_mote_list:
           self.mgr1.dn_deleteACLEntry(
               macAddress = m,
            )
           self.mgr1.dn_reset(
                type       = 2,
                macAddress = m,
            )

        # wait for all motes in manager 1 after detaching motes
        print 'wait for removing mote out of manager 1'
        while self.mgr1.dn_getNetworkInfo().numMotes != networksize:
            print '.',
            time.sleep(1)
        

        oldNetId = self.mgr1.dn_getNetworkConfig().networkId
        print 'old network id from manager 1 and tag: {}'.format(oldNetId)
        print 'old network id from manager 2: {}'.format(self.mgr2.dn_getNetworkConfig().networkId)

        # set new network id for manager 1, 2 and tag

        self.mgr1.dn_exchangeNetworkId(
            id = oldNetId + 2
        )

        self.tag.dn_setParameter_networkId(
            networkId = oldNetId + 2
        )

        self.mgr2.dn_exchangeNetworkId(
            id = oldNetId
        )

        print 'new network id from manager 1 and tag: {}'.format(self.mgr1.dn_getNetworkConfig().networkId)
        print 'new network id from manager 2: {}\n'.format(self.mgr2.dn_getNetworkConfig().networkId)

        # reset all networks to apply new ID
        print '\nchange network id successfully and wait for manager 1 and manager 2 deliver the network id to motes\n'

        # wait for both manager deliver network id to all motes
        if res1.numMotes >= res2.numMotes:
            timeWait = (res1.numMotes)*30 + 45
        else:
            timeWait = (res2.numMotes)*30 + 45
        print 'waiting time is {}s'.format(timeWait)
        time.sleep(timeWait)
        
        self.mgr1.dn_reset(
            type       = 0,
            macAddress = [0x00]*8,
        )

        self.tag.dn_reset()
        
        self.mgr2.dn_reset(
            type       = 0,
            macAddress = [0x00]*8,
        )
        time.sleep(1)              

        print 'reset all networks done and wait for 45s to change network id in the motes!'

        self.mgr1.disconnect()
        self.mgr2.disconnect()
        self.tag.disconnect()        

        time.sleep(45)
        
        self.mgr1.connect({'port': SERIALPORT_MGR_1})
        self.mgr2.connect({'port': SERIALPORT_MGR_2})
        self.tag.connect({'port': SERIALPORT_TAG})

        print 'connect manager 1, 2 and blink mote again done!'     
        
        
        # wait for both manager 1, 2 network to form to ensure both of them don't lost any mote for next network id change
        while True:
            
            res = self.mgr1.dn_getNetworkInfo()
            print 'size of network as parameter: {0}, Mgr1.numMotes={1}, Mgr2.numMotes={2}'.format(networksize,res.numMotes,self.mgr2.dn_getNetworkInfo().numMotes)
            if (res.numMotes==networksize) and (self.mgr2.dn_getNetworkInfo().numMotes == 45-networksize):
                break
            time.sleep(1)
        printAndLog('BEGINEXPERIMENT', {'networksize': networksize})
        printAndLog('MACMOTEID{}'.format(networksize), getAllMote(mgr1))

        # manager 1 subscribes network information
        print 'manager subscribes network info'
        self.mgrsub = IpMgrSubscribe.IpMgrSubscribe(self.mgr1)
        self.mgrsub.start()
        self.mgrsub.subscribe(
            notifTypes =    IpMgrSubscribe.IpMgrSubscribe.ALLNOTIF,
            fun =           handle_mgr_notif,
            isRlbl =        False,
        )

        # blink mote listens txDone
        print 'blink mote tracks txDone'

        mynotifListener   = NotifListener (
                          tag,
                          handle_mote_notif,
                          mote_disconnection,
                          )
        mynotifListener.start()

        print 'manager and blink heard blink now !!!'
        
        # blink transactions, tag sends the packets
        for t in range(10):
            
            # blink packets
            for p in range(100):
                print 'send packet {0} of transaction {1}'.format(p,t)
                try:
                    payLoadBlink = 'Size{0}_{1}{2}_{3}'.format(networksize, p, t, time.time())
                    res = self.tag.dn_blink(
                        fIncludeDscvNbrs = 1,
                        payload          = [ord(i) for i in payLoadBlink],
                    )
                    issueTime = datetime.datetime.now()
                    print 'blink request packet {}'.format(payLoadBlink)
                except Exception as err:
                    print 'could not send blink packet: {0}\n'.format(err)
                
                print "...waiting for packet sent notification \n",

                while not NotifEventDone.is_set():
                    print '!',
                    time.sleep(1)
                NotifEventDone.clear()
        printAndLog('ENDEXPERIMENT', {'networksize': networksize})
    
    def setDefaultConfig(self,):
        mote_list = [ALLMOTES[a] for a in range(len(ALLMOTES))] + [TAG_EUI]
        res1 = self.mgr1.dn_getNetworkInfo()
        res2 = self.mgr2.dn_getNetworkInfo()

        # create acl for all normal motes and blink motes in manager 1
        print 'set all acls in manager 1 !\n'

        for m in mote_list:
            self.mgr1.dn_setACLEntry(
                macAddress   = m,
                joinKey      = [ord(b) for b in 'DUSTNETWORKSROCK'], 
                           
            )
            self.mgr2.dn_setACLEntry(
                macAddress   = m,
                joinKey      = [ord(b) for b in 'DUSTNETWORKSROCK'],
            )   
        
        for i in range(len(ALLMOTES)):
            print 'Mote {}: {}'.format(i+1, FormatUtils.formatMacString(ALLMOTES[i]))
        
        print '\n\nset all acls in manager 1 done!\n'

        time.sleep(10)

        print 'old network id from manager 1: {}'.format(self.mgr1.dn_getNetworkConfig().networkId)
        print 'old network id from manager 2: {}'.format(self.mgr2.dn_getNetworkConfig().networkId)
        print 'old network id from tag: {}'.format(self.tag.dn_getParameter_networkId().networkId)
        

        # set new network id for manager 1
        self.mgr1.dn_exchangeNetworkId(
            id = 1229
        )

        # set new network ID for tag
        self.tag.dn_setParameter_networkId(
            networkId = 1229
        )
        
        self.mgr2.dn_exchangeNetworkId(
            id = 1229
        )

        print 'new network id from manager 1 and tag: {}'.format(self.mgr1.dn_getNetworkConfig().networkId)
        print 'new network id from manager 2: {}'.format(self.mgr2.dn_getNetworkConfig().networkId)

        # reset all networks to apply new ID
        print 'change network id successfully and wait for manager to deliver the network id command to mote'

        # wait for manager deliver packet
        if res1.numMotes >= res2.numMotes:
            timeWait = (res1.numMotes)*30 + 45
        else:
            timeWait = (res2.numMotes)*30 + 45
        print 'waiting time is {}s'.format(timeWait)
        time.sleep(timeWait)
        
        self.mgr1.dn_reset(
                type       = 0,
                macAddress = [0x00]*8,
        )
        
        self.tag.dn_reset()
        
        self.mgr2.dn_reset(
                type       = 0,
                macAddress = [0x00]*8,
        )   

        time.sleep(1)           

        print 'reset all networks done and wait for 45s to change network id in the motes !'

        self.mgr1.disconnect()
        self.mgr2.disconnect()
        self.tag.disconnect()        

        time.sleep(30)
        
        self.mgr1.connect({'port': SERIALPORT_MGR_1})
        self.mgr2.connect({'port': SERIALPORT_MGR_2})
        self.tag.connect({'port': SERIALPORT_TAG})

        print 'connect manager 1, 2 and blink mote again done!'

        print '\n\n\ncurrent network id from manager 1: {}'.format(self.mgr2.dn_getNetworkConfig().networkId)
        print 'current network id from manager 2: {}'.format(self.mgr2.dn_getNetworkConfig().networkId)
        print 'current network id from tag: {}'.format(self.tag.dn_getParameter_networkId().networkId)

        time.sleep(1)

# Motes listen TxDone
class NotifListener(threading.Thread):
    
    def __init__(self,connector,notifCb,disconnectedCb):
    
        # record variables
        self.connector       = connector
        self.notifCb         = notifCb
        self.disconnectedCb  = disconnectedCb
        
        # init the parent
        threading.Thread.__init__(self)
        
        # give this thread a name
        self.name            = 'NotifListener'
        
    #======================== public ==========================================
    
    def run(self):
        keepListening = True
        while keepListening:
            try:
                input = self.connector.getNotificationInternal(-1)
            except (ConnectionError,QueueError) as err:
                keepListening = False
            else:
                if input:
                    self.notifCb(input)
                else:
                    keepListening = False
        self.disconnectedCb()


#============================ main ============================================

def main():
    blinklab = BlinkLab()
    blinklab.join()
    mgr1.disconnect()
    mgr2.disconnect()
    tag.disconnect()
    raw_input("Script ended successfully. Press Enter to close.")

if __name__=="__main__":
    main()

