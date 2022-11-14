# WifiSniffing
Testing A Case Study of WiFi Sniffing for Class Project 

In this project, the goal is to sniff the probe request from mobil users, so we are going to be sniffing the probe-req messages only.


 * paper: `https://ieeexplore.ieee.org/document/9138409`

 * script for channel hopping: `https://gist.githubusercontent.com/hnw/6fbd3ac3bb59d0c93fc0bd2a823cf5cb/raw/8d3f3a0d0e7da98c43feba59e741aa40049646d2/chanhop.sh`

 * tutorials for monitor mode and iw use: 
 	- `https://netbeez.net/blog/linux-how-to-configure-monitoring-mode-wifi-interface/` 
	- `https://netbeez.net/blog/linux-channel-hopping-wifi-packet-capturing/`

 * Attemps to reproduce the WiFi sniffing on Oragne Pi Zero
   	- Can't configure channel hopping due to Unknown Error 524 (-524).
  	- Sniff probe request in signle channel (channel 5, default).
   
 * As I do not  own any other hardware, proceed to test on a linux notebook (manjaro linux, gnome version 42.4)
 	- Single channel probe request.
   	- Hopping over the IEEE80211B channels (the 11 firsts).
 * This may be reproduced on a RPi 3 model B.


### How to set up (linux notebook)

Install net-tools: `sudo pacman -S net-tools`

Install tcpdump: `sudo pacman -S tcpdump`

Install aircrack-ng: `sudo pacman -S aircrack-ng`

If it is not installed, install iw


### Configure monitor mode

First, check your wlan interface: `ifconfig`
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

We need it to be type monitor, for this we will be using aircrack-ng as follows:

  First, to ensure that others process do not interfere with our monitoring, use
  ``` sudo airmon-ng check kill ```
  It may let you without Wi-Fi connection, but with Ethernet you still can use the net...
  
  Then, use the following `sudo airmon-ng start <interface> <channel>` as follows for interface `wlon1` and channel 11
  
  ```
  sudo airmon-ng start wlo1 11 
  ```
  output:
```
PHY	Interface	Driver		Chipset
phy0	wlo1		iwlwifi		***
	(mac80211 monitor mode enabled for [phy0]wlo1 on [phy0]wlo1mon)
 
```
  
  this creates `wlo1mon` interfaces which we will be using for monitoing (at the channel 11, in this case).
  
  Check the `iw <interface> info` again, it should be something like:

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
  
  
  ## Channel hopping:
  
  The script `chanmon.sh` allows to hop into different channes in monitor mode, use as follows:
  
  ```
  ./chanhop.sh -i <interface> -b <band> -b <band> -d <time on each channel in seconds>
  ```
  
  example: 
  
  ```
  ./chanhop.sh -i wlo1mon -b IEEE80211B  -d .10
  ```
  
  for more information, use ./chanhop.sh --help
  
  
  # TCPDUMP SINGLE CHANNEL
  
  Once the wlan interface is set as monitor mode, we can sniff the probe request on it using tcpdump as follows:
  
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
  
  
  

