import os
from argparse import ArgumentParser
from libs import zabbix_functions
from pyzabbix import ZabbixAPI
import csv
import requests
from datetime import datetime, time ,timedelta, date
import time
import json


parser = ArgumentParser(description='Cadastra services com um JSON como input')
parser.add_argument('--url-api', dest='url_api', help='URL Zabbix API')
parser.add_argument('--user', dest='user', help='Zabbix user')
parser.add_argument('--password', dest='password', help='Zabbix password')

args = parser.parse_args()

zapi = zabbix_functions.zbx_login(args.url_api,args.user,args.password)

f = open('input_format/mpls_sla.json')
data = json.load(f)
#print(data['MPLS_SLA']['LINK 1']['NAME'])
service_master_id= '1696'
for i in data['MPLS_SLA']:
    print(i)
    service_pai=zapi.service.create(name=i, algorithm='2', showsla='1', goodsla='99.80', sortorder='0')
    service_pai_id = service_pai['serviceids']
    zapi.service.adddependencies(serviceid=service_master_id,dependsOnServiceid=service_pai_id[0], soft='0')
    for j in data['MPLS_SLA'][i]:
        print(j)
        service_filho=zapi.service.create(name=j, algorithm='1', showsla='1', goodsla='99.80', sortorder='0')
        service_filho_id = service_filho['serviceids']
        zapi.service.adddependencies(serviceid=service_pai_id[0],dependsOnServiceid=service_filho_id[0], soft='0')
        for k in data['MPLS_SLA'][i][j]['LINKS']:
            for l in data['MPLS_SLA'][i][j]['LINKS'][k]:
                print(k)
                trigger_id = zapi.trigger.get(filter={'description' : data['MPLS_SLA'][i][j]['LINKS'][k]['TRIGGER']})
                print(data['MPLS_SLA'][i][j]['LINKS'][k]['TRIGGER'])
                service_neto = zapi.service.create(name=k, algorithm='1', showsla='1', goodsla='99.80', sortorder='0', triggerid=trigger_id[0]['triggerid'])
                service_neto_id = service_neto['serviceids']
                zapi.service.adddependencies(serviceid=service_filho_id[0],dependsOnServiceid=service_neto_id[0], soft='0')
