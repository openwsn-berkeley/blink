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

NETID_EXPERIMENT        = 601
NETID_HIDING            = 602
NETID_PARKED            = 603

SERIALPORT_MGR1         = 'COM7'
SERIALPORT_MGR2         = 'COM15'
SERIALPORT_TAG          = 'COM11'

TAG_EUI                 = [0, 23, 13, 0, 0, 56, 7, 12]
ALLMOTES                = [
    [0, 23, 13, 0, 0, 49, 198, 161],
    [0, 23, 13, 0, 0, 49, 213, 31], 
    [0, 23, 13, 0, 0, 49, 203, 229],
    [0, 23, 13, 0, 0, 49, 194, 249],
    [0, 23, 13, 0, 0, 49, 209, 112],
    [0, 23, 13, 0, 0, 49, 213, 1],
]

TIMEOUT_EXCHANGENETID   = 120
TIMEOUT_RESETMGRID      = 30

#============================ helpers =========================================

fileLock = threading.RLock() 

def printAndLog(msg_type, msg, firstline = False):
    global fileLock
    
    # print
    
    output = []
    if msg_type=='CMD':
        if   msg['serialport']==SERIALPORT_MGR1:
            mgr = 'MGR1'
        elif msg['serialport']==SERIALPORT_MGR2:
            mgr = 'MGR2'
        if   msg['cmd']=='dn_exchangeNetworkId':
            notes = 'networkId={0}'.format(msg['params']['id'])
        elif msg['cmd']=='dn_setNetworkConfig':
            notes = 'networkId={0}'.format(msg['params']['networkId'])
        elif msg['cmd']=='dn_getNeworkInfo':
            notes = 'numMotes={0}'.format(msg['res']['numMotes'])
        else:
            notes = ''
        output += ['{0} {1} {2} {3}'.format(msg_type, mgr, msg['cmd'], notes)]
    else:
        output += ['{0} {1}'.format(msg_type,msg)]
    output = '\n'.join(output)
    print output
    
    # log
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
        printAndLog('NOTIF', {'notifName': notifName, 'notifParams': notifParams})
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
        
        self.mgr = {}
        
        # connect to manager1
        self.mgr[SERIALPORT_MGR1] = IpMgrConnectorSerial.IpMgrConnectorSerial()
        self.mgr[SERIALPORT_MGR1].connect({'port': SERIALPORT_MGR1})
        
        # connect to manager2
        self.mgr[SERIALPORT_MGR2] = IpMgrConnectorSerial.IpMgrConnectorSerial()
        self.mgr[SERIALPORT_MGR2].connect({'port': SERIALPORT_MGR2})
        
        # connect to tag
        self.tag = IpMoteConnector.IpMoteConnector()
        self.tag.connect({'port':  SERIALPORT_TAG})
        
        for networksize in range(6,-1,-3):
            self.runExperimentForSize(networksize)
    
    #======================== private ==========================================
    
    def runExperimentForSize(self,networksize):
        
        # log
        printAndLog('NETWORKSIZE', {'networksize': networksize})
        
        #===== step 1. prepare network
        
        #=== MGR2 -> NETID_PARKED
        
        self.change_networkid_manager_and_reset(SERIALPORT_MGR2,NETID_PARKED)
        
        #=== configure and reset MGR1
        
        # clear ACL
        self.issue_manager_command(SERIALPORT_MGR1,"dn_deleteACLEntry", {"macAddress": [0x00]*8})
        
        # add ACL entries
        for m in [TAG_EUI]+[ALLMOTES[a] for a in range(networksize)]:
            self.issue_manager_command(SERIALPORT_MGR1,"dn_setACLEntry", {"macAddress": m, "joinKey": [ord(b) for b in 'DUSTNETWORKSROCK']})
        
        # MGR1 -> NETID_EXPERIMENT
        self.change_networkid_manager_and_reset(SERIALPORT_MGR1,NETID_EXPERIMENT)
        
        # subscribe to notifications
        '''
        self.mgr1sub = IpMgrSubscribe.IpMgrSubscribe(self.mgr1)
        self.mgr1sub.start()
        self.mgr1sub.subscribe(
            notifTypes =    IpMgrSubscribe.IpMgrSubscribe.ALLNOTIF,
            fun =           handle_mgr1_notif,
            isRlbl =        False,
        )
        '''
        
        #=== wait for networksize nodes to join MGR1
        
        while True:
            res = self.issue_manager_command(SERIALPORT_MGR1,"dn_getNetworkInfo")
            if res.numMotes==networksize:
                break
            time.sleep(1)
        
        #=== MGR1 (+network) -> NETID_HIDING
        
        self.change_networkid_network_and_reset(SERIALPORT_MGR1,NETID_HIDING)
        
        #=== MGR2 -> NETID_EXPERIMENT
        
        self.change_networkid_manager_and_reset(SERIALPORT_MGR2, NETID_EXPERIMENT)
        
        #=== wait for len(ALLMOTES)-networksize nodes to join MGR2
        
        while True:
            res = self.issue_manager_command(SERIALPORT_MGR2,"dn_getNetworkInfo") 
            if res.numMotes==len(ALLMOTES)-networksize:
                break
            time.sleep(1)
        
        #=== MGR2 (+network) -> NETID_PARKED
        
        self.change_networkid_network_and_reset(SERIALPORT_MGR2,NETID_PARKED)
        
        #=== MGR1 (+network) -> NETID_EXPERIMENT
        
        self.change_networkid_network_and_reset(SERIALPORT_MGR1,NETID_EXPERIMENT)
        
        #=== wait for networksize nodes to join MGR1
        
        while True:
            res = self.issue_manager_command(SERIALPORT_MGR1,"dn_getNetworkInfo")
            if res.numMotes==networksize:
                break
            time.sleep(1)
        
        # when you get here:
        # - networksize               motes are attached to MGR1
        # - len(ALLMOTES)-networksize motes are attached to MGR2
        
        #=== retrieve moteId/macAddress correspondance on MGR1
        
        # TODO
        
        raw_input(
            "\nWe should have {0} motes on MGR1 and {1} motes in MGR2. Press Enter to continue.\n".format(
                networksize,
                len(ALLMOTES)-networksize,
            )
        )
        
        #===== step 1. issue blink commands
        
        '''
        # blink transactions
        for t in range(10):
            
            # blink packets
            for p in range(10):
                
                resp = self.tag.dn_blink(
                    fIncludeDscvNbrs = 1,
                    payload          = [t,p],
                )
                
                time.sleep(5) # TODO wait for response
                
            # reset tag
            self.tag.dn_reset()
        '''
    
    def issue_manager_command(self,serialport,cmd,params=None):
        
        # issue
        if   params:
            res = getattr(self.mgr[serialport],cmd)(**params)
        else:
            res = getattr(self.mgr[serialport],cmd)()
        
        # log
        printAndLog('CMD',
            {
                "serialport":     serialport,
                "cmd":            cmd,
                "params":         params,
                "res":            res,
            }
        )
        
        return res
    
    def change_networkid_manager_and_reset(self, serialport, newnetid):
        
        # retrieve the current configuration
        res = self.issue_manager_command(serialport,"dn_getNetworkConfig")
        
        # set new configuration
        self.issue_manager_command(serialport,"dn_setNetworkConfig",
            {
                "networkId"            : newnetid, # changed
                "apTxPower"            : res.apTxPower,
                "frameProfile"         : res.frameProfile,
                "maxMotes"             : res.maxMotes, 
                "baseBandwidth"        : res.baseBandwidth, 
                "downFrameMultVal"     : res.downFrameMultVal, 
                "numParents"           : res.numParents, 
                "ccaMode"              : res.ccaMode, 
                "channelList"          : res.channelList, 
                "autoStartNetwork"     : res.autoStartNetwork, 
                "locMode"              : res.locMode, 
                "bbMode"               : res.bbMode, 
                "bbSize"               : res.bbSize, 
                "isRadioTest"          : res.isRadioTest, 
                "bwMult"               : res.bwMult, 
                "oneChannel"           : res.oneChannel
            }
        )
        
        # reset
        self.resetManager(serialport)
    
    def change_networkid_network_and_reset(self, serialport, newnetid):
        self.issue_manager_command(serialport,"dn_exchangeNetworkId", {"id": newnetid})
        time.sleep(TIMEOUT_EXCHANGENETID) # worst duration for dn_exchangeNetworkId to take effect
        self.resetManager(serialport)
    
    def resetManager(self,serialport):
        self.issue_manager_command(serialport,"dn_reset",
            {
                "type"                 : 0, # reset system: type = 0, reset specific motes: type= 2
                "macAddress"           : [0x00]*8,
            }
        )
        self.mgr[serialport].disconnect()
        time.sleep(TIMEOUT_RESETMGRID)
        self.mgr[serialport].connect({'port': serialport})

#============================ main ============================================

def main():
    blinklab = BlinkLab()
    blinklab.join()
    raw_input("Script ended successfully. Press Enter to close.")

if __name__=="__main__":
    main()
    