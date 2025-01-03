# coding: utf-8
from pyzabbix import ZabbixAPI
from argparse import ArgumentParser

parser = ArgumentParser(description='Recupera número de eventos dos grupos DBOps, Enterprise, NetOps e SysOps em determinado período.')
parser.add_argument('--url-api', dest='url_api', help='URL Zabbix API - ex.: https://ro.api.zabbix.globoi.com')
parser.add_argument('--user', dest='user', help='Zabbix user')
parser.add_argument('--password', dest='password', help='Zabbix password')
parser.add_argument('--output', dest='output', help='Arquivo de saida')

args = parser.parse_args()

if args.url_api:
    zapi = ZabbixAPI(args.url_api, timeout=600.0)
    try:
        zapi.login(args.user, args.password)
    except Exception:
        print("Não foi possível fazer login: %s")
        exit(1)
else:
    print("Execute get_events.py -h para obter ajuda.")
    exit(0)

with open(args.output, 'w') as arquivo:
    print("Hostname,Agent Version", file=arquivo)
    items = zapi.item.get(output=["name","lastvalue"], filter= {"key_": "agent.version", "status": 0},monitored=True,selectHosts=["name"])
    for item in items:
        hostname = item['hosts'][0]['name']
        item_value = item['lastvalue']
        print(hostname,',',item_value, file=arquivo)
