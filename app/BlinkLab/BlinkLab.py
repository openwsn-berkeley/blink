'''
Starting point:
- 2 managers
- 45 motes set to netid=NETID1
'''

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

NETID_PRIMARY           = 601
NETID_SECONDARY         = 602

SERIALPORT_MGR1         = 'COM7'
SERIALPORT_MGR2         = 'COM15'
SERIALPORT_TAG          = 'COM11'

TAG_EUI                 = [0, 23, 13, 0, 0, 56, 7, 12]
ALLMOTES                = [
    0x00,0x17,0x0d,0x00,0x00,0x31,0xc6,0xa1,
    0x00,0x17,0x0d,0x00,0x00,0x31,0xd1,0x70,
    0x00,0x17,0x0d,0x00,0x00,0x31,0xc2,0xf9, 
    0x00,0x17,0x0d,0x00,0x00,0x31,0xcb,0xe5 ,
    0x00,0x17,0x0d,0x00,0x00,0x31,0xd5,0x1f ,
    0x00,0x17,0x0d,0x00,0x00,0x31,0xd5,0x01 ,
    #[0, 23, 13, 0, 0, 49, 201, 230], 
    #[0, 23, 13, 0, 0, 49, 202, 3], 
    #[0, 23, 13, 0, 0, 49, 209, 95], 
    #[0, 23, 13, 0, 0, 49, 213, 103], 
    #[0, 23, 13, 0, 0, 49, 213, 106], 
    #[0, 23, 13, 0, 0, 49, 213, 48], 
    #[0, 23, 13, 0, 0, 49, 202, 5], 
    #[0, 23, 13, 0, 0, 49, 204, 46], 
    #[0, 23, 13, 0, 0, 49, 193, 161], 
    #[0, 23, 13, 0, 0, 49, 209, 112], 
    #[0, 23, 13, 0, 0, 49, 213, 1], 
    #[0, 23, 13, 0, 0, 49, 204, 64], 
    #[0, 23, 13, 0, 0, 49, 199, 176], 
    #[0, 23, 13, 0, 0, 49, 201, 241], 
    #[0, 23, 13, 0, 0, 49, 213, 32], 
    #[0, 23, 13, 0, 0, 49, 209, 172], 
    #[0, 23, 13, 0, 0, 49, 198, 184], 
    #[0, 23, 13, 0, 0, 49, 195, 55], 
    #[0, 23, 13, 0, 0, 49, 194, 249], 
    #[0, 23, 13, 0, 0, 49, 204, 88], 
    #[0, 23, 13, 0, 0, 49, 195, 83], 
    #[0, 23, 13, 0, 0, 49, 203, 229], 
    #[0, 23, 13, 0, 0, 49, 209, 50], 
    #[0, 23, 13, 0, 0, 49, 193, 160], 
    #[0, 23, 13, 0, 0, 49, 212, 126], 
    #[0, 23, 13, 0, 0, 49, 195, 113], 
    #[0, 23, 13, 0, 0, 49, 209, 211], 
    #[0, 23, 13, 0, 0, 49, 193, 193], 
    #[0, 23, 13, 0, 0, 49, 195, 62], 
    #[0, 23, 13, 0, 0, 49, 213, 31], 
    #[0, 23, 13, 0, 0, 49, 209, 168], 
    #[0, 23, 13, 0, 0, 49, 195, 25], 
    #[0, 23, 13, 0, 0, 49, 199, 222], 
    #[0, 23, 13, 0, 0, 49, 203, 231], 
    #[0, 23, 13, 0, 0, 49, 204, 89], 
    #[0, 23, 13, 0, 0, 49, 198, 146], 
    #[0, 23, 13, 0, 0, 49, 213, 105], 
    #[0, 23, 13, 0, 0, 49, 199, 219], 
    #[0, 23, 13, 0, 0, 49, 213, 134], 
    #[0, 23, 13, 0, 0, 49, 213, 50], 
    #[0, 23, 13, 0, 0, 49, 195, 10],
]

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
                    'timestamp': time.time(),
                    'type'     : msg_type,
                    'msg'      : msg,
                })+ '\n'
            )
    
def handle_mgr1_notif(notifName, notifParams):
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
        
        # connect to manager1
        self.mgr1 = IpMgrConnectorSerial.IpMgrConnectorSerial()
        self.mgr1.connect({'port': SERIALPORT_MGR1})
        
        # connect to manager2
        self.mgr2 = IpMgrConnectorSerial.IpMgrConnectorSerial()
        self.mgr2.connect({'port': SERIALPORT_MGR2})
        
        # connect to tag
        self.tag = IpMoteConnector.IpMoteConnector()
        self.tag.connect({'port':  SERIALPORT_TAG})
        
        for networksize in range(6,-1,-3):
            self.runExperimentForSize(networksize)
    
    #======================== private ==========================================
    
    def runExperimentForSize(self,networksize):
        
        # log
        printAndLog('NEWNETWORKSIZE', {'networksize': networksize})
        
        #===== step 1. prepare network
        
        #=== move mgr2 to NETID_SECONDARY
        
        # change netid
        self.mgr2.dn_exchangeNetworkId(
            id = NETID_SECONDARY,
        )
        
        # reset manager
        self.resetManager(self.mgr2,SERIALPORT_MGR2)
        
        #=== configure and reset mgr1
        
        # change netid
        self.mgr1.dn_exchangeNetworkId(
            id = NETID_PRIMARY,
        )
        
        # configure ACL
        mote_list = [TAG_EUI]+[ALLMOTES[a] for a in range(networksize)]
        for m in mote_list:
            
            # log
            printAndLog('MNGCMD', {'cmd': 'dn_setACLEntry'})
            
            # call 
            self.mgr1.dn_setACLEntry(
                macAddress   = m,
                joinKey      = [ord(b) for b in 'DUSTNETWORKSROCK'],
            )
        
        # reset manager
        self.resetManager(self.mrg1,SERIALPORT_MGR1)
        
        self.mgr1sub = IpMgrSubscribe.IpMgrSubscribe(self.mgr1)
        self.mgr1sub.start()
        self.mgr1sub.subscribe(
            notifTypes =    IpMgrSubscribe.IpMgrSubscribe.ALLNOTIF,
            fun =           handle_mgr1_notif,
            isRlbl =        False,
        )
        
        #=== wait for networksize nodes to join mgr1
        
        while True:
            res = self.mgr1.dn_getNetworkInfo()
            print 'mgr1 networkSize={0}'.format(res.numMotes)
            if res.numMotes==networksize:
                break
            time.sleep(1)
        
        #=== move mrg2 to NETID_PRIMARY
        
        # change netid
        self.mgr2.exchangeNetworkId(
            id = NETID_PRIMARY,
        )
        
        # reset manager
        self.resetManager(self.mrg2,SERIALPORT_MGR2)
        
        #=== wait for len(ALLMOTES)-networksize nodes to join mgr2
        
        while True:
            res = self.mgr2.dn_getNetworkInfo()
            print 'mgr2 networkSize={0}'.format(res.numMotes)
            if res.numMotes==len(ALLMOTES)-networksize:
                break
            time.sleep(1)
        
        #=== move motes now attached to mgr2 to NETID_SECONDARY
        
        self.mgr2.dn_exchangeNetworkId(
            id = NETID_SECONDARY,
        )
        time.sleep(120) # worst duration for dn_exchangeNetworkId to take effect
        
        # reset manager
        self.resetManager(self.mrg2,SERIALPORT_MGR2)
        
        # when you get here:
        # - networksize               motes are attached to mgr1
        # - len(ALLMOTES)-networksize motes are attached to mgr2
        
        #=== retrieve moteId/macAddress correspondance on mgr1
        
        # TODO
        
        #===== step 1. issue blink commands
        
        # blink transactions
        for t in range(10):
            
            # blink packets
            for p in range(10):
                
                print 'send packet {0} of transaction {1}'.format(p,t)
                self.tag.dn_blink(
                    fIncludeDscvNbrs = 1,
                    payload          = [t,p],
                )
                
                time.sleep(5) # TODO wait for response
                
            # reset tag
            print 'self.tag.dn_reset()'
            self.tag.dn_reset()
    
    def resetManager(self,mgr,serialport):
        print 'mgr.dn_reset'
        mgr.dn_reset(
            type       = 0, # reset system: type = 0, reset specific motes: type= 2
            macAddress = [0x00]*8,
        )
        print 'mgr.disconnect()'
        mgr.disconnect()
        time.sleep(30)
        print 'mgr.connect()'
        mgr.connect({'port': serialport})

#============================ main ============================================

def main():
    blinklab = BlinkLab()
    blinklab.join()
    raw_input("Script ended successfully. Press Enter to close.")

if __name__=="__main__":
    main()
