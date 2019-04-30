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

from SmartMeshSDK.IpMgrConnectorSerial  import IpMgrConnectorSerial
from SmartMeshSDK.IpMoteConnector       import IpMoteConnector

#============================ defines =========================================

SERIALPORT_MGR          = 'COM95'
SERIALPORT_TAG          = 'COM91'
ALLMOTES                = [
    '00-00-00-00-00-00-00-00',
    '00-00-00-00-00-00-00-00',
    '00-00-00-00-00-00-00-00',
    '00-00-00-00-00-00-00-00',
    '00-00-00-00-00-00-00-00',
]

#============================ Functions ============================================

class BlinkLab(threading.Thread):
    
    def __init__(self):
    
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
        
        for networksize in range(5,46,5):
            self.runExperimentForSize(networksize)
    
    #======================== private ==========================================
    
    def runExperimentForSize(self,networksize):
        print 'TODO runExperimentForSize {0}'.format(networksize)
        
        # configure the manager's ACL
        for m in range(networksize):
            self.mgr.dn_setACLEntry(
                macAddress   = ALLMOTES[m],
                joinKey      = [ord(b) for b in 'DUSTNETWORKSROCK'],
            )
        
        # reset the network (reset sytstem)
        self.mgr.dn_reset(
            type       = 'resetSystem',
            macAddress = [0x00]*8,
        )
        
        # wait for network to form
        while True:
            res = self.mgr.dn_getNetworkInfo()
            if res.numMotes==networksize:
                break
            time.sleep(1)
        
        # blink transactions
        for t in range(100):
            
            # blink packets
            for p in range(10):
                print 'send packet {0} of transaction {1}'.format(p,t)
                self.tag.blink(
                    fIncludeDscvNbrs = 1,
                    payload          = [t,p],
                )

#============================ main ============================================

def main():
    blinklab = BlinkLab()
    blinklab.join()
    raw_input("Script ended successfully. Press Enter to close.")

if __name__=="__main__":
    main()


