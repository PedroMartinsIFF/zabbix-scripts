import os
from argparse import ArgumentParser
from libs import zabbix_functions
from pyzabbix import ZabbixAPI
import csv
import requests
from datetime import datetime, time ,timedelta, date
import time
import json


parser = ArgumentParser(description='Relatorio de hosts adicionados e removidos do zabbix no dia')
parser.add_argument('--url-api', dest='url_api', help='URL Zabbix API')
parser.add_argument('--user', dest='user', help='Zabbix user')
parser.add_argument('--password', dest='password', help='Zabbix password')

args = parser.parse_args()

zapi = zabbix_functions.zbx_login(args.url_api,args.user,args.password)

triggers = zapi.template.get(templateids='347891',selectTriggers=['description'])


with open('results/lista_triggers_template2.csv', 'w') as list:
    print("Template;Trigger Name;TriggerID;Tags", file=list)
    for trigger in triggers:
        templateid = trigger['templateid']
        prototype = zapi.triggerprototype.get(templateids=templateid,selectTags='extend')
        template = trigger['host']
        #print(prototype)
        for i in range(len(trigger['triggers'])):
            tag = zapi.trigger.get(triggerids=trigger['triggers'][i]['triggerid'], selectTags='extend')
            tags=tag[0]['tags']
            tags.append({'tag' : 'close_problem', 'value' : 'enabled'})
            try:
                zapi.trigger.update(triggerid=trigger['triggers'][i]['triggerid'],tags=tags,manual_close=1)
            except Exception:
                print('Não foi possível atualizar a trigger pois a mesma ja possui a tag')

            #print(template+';'+trigger['triggers'][i]['description']+';'+trigger['triggers'][i]['triggerid']+';'+str(tags), file=list)
        for i in range(len(prototype)):
            tag_prototype = prototype[i]['tags']
            tag_prototype.append({'tag' : 'close_problem', 'value' : 'enabled'})
            try:
                zapi.triggerprototype.update(triggerid=prototype[i]['triggerid'],tags=tag_prototype,manual_close=1)
            except Exception:
                print('Não foi possível atualizar a triggerprototype pois a mesma ja possui a tag')

            #print(template+';'+prototype[i]['description']+';'+prototype[i]['triggerid']+';'+str(tag_prototype))

