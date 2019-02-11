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
  print('mac : ' , ubinascii.hexlify(WLAN().config('mac'),':').decode())
  print('freq : ', machine.freq())
  print('id : ', ubinascii.hexlify(machine.unique_id(),':').decode())
  print()

def initi():
  esp.osdebug(None) #no debug
  gc.collect() #garbage collector
  
def do_connect():
  print("-------------------------------- NETWORK --------------------------------")
  wlan = network.WLAN(network.STA_IF)
  wifi_ssid = "ITIS_Ravenna" 
  wifi_password = "nullobaldini"
  wlan.active(True)
  if not wlan.isconnected():
    print('connecting to network ...')
    wlan.connect(wifi_ssid, wifi_password)
    while not wlan.isconnected():
      pass
  print('network config : ', wlan.ifconfig())  #shows ip, subnet, network and gateway
  
def read():
  pinna = Pin(12) #pin connected to sensor data in the breadboard
  ow = onewire.OneWire(pinna) 
  ds = ds18x20.DS18X20(ow)
  roms = ds.scan() #n of sensors 
  ds.convert_temp() 
  time.sleep_ms(750)
  n = 0
  for rom in roms:       
    stringa = { #json
      "value": [
        {
          "mac": ubinascii.hexlify(WLAN().config('mac'),':').decode() ,
          "sensorProgressive": n ,
          "reading": ds.read_temp(rom) 
        }
      ]
    }
    response = urequests2.post(url_post, json=dict(stringa)) #call the post function
    n = n + 1

def http_get(url):
    _, _, host, path = url.split('/', 3)
    print("[1]: ",_,"[2]: ",_,"host: ",host,"path: ",path)
    port = 8080 #8080 is the port that we used, you can change it with yours. 
    addr_info = socket.getaddrinfo(host, port)
    addr = addr_info[0][-1]
    s = socket.socket()
    s.connect(addr)
    s.send(bytes('GET /%s HTTP/1.1\r\nHost: %s\r\n\r\n' % (path, host), 'utf8'))
    
    while True:
        data = s.recv(100)
        if data:
            print(str(data, 'utf8'), end='')
        else:
            break
    print('\nData received')       

    s.close()

url_post = "http://10.11.5.89:8080/devices/0" #POST
url_get_loc = "http://10.11.5.89/locations" #GET di tutte le location
url_get_dev = str("http://10.11.5.89/devices/" + n + "/readings") #GET delle letture device 

url_db = 

initi()

getInfo()

do_connect()

print("-------------------------------- POST & GET --------------------------------")

while True:
  time.sleep_ms(750)
  read()
  print('\nData sent\n')
  http_get(url_get_loc)
  
print("\nScript ended")
