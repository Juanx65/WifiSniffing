# A Case Study of WiFi Sniffing Performance Evaluation 
## Class project review

The goal of this repository is to recreate the results shown in this paper:
    
    https://ieeexplore.ieee.org/document/9138409

 * WiFi sniffing on Oragne Pi Zero
   	- Can't configure channel hopping due to Unknown Error 524 (-524).
  	- Sniff probe request in signle channel (channel 5, default).
   
 * Test on a linux notebook (manjaro linux, gnome version 42.4)
   	- Channel hopping over the IEEE80211B channels in different setups.
    - This may be reproduced on a RPi 3 model B.


### How to set up (Majaro linux)

Install net-tools: `sudo pacman -S net-tools`

Install tcpdump: `sudo pacman -S tcpdump`

Install aircrack-ng: `sudo pacman -S aircrack-ng`

Install `iw`


### Configure monitor mode

First, check your wlan interface with: 

input:

`ifconfig`


output:

  ```
    eno1: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
    inet 192.168.*.**  netmask 255.255.255.0  broadcast 192.168.*.255
    inet6 **::**:**:**:**  prefixlen **  scopeid 0x**<link>
    ether **:**:**:**:**  txqueuelen 1000  (Ethernet)
    RX packets 47104  bytes 34335909 (32.7 MiB)
    RX errors 0  dropped 82  overruns 0  frame 0
    TX packets 18076  bytes 2848041 (2.7 MiB)
    TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0

    wlo1: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
    unspec **-**-**-**-**-**-**-**-**-**-**-**-**-**-**-**  txqueuelen 1000  (UNSPEC)
    RX packets 106475  bytes 26883581 (25.6 MiB)
    RX errors 0  dropped 0  overruns 0  frame 0
    TX packets 0  bytes 0 (0.0 B)
    TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0
  ```
  
The interface of interest is ` wlo1` (often `wlan0`).

Use `iw <interface> info` to show information of the wlan interface:

input:

```iw wlo1 info```

output:
```
Interface wlo1
ifindex *
wdev 0x*
addr **:**:**:**:**:**
type managed
wiphy 0
channel 4 (2427 MHz), width: 20 MHz (no HT), center1: 2427 MHz
txpower 0.00 dBm

```

We need it to be `type monitor`, for this use aircrack-ng as follows:

  First, to ensure that others process do not interfere, use

  ``` sudo airmon-ng check kill ```
  
  It might let you without Wi-Fi connection (a reboot will solve it).
  
  Then, use the following `sudo airmon-ng start <interface> <channel>` as follows for interface `wlon1` and channel 11

  input:
  
  ```
  sudo airmon-ng start wlo1 11 
  ```
  output:
```
PHY	Interface	Driver		Chipset
phy0	wlo1		iwlwifi		***
	(mac80211 monitor mode enabled for [phy0]wlo1 on [phy0]wlo1mon)
 
```
  
  This creates `wlo1mon` interfaces which we will be using for monitoing (at the channel 11, in this case).
  
  Check the `iw <interface> info` again, it should look like:

``` 
Interface wlo1mon
ifindex *
wdev 0x*
addr **:**:*:**:**:**
type monitor
wiphy 0
channel 11 (2462 MHz), width: 20 MHz (no HT), center1: 2462 MHz
txpower 0.00 dBm

```
  
  
  # Channel hopping:
  
  When creating the `chanhop.sh` file, give it permission: `chmod 700 chanhop.sh`. 
  
  The script `chanhon.sh` allows to hop into different channels in monitor mode, use as follows:
  
  ```
  ./chanhop.sh -i <interface> -b <band> -b <band> -d <time on each channel in seconds>
  ```
  
  example: 
  
  ```
  ./chanhop.sh -i wlo1mon -b IEEE80211B  -d .10
  ```
  
  for more information, use ./chanhop.sh --help
  
  
  # TCPDUMP SINGLE CHANNEL
  
  Once the wlan interface is set as `monitor mode`, we can sniff the probe request on it using tcpdump as follows:
  
  ```
  sudo tcpdump -I -i <intreface> -y IEEE802_11_RADIO -e -s 256 type mgt subtype probe-req -w <filen name to save>
  ```
  
  example:
  
  ```
  sudo tcpdump -I -i wlo1mon -y IEEE802_11_RADIO -e -s 256 type mgt subtype probe-req -w single_channel_test.pcap 
  ```
  
  obs: to prevent error `tcpdump: Couldn't change ownership of savefile` download the latest version of tcpdump ( I use version 4.99.1 ).
  
  
  
  # TCPDUMP CHANNEL HOPPING
  
  To sniff the probe-req files on channel hopping do as follow:
  
  ```
  sudo ./chanhop.sh -i <interface> -b <band> -d <channel time s> & sudo tcpdump -I -i <interface> -y IEEE802_11_RADIO -e -s 256 type mgt subtype probe-req -w <file name>
  

  ```
  Example: 
  
  ```
  sudo ./chanhop.sh -i wlo1mon -b IEEE80211B -d .10 & sudo tcpdump -I -i wlo1mon -y IEEE802_11_RADIO -e -s 256 type mgt subtype probe-req -w channelhoping-20min-house.pcap
  ```

# PCAP ANALYSIS

## Setup env
Create an envitoment using `virtualenv` as follows:

``` 
virtualenv env
``` 

Activate it:

```
source env/bin/activate        
``` 

Install requirements:

```
pip install -r requirements.txt
```

## Analysis of probe request

For the datasets in `\datasets`, use `pcap-analyzer.py` as follows:

```
python pcap-analyzer.py --file_name "/datasets/60m_05s_home" 
```
 
Where `60m_05s_home` is one of the folders with `pcap` test files.

Output example:

```
CH1.pcap
#SA:  11
CH2.pcap
#SA:  17
CH3.pcap
#SA:  13
CH4.pcap
#SA:  10
          Number of Packets
CH1.pcap                 77
CH2.pcap                 94
CH3.pcap                 50
CH4.pcap                 48
Valid MAC : 21.098039215686274 %
``` 

Where `#SA` stands for number of Source Address, and the number of packates shown are for the valid MAC address only.


## Multichannel antenna

If your hardware is capable of, you may want to sniff at different channels at the same time.

To can obtine information of your interface with `iw list` and check the 'valid interface cominations' that may looks as follows:

```
valid interface combinations:
		 * #{ managed } <= 1, #{ AP, P2P-client, P2P-GO } <= 1, #{ P2P-device } <= 1,
		   total <= 3, #channels <= 2

``` 

where it indicates that there are 2 channels.

Now you can create the number of channels interfaces to sniff on as follows:

```
iw dev <interface> interface add <new interface name> type monitor
```

example:

```
iw dev wlo1 interface add wlo2 type monitor
```

and make sure it does exist with `iw wlo2 info`

after that you can use airmon-ng to configure it and use it as you please.

#   
## References

* Paper:

    `https://ieeexplore.ieee.org/document/9138409`

 * Script for channel hopping: 
 
      `https://gist.githubusercontent.com/hnw/6fbd3ac3bb59d0c93fc0bd2a823cf5cb/raw/8d3f3a0d0e7da98c43feba59e741aa40049646d2/chanhop.sh`

 * Tutorials for monitor mode and iw use: 
 	- `https://netbeez.net/blog/linux-how-to-configure-monitoring-mode-wifi-interface/` 
	- `https://netbeez.net/blog/linux-channel-hopping-wifi-packet-capturing/`


* MAC-lookup
  
  `https://github.com/henriksb/MAC-Lookup`
  
* Multichannel capable antenna
  `https://superuser.com/questions/1137949/multiple-802-11-association-with-single-physical-antenna`


