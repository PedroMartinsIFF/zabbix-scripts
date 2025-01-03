import os
from argparse import ArgumentParser
from libs import zabbix_functions
from pyzabbix import ZabbixAPI
import csv
import requests
from datetime import datetime, time ,timedelta, date
import time


parser = ArgumentParser(description='Retira um relatório mensal dos SLA do servico de monitoracao dos liks mpls')
parser.add_argument('--url-api', dest='url_api', help='URL Zabbix API')
parser.add_argument('--user', dest='user', help='Zabbix user')
parser.add_argument('--password', dest='password', help='Zabbix password')

args = parser.parse_args()


zapi = zabbix_functions.zbx_login(args.url_api,args.user,args.password)

last_day_of_prev_month = datetime.today().replace(day=1,hour=23,minute=59,second=59,microsecond=00) - timedelta(days=1)
start_day_of_prev_month = datetime.today().replace(day=1,hour=0,minute=0,second=0,microsecond=00) - timedelta(days=last_day_of_prev_month.day)
start_timestamp = int(start_day_of_prev_month.timestamp())
end_timestamp = int(last_day_of_prev_month.timestamp())

all_services = zapi.service.get(serviceids='1696',selectDependencies=['serviceid'])

with open('results/relatorio_mpls3.csv', 'w') as arquivo:
    print("LINK,SLA,UP TIME,DOWN TIME,LINK 1 SLA,LINK 1 UPTIME,LINK 1 DOWNTIME,LINK 2 SLA,LINK 2 UPTIME,LINK 2 DOWNTIME ", file=arquivo)
    for service in all_services[0]['dependencies']:
        info_service_sla = zapi.service.getsla(serviceids=service['serviceid'],intervals={'from': start_timestamp, 'to': end_timestamp})
        info_service = zapi.service.get(serviceids=service['serviceid'],selectDependencies=['serviceid'])
        name = info_service[0]['name']
        downtime = time.strftime('%H:%M:%S', time.gmtime(info_service_sla[service['serviceid']]['sla'][0]['problemTime']))
        oktime = time.strftime('%H:%M:%S', time.gmtime(info_service_sla[service['serviceid']]['sla'][0]['okTime']))
        
        sla = info_service_sla[service['serviceid']]['sla'][0]['sla']
        name_filho = []
        downtime_filho = []
        oktime_filho = []
        sla_filho = []
        for filho in info_service[0]['dependencies']:
            info_service_sla = zapi.service.getsla(serviceids=filho['serviceid'],intervals={'from': start_timestamp, 'to': end_timestamp})
            info_service = zapi.service.get(serviceids=filho['serviceid'],selectDependencies=['serviceid'])
            name_new = info_service[0]['name']
            name_filho.append(name_new)
            downtime_new = time.strftime('%H:%M:%S', time.gmtime(info_service_sla[filho['serviceid']]['sla'][0]['problemTime']))
            downtime_filho.append(downtime_new)
            oktime_new = time.strftime('%H:%M:%S', time.gmtime(info_service_sla[filho['serviceid']]['sla'][0]['okTime']))
            oktime_filho.append(oktime_new)
            sla_new = info_service_sla[filho['serviceid']]['sla'][0]['sla']
            sla_filho.append(sla_new)
            #print(str(name)+','+str(sla)+','+str(oktime)+','+str(downtime),file=arquivo)
        if len(name_filho) > 1:
            print(str(name)+','+str(sla)+','+str(oktime)+','+str(downtime)+','+str(sla_filho[0])+','+str(oktime_filho[0])+','+str(downtime_filho[0])+','+str(sla_filho[1])+','+str(oktime_filho[1])+','+str(downtime_filho[1]),file=arquivo)
        else:
            print(str(name)+','+str(sla)+','+str(oktime)+','+str(downtime)+','+str(sla_filho[0])+','+str(oktime_filho[0])+','+str(downtime_filho[0])+',-,-,-',file=arquivo)

    
 


