#!/usr/bin/python

''' BlinkPacketSend

This scipt will connect to a mote via serial port, then issue a Blink command
It will then wait for a txDone notification signalling that the packet has left
the mote queue and is in the network. Calling this with -p X will send X packets
one after the other, waiting for txDone between each one.

Command line options include
   -c | --com to specify the COM port
   -n | --neighbors to send the packet with or without the discovered neighbors
   -p | --packets to specify how many packets to send
   -l | --location of Blink mote to send blink packet 
   -h | --help 
   Example:   BlinkPacketSend.py -c COM11 -n 0 -p 2 -l Lab-room
''' 
#============================ adjust path =====================================

import sys
import os
if __name__ == "__main__":
    here = sys.path[0]
    sys.path.insert(0, os.path.join(here, '..', '..','libs'))
    sys.path.insert(0, os.path.join(here, '..', '..','external_libs'))
    
#============================ imports =========================================

import threading
import traceback
import time
import json
import datetime
import random

from SmartMeshSDK                       import sdk_version
from SmartMeshSDK.IpMoteConnector       import IpMoteConnector
from SmartMeshSDK.ApiException          import APIError,                   \
                                               ConnectionError,            \
                                               QueueError

#============================ defines =========================================

UDP_PORT_NUMBER         = 60000
ROOMID = {'A111': 21, 'A110': 20, 'A113': 23, 'A112': 22, 'A115': 25, 'A114': 24, 'A117': 27, 'A116': 26, 'A119': 29, 'A118': 28, 'A303': 73, 'A326': 96, 'A310': 80, 'A305': 75, 'A212': 52, 'A120': 30, 'A210': 50, 'A211': 51, 'A216': 56, 'A217': 57, 'A214': 54, 'A215': 55, 'A312': 82, 'A218': 58, 'A219': 59, 'A207': 47, 'A319': 89, 'A315': 85, 'A316': 86, 'A206': 46, 'A302': 72, 'A328': 98, 'A201': 41, 'A327': 97, 'A309': 79, 'A121': 31, 'A323': 93, 'A203': 43, 'A311': 81, 'A301': 71, 'A127': 37, 'A318': 88, 'A308': 78, 'A106': 16, 'A107': 17, 'A104': 14, 'A105': 15, 'A102': 12, 'A103': 13, 'A101': 11, 'A324': 94, 'A320': 90, 'A314': 84, 'A108': 18, 'A109': 19, 'A304': 74, 'A226': 66, 'A225': 65, 'A224': 64, 'A209': 49, 'A208': 48, 'A221': 61, 'A220': 60, 'A205': 45, 'A204': 44, 'A122': 32, 'A123': 33, 'A124': 34, 'A125': 35, 'A126': 36, 'A202': 42, 'A317': 87, 'A325': 95, 'A213': 53, 'A306': 76, 'A321': 91, 'A307': 77, 'A223': 63, 'A313': 83, 'A322': 92, 'A222': 62}

#============================ Functions ============================================
global data
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

def mynotifIndication(my_notif):
    # Check for txDone notification, then print status information
    print_and_log('NOTIF', {'txMsg': my_notif, 'payload': data})
    NotifEventDone.set()

def mydisconnectedIndication():
    print 'Mote was disconnected\n'

def print_and_log(msg_type, msg, firstline = False):
    # for printing

    # for logging
    if firstline:
        writing_mode = 'w'
    else:
        writing_mode = 'a'
    with open('expr2_blink_log.txt', writing_mode) as f:
        f.write(
                json.dumps({
                    'timestamp': time.time(),
                    'type'     : msg_type,
                    'msg'      : msg,
                })+ '\n'
        )

#============================ command line options=============================
import optparse

parser = optparse.OptionParser(usage="usage: %prog [options]")
parser.add_option("-r", "--roomid", dest='roomid', default= 'A102',
                  help="Enter location of Blink mote to send packets") # room A127 is encoded 37
(options, args) = parser.parse_args()

#============================ main ============================================

try:
    print 'BlinkPacketSend (c) Dust Networks'
    print 'SmartMesh SDK {0}\n'.format('.'.join([str(b) for b in sdk_version.VERSION]))
    
    print 'sending 10 packets with discovered netighbore 1 {0}\n'.format(options)
    
    #=====

    moteconnector  = IpMoteConnector.IpMoteConnector()
    moteconnector.connect({'port': 'COM11'})

    # start a NotifListener
    NotifEventDone = threading.Event()
    mynotifListener   = NotifListener (
                          moteconnector,
                          mynotifIndication,
                          mydisconnectedIndication,
                          )
    mynotifListener.start()

    #=====
    transid = 1
    for packetid in range(10):
        try:
            data = [ROOMID[options.roomid], transid, packetid+1]
            resp = moteconnector.dn_blink(
                fIncludeDscvNbrs    = 1,
                payload             = data,
            )
            print_and_log('CMD',{'cmd':'dn_blink', 'params':{'fIncludeDscvNbrs': 1, 'payload': data}, 'res': resp},)
            print ("\n...Blink mote requested sending packet----> {}".format(data))
        except Exception as err:
            print ("Could not execute dn_blink: {0}\n".format(err))
        print "...Waiting for packet sent notification",       
        while not NotifEventDone.is_set():
            time.sleep(1)
        NotifEventDone.clear()
    # reset tag after each experiment
    time.sleep(3)
    moteconnector.dn_reset()
    time.sleep(10)
    moteconnector.disconnect()
    raw_input ('Press any key to stop\n\n')
    print 'Script ended normally.'

except Exception as err:
    output  = []
    output += ["Script ended with an error!"]
    output += [""]
    output += ["======== exception ==========="]
    output += [""]
    output += [str(err)]
    output += [""]
    output += ["======== trace ==============="]
    output += [""]
    output += [traceback.format_exc()]
    output += ["=============================="]
    output += [""]
    output  = '\n'.join(output)
    print output
    
    tout = 10
    while tout:
        print 'closing in {0} s...'.format(tout)
        time.sleep(1)
        tout -= 1
    sys.exit()
