import pyshark
import collections
import matplotlib.pyplot as plt
import numpy as np
import requests
import pandas as pd
import openpyxl
from bs4 import BeautifulSoup
import platform

import os
from pathlib import Path
import argparse

MAC_URL = "http://standards-oui.ieee.org/oui.txt" # url para verificar las MAC address atravez del OUI

def analyzer(opt):
    
    download()

    loadPath = str( str(Path(__file__).parent) + opt.file_name)
    archivos = os.listdir(str(loadPath))
    channels = {} 
    valid_mac_count = 0
    mac_count = 0

    for pcap in archivos:
        captura = pyshark.FileCapture(loadPath+'/'+pcap)
        valid_SA = []
        
        for packet in captura: #packet.wlan.sa == Source MAC address 
            mac_count += 1
            if(compare_macs(packet.wlan.sa)):
                valid_SA.append(packet.wlan.sa)
                valid_mac_count += 1  
        print(pcap)
        CountFrequency(valid_SA)
        channels[pcap] = len(valid_SA)
    df = pd.DataFrame(channels.values(),index=channels.keys(), columns=['Number of Packets'])
    print(df)
    print("Valid MAC :",valid_mac_count/mac_count * 100 , "%")

    df.to_excel('channels_graph1.xlsx', sheet_name='new_sheet_name')
        

def CountFrequency(my_list):
    # Creating an empty dictionary
    freq = {}
    for item in my_list:
        if (item in freq):
            freq[item] += 1
        else:
            freq[item] = 1
    print("#SA: ", len(freq))
    #for key, value in freq.items():
    #    print ("% s : % d"%(key, value))

def download(): # actualiza la lista de OUI desde la IEEE
    if platform.system() == "Windows":
        MAC_ADDRESS_PATH = os.path.dirname(os.path.realpath(__file__)) + "\MAC_ADDRESS.txt" 
    else:
        MAC_ADDRESS_PATH = os.path.dirname(os.path.realpath(__file__)) + "/MAC_ADDRESS.txt" 
    # Remove old list
    if os.path.exists(MAC_ADDRESS_PATH):
        os.remove(MAC_ADDRESS_PATH)

    addresses = requests.get(url=MAC_URL)
    soup = BeautifulSoup(addresses.text, "lxml").text

    with open(MAC_ADDRESS_PATH, "a", encoding="utf8") as MAC_ADDRESS:
        for line in soup.split("\n"):
            if "(base 16)" in line:
                MAC_ADDRESS.write(line.replace("(base 16)", ""))

def compare_macs(mac_address): # permite verificar si es que la MAC address es valida comparando las OUI 
    mac_address = mac_address.replace(":", "").replace("-", "").upper()
    if platform.system() == "Windows":
        MAC_ADDRESS_PATH = os.path.dirname(os.path.realpath(__file__)) + "\MAC_ADDRESS.txt" 
    else:
        MAC_ADDRESS_PATH = os.path.dirname(os.path.realpath(__file__)) + "/MAC_ADDRESS.txt" 
    with open(MAC_ADDRESS_PATH, "r", encoding="utf8") as m:
        # Compare entered MAC address with addresses in text file
        MAC_ADDRESS_F = m.read()
        for address in MAC_ADDRESS_F.split("\n"):
            if address[0:6] == mac_address[0:6]:
                return(True)
                #print(address[7:].strip())
                #break
        else:
            return(False)
            #print("[!] MAC address not found")

def parse_opt():
    parser = argparse.ArgumentParser()
    parser.add_argument('--file_name' ,help='file where the ch pcap files are located')

    opt = parser.parse_args()
    return opt

def main(opt):
    analyzer(opt)

if __name__ == '__main__':
    opt = parse_opt()
    main(opt)