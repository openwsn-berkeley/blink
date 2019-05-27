#!/usr/bin/python

'''
Starting point:
- 2 managers
- 45 motes set to netid=NETID_EXPERIMENT
'''

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
import struct

from SmartMeshSDK.IpMgrConnectorSerial import IpMgrConnectorSerial
from SmartMeshSDK.IpMoteConnector      import IpMoteConnector
from SmartMeshSDK.IpMgrConnectorMux    import IpMgrSubscribe
from SmartMeshSDK.ApiException         import APIError
from SmartMeshSDK.protocols.blink      import blink

#============================ defines =========================================

NETID_EXPERIMENT        = 601
NETID_HIDING            = 602
NETID_PARKED            = 603

SERIALPORT_MGR1         = 'COM7'
SERIALPORT_MGR2         = 'COM15'
SERIALPORT_TAG          = 'COM11'

TAG_EUI                 = [0, 23, 13, 0, 0, 56, 7, 12]
ALLMOTES                = [
    [0x00,0x17,0x0D,0x00,0x00,0x31,0xCC,0x0F],
    [0x00,0x17,0x0D,0x00,0x00,0x31,0xC3,0x71],
    [0x00,0x17,0x0D,0x00,0x00,0x31,0xD1,0xAC],
    [0x00,0x17,0x0D,0x00,0x00,0x31,0xC3,0x3E],
    [0x00,0x17,0x0D,0x00,0x00,0x31,0xC1,0xA0],
    [0x00,0x17,0x0D,0x00,0x00,0x31,0xD1,0x5F],
    [0x00,0x17,0x0D,0x00,0x00,0x31,0xD1,0xD3],
    [0x00,0x17,0x0D,0x00,0x00,0x31,0xCA,0x05],
    [0x00,0x17,0x0D,0x00,0x00,0x31,0xCA,0x03],
    [0x00,0x17,0x0D,0x00,0x00,0x31,0xC3,0x53],
    [0x00,0x17,0x0D,0x00,0x00,0x31,0xD5,0x01],
    [0x00,0x17,0x0D,0x00,0x00,0x31,0xC9,0xDA],


]
NUMNODESSTEP              = 4
NUMNODESEND               = -1

TIMEOUT_RESETMGRID        = 30
TIMEOUT_DROP_BLINK_PACKET = 120

#============================ helpers =========================================

fileLock = threading.RLock()

def serialport2mgr(serialport):
    if   serialport==SERIALPORT_MGR1:
        returnVal = 'MGR1'
    elif serialport==SERIALPORT_MGR2:
        returnVal = 'MGR2'
    elif serialport==SERIALPORT_TAG:
        returnVal = 'TAG'
    return returnVal

def printAndLog(msg_type, msg, firstline = False):
    global fileLock
    
    # print
    output = []
    if msg_type=='CMD':
        if   msg['cmd']=='dn_exchangeNetworkId':
            notes = 'networkId={0}'.format(msg['params']['id'])
        elif msg['cmd']=='dn_setNetworkConfig':
            notes = 'networkId={0}'.format(msg['params']['networkId'])
        elif msg['cmd']=='dn_getNetworkInfo':
            notes = 'numMotes={0}'.format(msg['res'].numMotes)
        else:
            notes = ''
        output += ['{0} {1:>6} {2} {3}'.format(serialport2mgr(msg['serialport']), msg_type, msg['cmd'], notes)]
    elif msg_type=='NOTIF':
        notes   = ''
        output += ['{0} {1:>6} {2} {3}'.format(serialport2mgr(msg['serialport']), msg_type, msg['notifName'], notes)]
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
        with open('blinkLab.txt', filemode) as f:
            f.write(
                json.dumps({
                    'timestamp': time.time(),
                    'type'     : msg_type,
                    'msg'      : msg,
                })+ '\n'
            )

def handle_mgr1_notif(notifName, notifParams):
    BlinkLab().handle_mgr_notif(SERIALPORT_MGR1, notifName, notifParams)

def handle_mgr2_notif(notifName, notifParams):
    BlinkLab().handle_mgr_notif(SERIALPORT_MGR2, notifName, notifParams)

#============================ classes =========================================

class BlinkLab(threading.Thread):
    _instance = None
    _init     = False
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(BlinkLab, cls).__new__(cls, *args, **kwargs)
        return cls._instance
    
    def __init__(self):
        
        # singleton
        if self._init:
            return
        self._init = True
        
        # log
        printAndLog('START', '', firstline = True)
        
        # init the parent
        threading.Thread.__init__(self)
        self.name            = 'BlinkLab'
        self.start()
        
    #======================== public ==========================================
    
    def run(self):
        
        self.dataLock                  = threading.RLock()
        self.mgr                       = {}
        self.mgrsub                    = {}
        self.lastCommandFinished       = {
            SERIALPORT_MGR1: None,
            SERIALPORT_MGR2: None,
        }
        self.previousNetworkSize       = None
        self.last_blink_payload        = None

        # connect and subscribe to manager1
        self.mgr[SERIALPORT_MGR1] = IpMgrConnectorSerial.IpMgrConnectorSerial()
        self.mgr[SERIALPORT_MGR1].connect({'port': SERIALPORT_MGR1})
        self.subscribeManager(SERIALPORT_MGR1)
        
        # connect and subscribe manager2
        self.mgr[SERIALPORT_MGR2] = IpMgrConnectorSerial.IpMgrConnectorSerial()
        self.mgr[SERIALPORT_MGR2].connect({'port': SERIALPORT_MGR2})
        #disable manager 2 subscribe feature
        #self.subscribeManager(SERIALPORT_MGR2)
        
        # connect to tag
        self.tag = IpMoteConnector.IpMoteConnector()
        self.tag.connect({'port':  SERIALPORT_TAG})
        
        for networksize in range(len(ALLMOTES), NUMNODESEND, -NUMNODESSTEP):
            self.runExperimentForSize(networksize)
        #self.send_blink_transactions(0, 10, 10)
    
    def handle_mgr_notif(self, serialport, notifName, notifParams):
        try:
            printAndLog('NOTIF', {'serialport': serialport, 'notifName': notifName, 'notifParams': notifParams})
            if notifName=='eventCommandFinished':
                with self.dataLock:
                    self.lastCommandFinished[serialport] = struct.unpack('>I',''.join([chr(b) for b in notifParams.callbackId]))[0]
            if notifName=='notifData' and notifParams.srcPort == 61616:
                    try:
                        payload     = ''.join([chr(b) for b in notifParams.data])
                        blinkdata,blinkneighbors = blink.decode_blink(payload)
                    except Exception as err:
                        print err
                        raise
                    else:
                        with self.dataLock:
                            self.last_blink_payload = blinkdata.encode('hex')
        except Exception as err:
            print err
    
    #======================== private ==========================================
    
    def runExperimentForSize(self,networksize):
        
        # log
        printAndLog('NETWORKSIZE', {'networksize': networksize})
        
        ##################### step 1. prepare network
        
        #=== MGR2 -> NETID_PARKED
        
        self.change_networkid_manager_and_reset(SERIALPORT_MGR2,NETID_PARKED)
        
        #=== configure and reset MGR1
        
        # ACL
        self.issue_command(SERIALPORT_MGR1,"dn_deleteACLEntry", {"macAddress": [0x00]*8})
        for m in [TAG_EUI]+[ALLMOTES[a] for a in range(networksize)]:
            self.issue_command(SERIALPORT_MGR1,"dn_setACLEntry", {"macAddress": m, "joinKey": [ord(b) for b in 'DUSTNETWORKSROCK']})
        
        # MGR1 -> NETID_EXPERIMENT
        self.change_networkid_manager_and_reset(SERIALPORT_MGR1,NETID_EXPERIMENT)
        
        #=== wait for networksize nodes to join MGR1
        
        while True:
            res = self.issue_command(SERIALPORT_MGR1,"dn_getNetworkInfo")
            if res.numMotes==networksize:
                break
            time.sleep(1)
        
        #=== MGR1 (+network) -> NETID_HIDING
        
        self.change_networkid_network_and_reset(SERIALPORT_MGR1,NETID_HIDING)
        
        #=== MGR2 -> NETID_EXPERIMENT
        
        self.change_networkid_manager_and_reset(SERIALPORT_MGR2, NETID_EXPERIMENT)
        
        #=== wait for nodes that couldn't join MGR1 to join MGR2
        
        if self.previousNetworkSize == None:
            numMotesToMoveToParked = 0
        else:
            numMotesToMoveToParked = self.previousNetworkSize-networksize
        self.previousNetworkSize = networksize
        while True:
            res = self.issue_command(SERIALPORT_MGR2,"dn_getNetworkInfo")
            if res.numMotes==numMotesToMoveToParked:
                break
            time.sleep(1)
        
        #=== MGR2 (+network) -> NETID_PARKED
        
        self.change_networkid_network_and_reset(SERIALPORT_MGR2,NETID_PARKED)
        
        #=== wait for networksize nodes to join MGR1 (on NETID_HIDING)
        
        while True:
            res = self.issue_command(SERIALPORT_MGR1,"dn_getNetworkInfo")
            if res.numMotes==networksize:
                break
            time.sleep(1)
        
        #=== MGR1 (+network) -> NETID_EXPERIMENT
        
        self.change_networkid_network_and_reset(SERIALPORT_MGR1,NETID_EXPERIMENT)
        
        #=== wait for networksize nodes to join MGR1 (on NETID_EXPERIMENT)
        
        while True:
            res = self.issue_command(SERIALPORT_MGR1,"dn_getNetworkInfo")
            res2 = self.issue_command(SERIALPORT_MGR2,"dn_getNetworkInfo")
            if (res.numMotes==networksize and res2.numMotes == len(ALLMOTES)-networksize):
                break
            time.sleep(1)
        
        # when you get here:
        # - networksize               motes are attached to MGR1 on NETID_EXPERIMENT
        # - len(ALLMOTES)-networksize motes are attached to MGR2 on NETID_PARKED
        
        #=== retrieve moteId/macAddress correspondance on MGR1
        
        currentMac      = (0,0,0,0,0,0,0,0) 
        while True:
            try:
                res     = self.issue_command(SERIALPORT_MGR1,"dn_getMoteConfig", {"macAddress": currentMac, "next": True})
            except APIError:
                break # end of list
            else:
                currentMac = res.macAddress

        #=== send blink transaction
        
        self.send_blink_transactions(networksize, 2, 10)
    
    def issue_command(self,serialport,cmd,params=None):
        
        # find device
        if  serialport in [SERIALPORT_MGR1,SERIALPORT_MGR2]:
            device = self.mgr[serialport]
        elif serialport==SERIALPORT_TAG:
            device = self.tag
        else:
            raise SystemError()
        
        # issue
        if params:
            res = getattr(device,cmd)(**params)
        else:
            res = getattr(device,cmd)()
        
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
        res = self.issue_command(serialport,"dn_getNetworkConfig")
        
        # set new configuration
        self.issue_command(serialport,"dn_setNetworkConfig",
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
        res = self.issue_command(serialport,"dn_exchangeNetworkId", {"id": newnetid})
        while True:
            with self.dataLock:
                if self.lastCommandFinished[serialport]==res.callbackId:
                    break
            time.sleep(1)
        self.resetManager(serialport)
    
    def resetManager(self,serialport):
    
        # issue system reset command
        self.issue_command(serialport,"dn_reset",
            {
                "type"                 : 0, # reset system: type = 0, reset specific motes: type= 2
                "macAddress"           : [0x00]*8,
            }
        )
        self.mgr[serialport].disconnect()
        
        # clear the lastCommandFinished for that manager
        with self.dataLock:
            self.lastCommandFinished[serialport] = None
            self.last_blink_payload              = None
        
        # wait for motes to disconnect
        time.sleep(TIMEOUT_RESETMGRID)
        
        # reconnect and resubsribe to manager
        self.mgr[serialport].connect({'port': serialport})
        self.subscribeManager(serialport)
    
    def subscribeManager(self,serialport):
        self.mgrsub[serialport] = IpMgrSubscribe.IpMgrSubscribe(self.mgr[serialport])
        self.mgrsub[serialport].start()
        if   serialport==SERIALPORT_MGR1:
            fun = handle_mgr1_notif
        elif serialport==SERIALPORT_MGR2:
            fun = handle_mgr2_notif
        self.mgrsub[serialport].subscribe(
            notifTypes =    IpMgrSubscribe.IpMgrSubscribe.ALLNOTIF,
            fun =           fun,
            isRlbl =        False,
        )
    
    def send_blink_transactions(self, networksize, num_transactions, num_packets):
        
        for t in range(num_transactions):
        
            for p in range(num_packets):
                # update timeout, when tag can drop packet
                timeout_drop_blink = 0
                
                # issue blink
                resp = self.issue_command(SERIALPORT_TAG, "dn_blink", {"fIncludeDscvNbrs": 1, "payload":[networksize, t, p]})
                blink_payload     = ''.join([chr(b) for b in [networksize, t, p]])
                
                while True:
                    with self.dataLock:
                        if self.last_blink_payload == blink_payload.encode('hex'):
                            break
                    time.sleep(1)
                    timeout_drop_blink += 1
                    if timeout_drop_blink == TIMEOUT_DROP_BLINK_PACKET:
                        break

            # reset tag at end of each transaction
            self.tag.dn_reset()
            time.sleep(3)
            self.tag.disconnect()
            time.sleep(20)
            self.tag.connect({'port': SERIALPORT_TAG})

#============================ main ============================================

def main():
    blinklab = BlinkLab()
    blinklab.join()
    raw_input("Script ended successfully. Press Enter to close.")

if __name__=="__main__":
    main()
