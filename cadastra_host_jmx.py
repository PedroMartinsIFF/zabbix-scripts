from zabbix_utils import ZabbixAPI
from argparse import ArgumentParser
from datetime import datetime
import csv

parser = ArgumentParser(description='Retorna lista de itens de n hosts')
parser.add_argument('--url-api', dest='url_api', help='URL Zabbix API')
parser.add_argument('--user', dest='user', help='Zabbix user')
parser.add_argument('--password', dest='password', help='Zabbix password')
args = parser.parse_args()

if args.url_api:
    zapi = ZabbixAPI(args.url_api, timeout=600.0)
    try:
        zapi.login(user=args.user, password=args.password)
        print("Logged")
    except Exception:
        print("Unable to login: %s")
        exit(1)
else:
    print("Erro ao logar na Api")
    

def prx_cache():
    return zapi.proxy.get(output=['proxyid','host'])

def get_proxyid_from_cache(name,cache=None):
    try:
        len(cache)
    except Exception:
        cache = prx_cache()
    try:
        int(name[-1])
        # Se ainda estamos aqui, entao eh um proxy especifico
        for prx in cache:
            if ( prx['host'] == name ):
                return prx['proxyid']
        return False
    except Exception as e:
        # Se estamos aqui, entao eh um grupo de proxy, onde eu sorteio um dos possiveis
        found = [ prx for prx in cache if name in prx['host'] ]
        if len(found) > 0:
            import random
            prx = found[random.randint(0,(len(found)-1))]
            return prx['proxyid']
        else:
            return False

def cadastra_host():
    with open('input_format/lista_hosts_jmx.csv') as arquivo:
        readCSV = csv.reader(arquivo, delimiter=",")
        for row in readCSV:
            try:
                template=[{'templateid':'354311'}]
                hg = [{'groupid' : '61836'},{'groupid': '616636'},{'groupid': '616680'},{'groupid': '2161'}]
                name=row[0]+'_'+row[1]
                interface= [{'type': '4', 'useip': '0', 'dns': row[0], 'main': '1', 'ip': '', 'port': row[2]}]
                host_macros=[{'macro':'{$EVENT_METADADO}', 'value':'Middleware Oracle JMX'},{'macro':'{$EVENT_SEVERITY}', 'value':'3'},{'macro':'{$EVENT_TEAM}', 'value':'SUPORTE INFRAESTRUTURA MIDDLEWARE ORACLE'}]
                cache = prx_cache()
                zapi.host.create(host=name,interfaces=interface,groups=hg,templates=template,macros=host_macros,proxy_hostid=get_proxyid_from_cache('TVG-LQ-BE',cache))
                print(f'Host {name} registered successfully')
            except:
                print(f'Unable to register host:{row[0]+'_'+row[1]}')
cadastra_host()
