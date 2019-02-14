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
  print('id : ', ubinascii.hexlify(machine.unique_id(),':').decode())
  print()

def initi():
  esp.osdebug(None) #no debug
  gc.collect() #garbage collector
  
def do_connect():
  print("-------------------------------- NETWORK --------------------------------")
  wlan = network.WLAN(network.STA_IF)
  wifi_ssid = 'Alternanza_Informatica'
  wifi_password = 'sensoritemp'
  wlan.active(True)
  if not wlan.isconnected():
    print('connecting to network ...')
    wlan.connect(wifi_ssid, wifi_password)
    while not wlan.isconnected():
      pass
  print('network config : ', wlan.ifconfig())
  
def read():
  pinna = Pin(12)
  ow = onewire.OneWire(pinna)
  ds = ds18x20.DS18X20(ow)
  roms = ds.scan()
  ds.convert_temp() 

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

  response = urequests2.post(url_post_db, json = stringa, headers={'X-MAC-Address': mac})
  print(response.text)

def http_get(url):
    _, _, host, path = url.split('/', 3)
    print("host: ",host,"path: ",path)
    addr_info = socket.getaddrinfo(host, 8080)
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
    print('\nDati ricevuti')
    s.close()

def conn_db():
  strdati = {
      "value": [
        {
          "mac" : mac
        }
      ]
    }
  resp = urequests2.post(url_post_db, json = strdati)

def exists():
  respo = urequests2.get(url_post_db, headers={'X-MAC-Address': mac})
  print(respo.text)
  if(respo.status_code == 200):
    return 0


n=0
url_dev_post = str("http://10.11.5.89/devices/current/readings") #sending/getting temperatures
url_dev_get = str("http://10.11.5.89:8080/devices/current/readings") #sending/getting temperatures
url_get_loc = "http://10.11.5.89:8080/locations" #getting locations
url_reg_db = "http://10.11.5.89:8080/devices" #sending id+mac+loc

mac = ubinascii.hexlify(WLAN().config('mac'),':').decode()

url_post_db = "http://172.16.22.91:8080/Sorbellini/devices/current/readings" #sending id+mac+loc
url_dev = "http://172.16.22.91:8080/Sorbellini/devices/current/readings" 


initi()
getInfo()
do_connect()

m = exists()
if(m!=0):
  conn_db()

print("-------------------------------- DEVICE REGISTERED APPROVED --------------------------------")
time.sleep_ms(5000)
print("-------------------------------- POST & GET --------------------------------")

while True:
  try:
    wlan = network.WLAN(network.STA_IF)
    time.sleep_ms(10000)
    if not wlan.isconnected():
      do_connect()
      while not wlan.isconnected():
        pass
      
    read()
    print('\nDati inviati\n')
    http_get(url_dev)
  except KeyboardInterrupt:
    sys.exit()
  except:
    pass


print("\nFinito programma")
