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
mrg_blink_data = ['lAMLAQGVDQQAAckAC8EAD8EADdc=', 'lAMLAQKVDQQAAc4AD8MACdoABMs=', 'lAMLAQOVDQQAAckAD70AC7wACdk=', 'lAMLAQSVDQQAAcsAD74AC7kACdg=', 'lAMLAQWVDQQAAcsAC8IAD78ADds=', 'lAMLAQaVDQQAAcoAC78ACd8ADds=', 'lAMLAQeVDQQAAcsAD8cAC8EACd4=', 'lAMLAQiVDQQAAc4AC78AD7YACd4=', 'lAMLAQmVDQQAAccAD78AC74ACdg=', 'lAMLAQqVDQQAAc0AD8QAC8IACdo=', 'lAMMAQGVDQQAAc8AC8YAD78ADdI=', 'lAMMAQOVDQQAAdEAC8UAD74ACdc=', 'lAMMAQSVDQQAAc4AD7wAC7kACdc=', 'lAMMAQWVDQQAAcoAC8EAD7oADdk=', 'lAMMAQaVDQQAAcwAC8cAD8IADdg=', 'lAMMAQeVDQQAAcwAC8oAD8EACdY=', 'lAMMAQmVDQQAAcsAD7kACdkABNI=', 'lAMMAQqVDQQAAckAC8IAD7wADdc=', 'lAMNAQGVDQQAAcsAD7wAC7wAAtY=', 'lAMNAQKVDQQAC8YAAckABNEACc0=', 'lAMNAQOVDQQAAcwAD8MAC78ABNE=', 'lAMNAQWVDQQAAc4AD8QAC8IADdY=', 'lAMNAQaVDQQAAckAC7wAD7kABNI=', 'lAMNAQeVDQQAAc8AD8AAC8AADdM=', 'lAMNAQiVDQQAAcwAD8EAC8MACdU=', 'lAMNAQmVDQQAAc8AD8EAC74ADc4=', 'lAMNAQqVDQQAAcUAD74ACdcADdM=', 'lAMOAQGVDQQAAcgAC8IAD7YAAtM=', 'lAMOAQKVDQQAAcQAC70ACcgABbs=', 'lAMOAQOVDQQAAcgAC7sAD7QAAtM=', 'lAMOAQSVDQQAAccAC7sAD7cADdE=', 'lAMOAQWVDQQAAccAD7oAC64AAtQ=', 'lAMOAQaVDQQAAckAC8AAD7YACc8=', 'lAMOAQeVDQQAAccAC7kAD7YAAtM=', 'lAMOAQiVDQQAAcoAD7gAC7cADdA=', 'lAMOAQmVDQQAAcUAC7kAD7QABNI=', 'lAMOAQqVDQQAAckAD7gABNAABcc=', 'lAMPAQGVDQQAAcYAC7gAD7UACck=', 'lAMPAQKVDQQAAboAD7IAC7AAEdY=', 'lAMPAQSVDQQAAboAD7QAC68ABMo=', 'lAMPAQWVDQQAAcIAD7YAC7QAEdY=', 'lAMPAQaVDQQAAcMAC7cAD68ACc4=', 'lAMPAQeVDQQAAb8AC7UAD7IAEdw=', 'lAMPAQiVDQQAAb8AC7IACckAA8U=', 'lAMPAQmVDQQAAcQAC7sAD7cAEdo=', 'lAMPAQqVDQQAAb8AD7cAC7UAEdE=', 'lAMQAQGVDQQAAb4AD7YACcwAEcw=', 'lAMQAQKVDQQAAcEAD7sAC7IACdA=', 'lAMQAQOVDQQAD7sAAbsAC7cAEdU=', 'lAMQAQSVDQQAAbwAC7cAD7MACc0=', 'lAMQAQWVDQQAAcEAD7cAC7gACc4=', 'lAMQAQaVDQQAAcEAC7gAD7QACcw=', 'lAMQAQeVDQQAAboAC7YAD7QAEco=', 'lAMQAQiVDQQAAbwAC7kAD7kACdA=', 'lAMQAQmVDQQAAb4AD7oAC7MAEcs=', 'lAMQAQqVDQQAAcAAD7cAC7MACc8=', 'lAMRAQGVDQQAAboAC7kAD7UAEdI=', 'lAMRAQKVDQQAAb4AC70AD7IAEc0=', 'lAMRAQOVDQQAD7sAAbsAC7YAA8c=', 'lAMRAQSVDQQAC7oAAb0AD7QABMU=', 'lAMRAQWVDQQAAboAC7gAD7UAFcw=', 'lAMRAQaVDQQAC78AAbkAD7QAFco=', 'lAMRAQeVDQQAAbsAC7oAD7UAA8c=', 'lAMRAQiVDQQAAcAAD7wAC7oAA8Q=', 'lAMRAQmVDQQAC7sAD70AAb4AEdI=', 'lAMRAQqVDQQAAcAAC7sAD7cAAsk=', 'lAMSAQGVDQQAC70AAboAD7cAFcw=', 'lAMSAQKVDQQAAbsAD7kAC7gAFcs=', 'lAMSAQOVDQQAAbcAC7wAD7cACco=', 'lAMSAQSVDQQAC8AAD7UAAbYACsg=', 'lAMSAQWVDQQAAb4AD70AC7gACck=', 'lAMSAQaVDQQAAbwAD7kAC7YAFco=', 'lAMSAQeVDQQAD7wAC7kAAbYACc4=', 'lAMSAQiVDQQAAb4AD7wAC7wACcw=', 'lAMSAQmVDQQAAbkAD70AC7oAEc0=', 'lAMSAQqVDQQAC8AAD7oAAbsAFcw=', 'lAMTAQGVDQQAC7gAAbYAD7QAFdY=', 'lAMTAQKVDQQAAbwAD7oAFdUAA84=', 'lAMTAQOVDQQAC70AD7sAAbUAFdY=', 'lAMTAQSVDQQAAboAC7kAD7cAFdo=', 'lAMTAQWVDQQAC70AD7wAA8kAF8k=', 'lAMTAQaVDQQAAb0AD7cAC7MAFdE=', 'lAMTAQeVDQQAC78AAboAD7QAFdU=', 'lAMTAQiVDQQAAbwAD7wAC7gAFdU=', 'lAMTAQmVDQQAAbcAC7QAD7UAFdc=', 'lAMUAQGVDQQAD8UAAcAAC7cAFdM=', 'lAMUAQKVDQQAD70AC7sAAboAFdc=', 'lAMUAQOVDQQAD8MAC78AAb0AFdM=', 'lAMUAQSVDQQAAb0AD7gAC7gAA8I=', 'lAMUAQWVDQQAAb4AD74AC7gAFdc=', 'lAMUAQaVDQQAD74AAbwAC7gAFdo=', 'lAMUAQeVDQQAAbgAD7gAC7YAFdk=', 'lAMUAQiVDQQAAboAD7kAC7MAFdk=', 'lAMUAQmVDQQAD8EAAbwAC7oAFdQ=', 'lAMUAQqVDQQAAbsAD7sAC7gAFdQ=', 'lAMVAQGVDQQAD8kAAcUAC8EAFdI=', 'lAMVAQKVDQQAAcUAD8gAC8UAB9I=', 'lAMVAQOVDQQAC8YAD8YAAcIAA9E=', 'lAMVAQSVDQQAAcYAD8gAC8MAA9Q=', 'lAMVAQWVDQQAD8cAC8YAAcMAA9c=', 'lAMVAQaVDQQAAccAC78AD8IAA9Q=', 'lAMVAQeVDQQAC78AD78AAb0AFdU=', 'lAMVAQiVDQQAD8sAAcMAC8EAGdE=', 'lAMVAQmVDQQAD8oAAcMAC8AAB9E=', 'lAMVAQqVDQQAD8gAAcUAC78AA9U=', 'lAMWAQGVDQQAD8cAC8QAAcIAGdY=', 'lAMWAQKVDQQAD8sAAcQAC8QAGdc=', 'lAMWAQOVDQQAAckAD8gAC8IAGdY=', 'lAMWAQSVDQQAD8wAC8gAAcMAA9U=', 'lAMWAQWVDQQAD8cAAccAC8MACts=', 'lAMWAQaVDQQAC8YAD8cAAb0AA9A=', 'lAMWAQeVDQQAD8oAC8MAAb4AGdY=', 'lAMWAQiVDQQAD8sAC8UAAcEAGdg=', 'lAMWAQmVDQQAD8sAAcUAC8MAGdU=', 'lAMWAQqVDQQAD8oAC8gAAb8AF8Q=', 'lAMXAQGVDQQAD80AC8YAAbcAB9c=', 'lAMXAQKVDQQAD88AC8QAAcAACtc=', 'lAMXAQOVDQQAD84AAbwAC8cAGdY=', 'lAMXAQSVDQQAD9AAC8cAAb0AB9s=', 'lAMXAQWVDQQAD80AC8oAAcMAGdk=', 'lAMXAQaVDQQAD88AC8cAAb0AGds=', 'lAMXAQeVDQQAD88AAcEAC74AB9E=', 'lAMXAQiVDQQAD8kAC8kAAccAFdA=', 'lAMXAQmVDQQAD9EAC8UAAbQACtU=', 'lAMXAQqVDQQAD9IAC8MAAcQAB9o=', 'lAMYAQGVDQQAD9AAC8kAAb0AA9Q=', 'lAMYAQKVDQQAD8oAC8gAAcUAGdQ=', 'lAMYAQOVDQQAD8wAC8kAAcAAB9k=', 'lAMYAQSVDQQAC84AD8oAAcMAB9c=', 'lAMYAQWVDQQAD8wAC8sAAcgAB9U=', 'lAMYAQaVDQQAD80AC80AAcUAB9c=', 'lAMYAQiVDQQAD88AC8wAAcUAB9o=', 'lAMYAQmVDQQAD9EAC8gAAcUAA84=', 'lAMYAQqVDQQAC8oAD8wAAccAGdY=', 'lAMZAQGVDQQAD9cAC9AAAc4AGdk=', 'lAMZAQKVDQQAD9cAC9EAAc0AB9o=', 'lAMZAQOVDQQAD9kAAc0AC8oAB9g=', 'lAMZAQSVDQQAD9oAC9IAAc8AB9c=', 'lAMZAQWVDQQAD9gAC9EAAcsACtY=', 'lAMZAQaVDQQAD9kAAc4AC80AB88=', 'lAMZAQeVDQQAD9kAC9UAAc0AGdA=', 'lAMZAQiVDQQAD9QAC9QAAc0AB9Y=', 'lAMZAQmVDQQAD9YAC9IAAc8AB9c=', 'lAMZAQqVDQQAD9IAC9AAAcsAGds=', 'lAMaAQGVDQQAD9cAC84AAcYAF9U=', 'lAMaAQKVDQQAD9kAC8wAAckAB94=', 'lAMaAQOVDQQAD9cAC8kAAcUAB9w=', 'lAMaAQSVDQQAD9MAAckAC8wAB9c=', 'lAMaAQWVDQQAD9cAC8oAAckAB9g=', 'lAMaAQaVDQQAD9sAC80AAcYAB9g=', 'lAMaAQeVDQQAD9oAC8wAAcQAB9c=', 'lAMaAQiVDQQAD9YAAcYAC8sAB84=', 'lAMaAQmVDQQAD9gAC8wAAcQAGdE=', 'lAMaAQqVDQQAD9gAAcgAC8kAB9Y=', 'lAMbAQGVDQQAD9kAAcoAC8oAF9M=', 'lAMbAQKVDQQAD9gAAc0AC8cAB9M=', 'lAMbAQOVDQQAD9sAAcwAC8kAB9M=', 'lAMbAQSVDQQAD9oAC8wAAcwAF9Q=', 'lAMbAQWVDQQAD9sAC8sAAcoAF9Q=', 'lAMbAQaVDQQAD9sAAcoAC8YAF88=', 'lAMbAQeVDQQAD9gAC8gAAcgAF9I=', 'lAMbAQiVDQQAD9gAC88AAc0AF9c=', 'lAMbAQmVDQQAD9sAC8wAAcoAF9M=', 'lAMbAQqVDQQAD9gAAckAC8kAB88=', 'lAMcAQGVDQQAC88AD9EAAcgAF8o=', 'lAMcAQKVDQQAD9QAC8gAAcMAF80=', 'lAMcAQOVDQQAD9MAAcYAC8EAB84=', 'lAMcAQSVDQQAD9UAC9AAAc0AB9M=', 'lAMcAQWVDQQAD9YAAcgAC8wAF9A=', 'lAMcAQaVDQQAD9QAC8kAAcgAB9E=', 'lAMcAQeVDQQAD9cAAcQAC8kAF9A=', 'lAMcAQiVDQQAD9UAAckAC8gAB8s=', 'lAMcAQmVDQQAD9MAC8gAAcYAGco=', 'lAMcAQqVDQQAD9QAC80AAcoAF88=', 'lAMdAQGVDQQAC9oAD9UAAdEACNI=', 'lAMdAQKVDQQAC9wAD9UAAdMAB8o=', 'lAMdAQOVDQQAC9wAD9MAAdAADMk=', 'lAMdAQSVDQQAC9wAD9QAAdAAGc4=', 'lAMdAQWVDQQAC9sAD9cAAdMAGcw=', 'lAMdAQaVDQQAC9wAD9gAAdEAF8w=', 'lAMdAQeVDQQAC98AD9YAAdEAGc8=', 'lAMdAQiVDQQAC9wAD9YAAdIAGdA=', 'lAMdAQmVDQQAC94AD9cAAdEAGc4=', 'lAMdAQqVDQQAC94AD9QAAdAAF8o=', 'lAMeAQGVDQQAC9sAAc8AD8wACNA=', 'lAMeAQKVDQQAC9YAAc0AD8kACNY=', 'lAMeAQOVDQQAC9sAAc4AD8kAF9E=', 'lAMeAQSVDQQAC9oAAc4AD80ACNY=', 'lAMeAQWVDQQAC9YAAdEAD8QACNY=', 'lAMeAQaVDQQAC9cAAdAAD8YACNY=', 'lAMeAQeVDQQAC9YAAdAAD8UACNE=', 'lAMeAQiVDQQAC9kAAc8AD8kACNQ=', 'lAMeAQmVDQQAC9gAAc4AD8cACNQ=', 'lAMeAQqVDQQAC9gAAc0AD8cACNQ=', 'lAMfAQGVDQQAC9cAAdQAD8wADNE=', 'lAMfAQKVDQQAC9cAAdQAD8oACNI=', 'lAMfAQOVDQQAC9QAAdcAD8wACNY=', 'lAMfAQSVDQQAAdcAC9EAD8MACNQ=', 'lAMfAQWVDQQAAc8AC9MAD8sACNU=', 'lAMfAQaVDQQAC9YAAdEAD8oACNc=', 'lAMfAQeVDQQAAdMAC9EAD8sACNY=', 'lAMfAQiVDQQAC9YAAdUAD80ACNY=', 'lAMfAQmVDQQAC9UAAdMAD8UADNE=', 'lAMfAQqVDQQAC9UAAdEAD8YACNg=', 'lAMgAQGVDQQAAdIAC9AAD8gACNQ=', 'lAMgAQKVDQQAC9AAD84AAc8ACNY=', 'lAMgAQOVDQQAC9MAAcwAD8oACNc=', 'lAMgAQSVDQQAC9EAAdEAD8oACNc=', 'lAMgAQWVDQQAC9QAAdAAD8oACNQ=', 'lAMgAQaVDQQAC9MAAc4AD8sACNQ=', 'lAMgAQeVDQQAAdIAC9EAD8oACM4=', 'lAMgAQiVDQQAAdIAC9IAD8wADNU=', 'lAMgAQmVDQQAC88AAc4AD8sACNM=', 'lAMgAQqVDQQAAc4AC8sAD8kACNY=', 'lAMhAQGVDQQAAdoAC8oAD8UABc4=', 'lAMhAQKVDQQAAdwAC8sAD8AADM4=', 'lAMhAQOVDQQAAdkAC80AD8QACdE=', 'lAMhAQSVDQQAAdoAC8oAD8YADNQ=', 'lAMhAQWVDQQAAdkAC8oAD8cAAtA=', 'lAMhAQaVDQQAAdwAC8wAD8gAAtA=', 'lAMhAQeVDQQAAdkAC80AD8cADNM=', 'lAMhAQiVDQQAAdwAC80AD8UABdA=', 'lAMhAQmVDQQAAdgAC80AD8IACc4=', 'lAMhAQqVDQQAAdgAC8wAD8UABc8=', 'lAMiAQGVDQQAAdIAC8gAD8UABdg=', 'lAMiAQKVDQQAC9AAAcsAD8cABdI=', 'lAMiAQOVDQQAAdYAC8wAD8QABdU=', 'lAMiAQSVDQQAAdAAC80AD8MABdE=', 'lAMiAQWVDQQAAdIAC88AD8UABNI=', 'lAMiAQaVDQQAC9EAAc4AD8YABdI=', 'lAMiAQeVDQQAAdYAC88AD8gABdU=', 'lAMiAQiVDQQAAdMAC9AAD8IABdY=', 'lAMiAQmVDQQAAdAAC9AAD8gABdY=', 'lAMiAQqVDQQAC9EAAdEAD8YACdM=', 'lAMjAQGVDQQAAc8AC8UAD8EABNg=', 'lAMjAQKVDQQAAdIAC8MAD7cABNk=', 'lAMjAQOVDQQAAc8AC8gAD8UABNs=', 'lAMjAQSVDQQAAc4AC8oAD8YABNw=', 'lAMjAQWVDQQAAdIAC8kAD8YAAtc=', 'lAMjAQaVDQQAAdcAC8oAD78ABNo=', 'lAMjAQeVDQQAAdgAC8cAD8MAAtw=', 'lAMjAQiVDQQAAdIAD8cAC8oABdk=', 'lAMjAQmVDQQAAdAAD8AAC7AABNw=', 'lAMjAQqVDQQAAdQAC8cAD8UABN0=', 'lAMkAQGVDQQAAdYAD8cAC8cABOI=', 'lAMkAQKVDQQAAdUAC8kAD8IABOM=', 'lAMkAQOVDQQAAdMAD8QAC8QABN8=', 'lAMkAQSVDQQAC8YAD8EABOAACdc=', 'lAMkAQWVDQQAAdMAC8YAD8MABN8=', 'lAMkAQaVDQQAAdMAC8cAD8IABOA=', 'lAMkAQeVDQQAAdQAD8EABOMABdE=', 'lAMkAQiVDQQAAdIAC8cAD78ABOM=', 'lAMkAQmVDQQAAdQAC8YAD8QABNw=', 'lAMkAQqVDQQAAdEAC8cAD7sABN0=', 'lAMlAQGVDQQAAc4AC8cAD7gADdg=', 'lAMlAQKVDQQAAdEAC8QAD7sABNo=', 'lAMlAQOVDQQAAdAAC8cABNsABdE=', 'lAMlAQSVDQQAAdIAC8cAD7wABOM=', 'lAMlAQWVDQQAAdAAC8IAD7sABOA=', 'lAMlAQaVDQQAAdAAC74AD7YABNw=', 'lAMlAQeVDQQAAdMAC8UAD70ABNs=', 'lAMlAQiVDQQAAc4AC8YAD7UABNw=', 'lAMlAQmVDQQAAc8AC8QAD8AABNg=', 'lAMlAQqVDQQAAdAAC8cABOIABdE=']

dict_mac_roomname = {'00-17-0D-00-00-31-C3-37': 'A125', '00-17-0D-00-00-38-06-67': 'A110', '00-17-0D-00-00-31-CC-0F': 'A320', '00-17-0D-00-00-31-C3-71': 'A315', '00-17-0D-00-00-31-D5-3B': 'A310', '00-17-0D-00-00-31-C1-AB': 'A313', '00-17-0D-00-00-31-C6-B8': 'A304', '00-17-0D-00-00-31-CC-58': 'A208', '00-17-0D-00-00-31-D5-20': 'A101', '00-17-0D-00-00-38-05-F1': 'A115', '00-17-0D-00-00-30-3E-09': 'A120W', '00-17-0D-00-00-31-C7-B0': 'A215', '00-17-0D-00-00-31-D1-A8': 'A328', '00-17-0D-00-00-38-05-E9': 'A109', '00-17-0D-00-00-31-D5-86': 'A327', '00-17-0D-00-00-31-C9-E6': 'A224', '00-17-0D-00-00-38-03-69': 'A111', '00-17-0D-00-00-38-06-F0': 'A116', '00-17-0D-00-00-38-03-CA': 'A103', '00-17-0D-00-00-58-2A-E8': 'A116W', '00-17-0D-00-00-31-C9-F1': 'A223', '00-17-0D-00-00-31-CC-40': 'A220', '00-17-0D-00-00-31-C1-A0': 'A211', '00-17-0D-00-00-38-05-DA': 'A107', '00-17-0D-00-00-38-06-AD': 'A105', '00-17-0D-00-00-31-C3-3E': 'A322', '00-17-0D-00-00-31-D5-30': 'A226', '00-17-0D-00-00-31-C3-19': 'A216', '00-17-0D-00-00-31-CA-03': 'A126', '00-17-0D-00-00-31-CA-05': 'A205', '00-17-0D-00-00-31-D5-1F': 'A203', '00-17-0D-00-00-38-04-3B': 'A120', '00-17-0D-00-00-31-C3-53': 'A210', '00-17-0D-00-00-38-06-C9': 'A123', '00-17-0D-00-00-31-D5-01': 'A309', '00-17-0D-00-00-31-D5-6A': 'A307', '00-17-0D-00-00-31-C1-A1': 'A301', '00-17-0D-00-00-38-04-25': 'A118', '00-17-0D-00-00-31-D1-D3': 'A318', '00-17-0D-00-00-31-C7-DE': 'A213', '00-17-0D-00-00-31-D1-AC': 'A204', '00-17-0D-00-00-58-2B-4F': 'A124W', '00-17-0D-00-00-31-D4-7E': 'A221', '00-17-0D-00-00-31-D5-69': 'A225', '00-17-0D-00-00-38-03-D9': 'A121', '00-17-0D-00-00-38-06-D5': 'A113', '00-17-0D-00-00-38-03-87': 'A104', '00-17-0D-00-00-31-D5-67': 'A207', '00-17-0D-00-00-31-C6-A1': 'A218', '00-17-0D-00-00-38-00-63': 'A124', '00-17-0D-00-00-31-D1-32': 'A303', '00-17-0D-00-00-31-CC-2E': 'A326', '00-17-0D-00-00-31-D1-70': 'A311', '00-17-0D-00-00-31-C9-DA': 'A316', '00-17-0D-00-00-31-CB-E7': 'A306', '00-17-0D-00-00-31-CB-E5': 'A201', '00-17-0D-00-00-31-C1-C1': 'A324'}

DICT_ACCESS_POINT = {'floor1':['00-17-0D-00-00-58-2A-E8', '00-17-0D-00-00-30-3E-09', '00-17-0D-00-00-58-2B-4F']}

dict_roomid_name = {11: 'A101', 12: 'A102', 13: 'A103', 14: 'A104', 15: 'A105', 16: 'A106', 17: 'A107', 18: 'A108', 19: 'A109', 20: 'A110', 21: 'A111', 22: 'A112', 23: 'A113', 24: 'A114', 25: 'A115', 26: 'A116', 27: 'A117', 28: 'A118', 29: 'A119', 30: 'A120', 31: 'A121', 32: 'A122', 33: 'A123', 34: 'A124', 35: 'A125', 36: 'A126', 37: 'A127', 41: 'A201', 42: 'A202', 43: 'A203', 44: 'A204', 45: 'A205', 46: 'A206', 47: 'A207', 48: 'A208', 49: 'A209', 50: 'A210', 51: 'A211', 52: 'A212', 53: 'A213', 54: 'A214', 55: 'A215', 56: 'A216', 57: 'A217', 58: 'A218', 59: 'A219', 60: 'A220', 61: 'A221', 62: 'A222', 63: 'A223', 64: 'A224', 65: 'A225', 66: 'A226', 71: 'A301', 72: 'A302', 73: 'A303', 74: 'A304', 75: 'A305', 76: 'A306', 77: 'A307', 78: 'A308', 79: 'A309', 80: 'A310', 81: 'A311', 82: 'A312', 83: 'A313', 84: 'A314', 85: 'A315', 86: 'A316', 87: 'A317', 88: 'A318', 89: 'A319', 90: 'A320', 91: 'A321', 92: 'A322', 93: 'A323', 94: 'A324', 95: 'A325', 96: 'A326', 97: 'A327', 98: 'A328'} # for all room

dict_roomid_name_for_all = {}

dict_moteid_mac = {1: '00-17-0D-00-00-58-2B-4F', 2: '00-17-0D-00-00-31-CA-03', 3: '00-17-0D-00-00-38-06-D5', 4: '00-17-0D-00-00-31-C3-37', 5: '00-17-0D-00-00-38-00-63', 6: '00-17-0D-00-00-38-05-E9', 7: '00-17-0D-00-00-38-06-F0', 8: '00-17-0D-00-00-38-03-D9', 9: '00-17-0D-00-00-31-D5-20', 10: '00-17-0D-00-00-38-03-69', 11: '00-17-0D-00-00-30-3E-09', 12: '00-17-0D-00-00-38-06-C9', 13: '00-17-0D-00-00-38-03-CA', 14: '00-17-0D-00-00-31-CC-40', 15: '00-17-0D-00-00-58-2A-E8', 16: '00-17-0D-00-00-31-D4-7E', 17: '00-17-0D-00-00-38-06-AD', 18: '00-17-0D-00-00-31-D1-AC', 19: '00-17-0D-00-00-38-05-DA', 20: '00-17-0D-00-00-31-C6-A1', 21: '00-17-0D-00-00-38-06-67', 22: '00-17-0D-00-00-38-03-87', 23: '00-17-0D-00-00-38-04-25', 24: '00-17-0D-00-00-31-D5-69', 25: '00-17-0D-00-00-38-05-F1', 26: '00-17-0D-00-00-31-C9-F1', 27: '00-17-0D-00-00-38-04-3B', 28: '00-17-0D-00-00-31-C7-B0', 29: '00-17-0D-00-00-31-C3-19', 30: '00-17-0D-00-00-31-D5-3B', 31: '00-17-0D-00-00-31-C7-DE', 32: '00-17-0D-00-00-31-C9-E6', 33: '00-17-0D-00-00-31-D5-30', 34: '00-17-0D-00-00-31-D5-1F', 35: '00-17-0D-00-00-31-C1-A0', 36: '00-17-0D-00-00-31-CA-05', 37: '00-17-0D-00-00-31-CC-58', 38: '00-17-0D-00-00-31-D5-67', 39: '00-17-0D-00-00-31-C3-53', 40: '00-17-0D-00-00-31-CB-E5', 41: '00-17-0D-00-00-31-C1-C1', 42: '00-17-0D-00-00-31-CC-2E', 43: '00-17-0D-00-00-31-D1-D3', 44: '00-17-0D-00-00-31-C9-DA', 45: '00-17-0D-00-00-31-D1-32', 46: '00-17-0D-00-00-31-D5-86', 47: '00-17-0D-00-00-31-C1-A1', 48: '00-17-0D-00-00-31-C6-B8', 49: '00-17-0D-00-00-31-CB-E7', 50: '00-17-0D-00-00-31-CC-0F', 51: '00-17-0D-00-00-31-D1-A8', 52: '00-17-0D-00-00-31-D1-70', 53: '00-17-0D-00-00-31-D5-6A', 54: '00-17-0D-00-00-31-C3-71', 55: '00-17-0D-00-00-31-C1-AB', 56: '00-17-0D-00-00-31-C3-3E', 57: '00-17-0D-00-00-31-D5-01'}


#============================ variable ======================================
dict_roomid_data_packet = {roomid: [] for roomid in dict_roomid_name} # {roomid:[]}
dict_roomid_list_neighbor = {roomid: [] for roomid in dict_roomid_name} # {roomid:[]}
#dict_roomid_list_neighbor = {roomid: [] for roomid in range(11, 99)} # {roomid:[]}
dict_roomid = {}

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

def get_blink_notif_mgr(notif_msg):
    list_blink_msg = []
    for a_msg in notif_msg:
        if a_msg['msg']['serialport'] == 'COM7' and a_msg['msg']['notifName'] == 'notifData' and a_msg['msg']['notifParams'][3] == 61616:
            list_blink_msg.append(a_msg)
    return list_blink_msg

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

def proc_expr2_bink():
    dict_roomid_moteid_rssi = {} # dictionary {roomid: {moteid1 : [rssi1, rssi2, rssi3]}, ...}

    blink_decode = [base64.b64decode(blk_str) for blk_str in mrg_blink_data]

    # get the values for each location test: {roomid:[packet1, packet2, packet3]}
    for blk in blink_decode:
        blk_decode = [ord(b) for b in blk]
        dict_roomid_data_packet[blk_decode[2]].append(blk)

    # decode blink data to payload, and neighbor we get rssi value, {roomid:[[(id1, rssi1),(),(), ()]]}
    for roomid in dict_roomid_data_packet:
        list_neighbor = []
        for data in dict_roomid_data_packet[roomid]:
            blinkdata, blinkneighbors = blink.decode_blink(data)
            list_neighbor.append(blinkneighbors)
        dict_roomid_list_neighbor[roomid] = list_neighbor

    # get {roomid: set moteid}
    for roomid in dict_roomid_list_neighbor:
        set_moteid = set()
        for packet in dict_roomid_list_neighbor[roomid]:
            for neighbor in packet:
                set_moteid.add(neighbor[0])
        dict_roomid.update({roomid:set_moteid})

    # get {roomid: {moteid: [rssi]}}
    for roomid in dict_roomid_list_neighbor:
        dict_moteid_rssi = {}
        for moteid in dict_roomid[roomid]:
            dict_moteid_rssi.update({moteid:[]})
        dict_roomid_moteid_rssi.update({roomid: dict_moteid_rssi})

        for packet in dict_roomid_list_neighbor[roomid]:
            for neighbor in packet:
                if neighbor[0] in dict_roomid[roomid]:
                    dict_roomid_moteid_rssi[roomid][neighbor[0]].append(neighbor[1])
    print 'before', dict_roomid_moteid_rssi

    # create {moteid: room_name}, dict_mac_roomname, dict_moteid_mac
    dict_moteid_room = {} #
    for moteid in dict_moteid_mac:
        dict_moteid_room.update({moteid:dict_mac_roomname[dict_moteid_mac[moteid]]})
        

    # change the roomid -> real location name of dict_roomid_moteid_rssi
    # change key of dictionary, command: dictionary[new_key] = dictionary.pop(old_key)
    for roomid in dict_roomid_list_neighbor:
        print dict_roomid_name[roomid]
        dict_roomid_moteid_rssi[dict_roomid_name[roomid]] = dict_roomid_moteid_rssi.pop(roomid)
        
        
    # change the moteid -> real location name of dict_roomid_moteid_rssi (can thay doi ma hoa cua 3 access point)
    

    print 'after', dict_roomid_moteid_rssi
    print 'dict_moteid_room', dict_moteid_room


#============================ main ============================================
def main():
    list_blk = proc_expr2_bink()
    raw_input('Press enter to finish')
if __name__=="__main__":
    main()



