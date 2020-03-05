'''
Copyright 2020 Eric Papenfuss wx9ep@yahoo.com

Permission is hereby granted, free of charge, to any person obtaining a copy of this software 
and associated documentation files (the "Software"), to deal in the Software without restriction, 
including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, 
and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, 
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial 
portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT 
NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. 
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, 
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE 
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

''' Sample command line 
* * * * * python3 /usr/local/bin/xds_trapper.py  192.168.1.14 xdsuser xdspassword LearfieldXDS
run every minute  script location				IP OF XDS	user	pass		Zabbix Host name
'''

# Goal is to communicate to XDS satellite receiver over telnet on port 2000 aka Hudson interface
import telnetlib
import re
import subprocess
import shlex
import sys
# Define regex searches to populate variables

EB = re.compile(b'EB:.+?(\d+\.\d*)')
AG = re.compile(b'AG:.+?(\d+)')
FADES = re.compile(b'Fades:.+?(\d+)')
TEMP = re.compile(b'(\d+).?degrees')
FAN = re.compile(b'(\w*?)\s\((\d*)\sRPM\)')
RS = re.compile(b'RS:\s+(\d+)\\r')
LOCKED = re.compile(b'LOCKED:\s+?(\w+)\\r')
V3_3 = re.compile(b'3.3V\s+:\s(\d*.\d*)')
V5  = re.compile(b'5.0V\s+:\s(\d*.\d*)')
V12  = re.compile(b'12.0V\s+:\s(\d*.\d*)')
#ZHOST = "LearfieldXDS"
#KEY = "EB"
#VALUE = "14.9"
SERVER = "127.0.0.1"
zabbixsender = '''/usr/bin/zabbix_sender''' # Linux location of zabbix sender, 
#zabbixsender = '''C:\program files\zabbix\zabbix_sender.exe''' # Windows location of zabbix sender, 

def zabbix_send(SERVER,ZHOST,KEY,VALUE):
        subprocess.call(shlex.split(zabbixsender + " -z " +  str(SERVER) + " -s " + str(ZHOST) + " -k " + str(KEY) + " -o " + str(VALUE)))

HOST = str(sys.argv[1])
PORT = 2000
user = str(sys.argv[2])
pwd = str(sys.argv[3])
ZHOST = str(sys.argv[4])

tn = telnetlib.Telnet(HOST, PORT)

tn.read_until(b"Hudson> ")

tn.write(b"login " + user.encode('ascii') + b"," + pwd.encode('ascii') + b"\n")

tn.write(b"tuner show\n")
tn.write(b"temp\n")
tn.write(b"fan show\n")
tn.write(b"pwr\n")
tn.write(b"logout\n")
tn.write(b"quit\n")

xds = tn.read_all()

#Check if tuner is locked
LOCKED = (LOCKED.search(xds).group(1)).decode()
zabbix_send(SERVER,ZHOST,"LOCKED","\""+LOCKED+"\"")

#12.0VDC voltage
V12 = float(V12.search(xds).group(1))
zabbix_send(SERVER,ZHOST,"12V",V12)

#5.0VDC Voltage
V5 = float(V5.search(xds).group(1))
zabbix_send(SERVER,ZHOST,"5V",V5)

#3.3VDC Voltage
V3_3 = float(V3_3.search(xds).group(1))
zabbix_send(SERVER,ZHOST,"3.3V",V3_3)

#Eb/No (Signal to noise ratio to bit)
EB = float(EB.search(xds).group(1))
zabbix_send(SERVER,ZHOST,"EB",EB)

#RF Signal Strength
AG = float(AG.search(xds).group(1))
zabbix_send(SERVER,ZHOST,"AG",AG)

#Reed-Solomon Errors
RS = int(RS.search(xds).group(1))
zabbix_send(SERVER,ZHOST,"RSERRORS",RS)

#Fade count
FADES = int(FADES.search(xds).group(1))
zabbix_send(SERVER,ZHOST,"FADES",FADES)

#Unit Temp
TEMP = float(TEMP.search(xds).group(1))
zabbix_send(SERVER,ZHOST,"TEMP",TEMP)

#Fan RPM / Speed
FANSPEED = (FAN.search(xds).group(1)).decode()
FANRPM = int(FAN.search(xds).group(2))
zabbix_send(SERVER,ZHOST,"FANSPEED",FANSPEED)
zabbix_send(SERVER,ZHOST,"FANRPM",FANRPM)

tn.close()

quit()
