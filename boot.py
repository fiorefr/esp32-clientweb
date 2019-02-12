import esp
import gc
import os
from network import WLAN
from machine import Pin
import machine
import network
import onewire
import ds18x20
import time
import urequests2
import ubinascii
import socket
import json

def getInfo():
  print('-------------------------------- INFO --------------------------------')
  print('mac : %s' % (mac))
  print('freq : ', machine.freq())
  print('id : ', ubinascii.hexlify(machine.unique_id(),':').decode()) #used to correspond to the mac
  print()

def initi():
  esp.osdebug(None) #no debug
  gc.collect() #garbage collector
  
def do_connect():
  print("-------------------------------- NETWORK --------------------------------")
  wlan = network.WLAN(network.STA_IF) #declaration
  wifi_ssid = 'Alternanza_Informatica' #your wifi ssid
  wifi_password = 'sensoritemp' #your wifi pwd
  wlan.active(True) 
  if not wlan.isconnected(): 
    print('connecting to network ...') #debug string
    wlan.connect(wifi_ssid, wifi_password)
    while not wlan.isconnected():
      pass
  print('network config : ', wlan.ifconfig()) #outputs device ip, subnet mask, network ip, gateway/dns
  
def read():
  pinna = Pin(12) #pin where the bus is connected
  ow = onewire.OneWire(pinna) #takes the bus from 1-wire
  ds = ds18x20.DS18X20(ow) 
  roms = ds.scan()
  ds.convert_temp() 
#json
  stringa = {
      "value": [
      ]
    }

  n = 0
  for rom in roms: 
    time.sleep_ms(750)      
    stringa['value'].append(
        {
          "sensorProgressive": n ,
          "reading": ds.read_temp(rom) 
        }
    )
    n = n + 1

  response = urequests2.post(url_dev, json = stringa, headers={'X-MAC-Address': mac}) #post call

def http_get(url):
    _, _, host, path = url.split('/', 3) #manual split of the url i entered in the URL var. '_' char is an empty python var
    print("host: ",host,"path: ",path) #i don't want to print also the two blank vars --> '_'
    addr_info = socket.getaddrinfo(host, 8080) #create the socket with host + manually insert port:8080
    addr = addr_info[0][-1] #trick used to take the right url
    s = socket.socket() 
    s.connect(addr)
    s.send(bytes('GET /%s HTTP/1.1\r\nHost: %s\r\n\r\n' % (path, host), 'utf8')) #query started
    #in the loop i print everything i can read from the server 
    while True:
        data = s.recv(100)
        if data:
            print(str(data, 'utf8'), end='')
        else:
            break
    print('\nData received.') #debug
    s.close() #end of connection

def conn_db(): #json sent to the db to register the device
  str_dati = {
      "value": [
        {
          "id" : 1 ,
          "location" : 1
        }
      ]
    }
  resp = urequests2.post(url_post_db, json = str_dati, headers={'X-MAC-Address': mac}) #post query
	
#start of the main
n=0
url_dev_post = str("http://10.11.5.89/devices/%d/readings" % (n)) #sending/getting temperatures
url_dev_get = str("http://10.11.5.89:8080/devices/%d/readings" % (n)) #sending/getting temperatures
url_get_loc = "http://10.11.5.89:8080/locations" #getting locations

mac = ubinascii.hexlify(WLAN().config('mac'),':').decode()

url_post_db = "http://172.16.22.91/Sorbellini/devices/current/readings" #sending id+mac+loc
url_dev = "http://172.16.22.91:8080/Sorbellini/devices/current/readings" #if u see here i have the port, cause my method needs it.

#function calls
initi()
getInfo()
do_connect()
conn_db()
print("-------------------------------- DEVICE REGISTERED APPROVED --------------------------------")
time.sleep_ms(5000)
print("-------------------------------- POST & GET --------------------------------")
#loop till it dies
while True:
  wlan = network.WLAN(network.STA_IF)
  time.sleep_ms(10000)
  if not wlan.isconnected(): #check if the device is still connected, if is not it calls the function to re-connect it
    do_connect()
    while not wlan.isconnected():
      pass
      
  read()
  print('\nData sent.\n')
  http_get(url_dev)

print("\nProgram ended.")
