from pyzabbix import ZabbixAPI
from argparse import ArgumentParser
import csv
from datetime import datetime, timedelta

parser = ArgumentParser(description='Retorna lista de itens de n hosts')
parser.add_argument('--url-api', dest='url_api', help='URL Zabbix API')
parser.add_argument('--user', dest='user', help='Zabbix user')
parser.add_argument('--password', dest='password', help='Zabbix password')
parser.add_argument('--group', dest='HOSTGROUP', help='Arquivo a ser lido com nome do grupo de op. Um grupo por linha.')
parser.add_argument('--path', dest='arquivo', help='Arquivo de saida')

import os
from pyzabbix import ZabbixAPI
args = parser.parse_args()

zapi = ZabbixAPI(args.url_api)
zapi.login(args.user,args.password)
exitcode = 0

def getValueFromMacroList(macro: str, macros: list):
    if not macro or not macros:
        return False
    x = [y['value'] for y in macros if y['macro'] == macro]
    if len(x):
        return x[0]
    return None

try:
    groupid = zapi.hostgroup.get(output=['groupid', 'name'], filter={'name': args.HOSTGROUP})
    h = zapi.host.get(output=['hostid', 'name', 'status', 'description'], selectGroups='extend', selectMacros='extend',
                      groupids=[groupid[0]['groupid']])
    print(f'Achei {len(h)} hosts')
    print('hostname;lastvalue;groups;hostdescription;days to expire;hps;description;url')
    report = []
    for i in h:
        lastvalue = zapi.item.get(ouput=['lastvalue'], hostids=[i['hostid']],
                                  filter={'name': 'SSL - Certificate - days until expire'})
        if len(lastvalue) == 1:
            lv = lastvalue[0].get('lastvalue', None)
        else:
            lv = 'ERROR'
        url = getValueFromMacroList(macro='{$URL}', macros=i['macros'])
        daystoexpire = getValueFromMacroList(macro='{$DAYS_TO_EXPIRE}', macros=i['macros'])
        hps = getValueFromMacroList(macro='{$HPS}', macros=i['macros'])
        description = getValueFromMacroList(macro='{$DESCRIPTION}', macros=i['macros'])
        groups = ','.join([x['name'] for x in i['groups']])
        hostdescription = i['description']
        print(f"{i['name']};{lv};{groups};{i['description']};{daystoexpire};{hps};{description};{url}")
        report.append({'name': i['name'], 'lv': lv, 'groups': groups, 'hostdescription': hostdescription,
                       'daystoexpire': daystoexpire, 'hps': hps, 'descr': description, 'url': url})


        with open(args.arquivo, "w") as arquivo:
            arquivo.write("Hostname;Last value;Groups;hostdescription;Threshold;Macro HPS;Macro Description;Macro URL\r\n")
            for r in report:
                arquivo.write(f'{r["name"]}')
                arquivo.write(";")
                arquivo.write(f'{r["lv"]}')
                arquivo.write(";")
                arquivo.write(f'{r["groups"]}')
                arquivo.write(";")
                arquivo.write(f'{r["hostdescription"]}')
                arquivo.write(";")
                arquivo.write(f'{r["daystoexpire"]}')
                arquivo.write(";")
                arquivo.write(f'{r["hps"]}')
                arquivo.write(";")
                arquivo.write(f'{r["descr"]}')
                arquivo.write(";")
                arquivo.write(f'{r["url"]}')
                arquivo.write(";")
                arquivo.write("\r\n")
        arquivo.close()

except Exception as e:
    print(f'Aborting. Error: \'{e}\'')
    exitcode = 1
finally:
    zapi.user.logout()
    exit(exitcode)
