# zabbix-trapper-xds-python
Zabbix trapper for XDS Satellite receivers via Hudson telnet port

Goal of project is to collect data from XDS receiver for Tuner status, EbNO, RF Level, Temp, Fan Speed, Fades, RS Errors, and system voltages.  Script can be run under Linux or Windows.  Currently only tested running on Linux Zabbix Server (4.4) and Raspberry Pi Zabbix Proxy (4.4).  This allows Zabbix to be more secure not opening up TCP/10051 to non local hosts.
