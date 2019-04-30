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

SERIALPORT_MGR          = '/dev/ttyUSB3'
SERIALPORT_TAG          = '/dev/ttyUSB8'

ALLMOTES                = [
    [0, 23, 13, 0, 0, 49, 193, 171],
    [0, 23, 13, 0, 0, 49, 204, 15],
    [0, 23, 13, 0, 0, 49, 195, 71],
    [0, 23, 13, 0, 0, 49, 213, 59],
    [0, 23, 13, 0, 0, 49, 201, 230]
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
                #joinKey      = [68, 85, 83, 84, 78, 69, 84, 87, 79, 82, 75, 83, 82, 79, 67, 75] # default key
            )
        
        # reset the network (reset sytstem: type = 0, reset specific motes: type= 2)
        self.mgr.dn_reset(
            type       = 0,
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
                self.tag.dn_blink(
                    fIncludeDscvNbrs = 1,
                    payload          = [t,p],
                )
            # Reset blink mote after 10 packets
            self.tag.dn_reset()

#============================ main ============================================

def main():
    blinklab = BlinkLab()
    blinklab.join()
    raw_input("Script ended successfully. Press Enter to close.")

if __name__=="__main__":
    main()



