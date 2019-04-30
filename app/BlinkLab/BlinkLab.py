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

from SmartMeshSDK.IpMgrConnectorSerial  import IpMgrConnectorSerial
from SmartMeshSDK.IpMoteConnector       import IpMoteConnector
from SmartMeshSDK.IpMgrConnectorMux     import IpMgrSubscribe

#============================ defines =========================================

SERIALPORT_MGR          = 'COM176'
SERIALPORT_TAG          = 'COM180'
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
    [0, 23, 13, 0, 0, 49, 199, 176], 
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
    [0, 23, 13, 0, 0, 49, 212, 126], 
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

def printAndLog(msg_type, msg, firstline = False):
    global fileLock
    print msg_type, msg
    if firstline:
        filemode = 'w'
    else:
        filemode = 'a'
    with fileLock:
        with open('blinkLlab.txt', filemode) as f:
            f.write(
                json.dumps({
                    'timestamp': 'poipoipoi',
                    'type'     : msg_type,
                    'msg'      : msg,
                })+ '\n'
            )
    
def handle_mgr_notif(notifName, notifParams):
    try:
        printAndLog('MGNNOTIF', {'notifName': notifName, 'notifParams': notifParams})
    except Exception as err:
        print err

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
        
        # connect to manager
        self.mgr = IpMgrConnectorSerial.IpMgrConnectorSerial()
        self.mgr.connect({'port': SERIALPORT_MGR})
        
        # connect to tag
        self.tag = IpMoteConnector.IpMoteConnector()
        self.tag.connect({'port': SERIALPORT_TAG})
        
        for networksize in range(5,6,5):
            self.runExperimentForSize(networksize)
    
    #======================== private ==========================================
    
    def runExperimentForSize(self,networksize):
        # log
        printAndLog('NEWNETWORKSIZE', {'networksize': networksize})
        
        # configure the manager's ACL
        mote_list = [TAG_EUI]+[ALLMOTES[a] for a in range(networksize)]
        for m in mote_list:
            
            # log
            printAndLog('MNGCMD', {'cmd': 'dn_setACLEntry'})
            
            # call 
            self.mgr.dn_setACLEntry(
                macAddress   = m,
                joinKey      = [ord(b) for b in 'DUSTNETWORKSROCK'],
                
            )
        
        # reset the network (reset sytstem: type = 0, reset specific motes: type= 2)
        print 'self.mgr.dn_reset'
        self.mgr.dn_reset(
            type       = 0,
            macAddress = [0x00]*8,
        )
        print 'self.mgr.disconnect()'
        self.mgr.disconnect()
        time.sleep(30)
        print 'self.mgr.connect()'
        self.mgr.connect({'port': SERIALPORT_MGR})
        
        self.mgrsub = IpMgrSubscribe.IpMgrSubscribe(self.mgr)
        self.mgrsub.start()
        self.mgrsub.subscribe(
            notifTypes =    IpMgrSubscribe.IpMgrSubscribe.ALLNOTIF,
            fun =           handle_mgr_notif,
            isRlbl =        False,
        )
        
        # wait for network to form
        while True:
            
            res = self.mgr.dn_getNetworkInfo()
            print 'size of network as parameter: {0}, res.numMotes={1}, {2}'.format(networksize,res.numMotes, res)
            if res.numMotes==networksize:
                break
            time.sleep(1)
        
        # blink transactions
        for t in range(1):
            
            # blink packets
            for p in range(1):
                print 'send packet {0} of transaction {1}'.format(p,t)
                self.tag.dn_blink(
                    fIncludeDscvNbrs = 1,
                    payload          = [t,p],
                )
                time.sleep(5)
                
            # reset tag
            print 'self.tag.dn_reset()'
            self.tag.dn_reset()

#============================ main ============================================

def main():
    blinklab = BlinkLab()
    blinklab.join()
    raw_input("Script ended successfully. Press Enter to close.")

if __name__=="__main__":
    main()



