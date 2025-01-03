
import sys
from pyzabbix import ZabbixAPI, ZabbixAPIException
from argparse import ArgumentParser
parser = ArgumentParser(description = 'Script para associar os hosts com template \'Template web - desktop ssl\' ao hostgroup \'Servico - SSL Cert\')')
parser.add_argument('--url', dest = 'url', required=True, help = 'Zabbix server address')
parser.add_argument('--user', dest = 'user', required=True, help = 'Zabbix user')
parser.add_argument('--password', dest = 'password', required=True, help = 'Zabbix password')
args = parser.parse_args()
TIMEOUT = 60
try:
    zapi = ZabbixAPI(args.url,timeout=TIMEOUT)
    zapi.login(args.user,args.password)
except Exception as e:
    exit(1)
web_desktop_ssl_template = zapi.template.get(output=['name'],filter={'name':'Template web - desktop ssl'})
web_desktop_ssl_templateid = web_desktop_ssl_template[0]['templateid']
ssl_cert_group = zapi.hostgroup.get(output=['name'],filter={'name':'Servico - SSL Cert'})
print(ssl_cert_group)
ssl_cert_groupid = ssl_cert_group[0]['groupid']
groups_to_add = [ssl_cert_groupid]
# Get host objects in Zabbix
hosts = zapi.host.get(output=['name','groups'],templateids=[web_desktop_ssl_templateid], search={'name': 'web_'}, selectGroups=['groupid'])
for host in hosts: 
    for group in groups_to_add:
        try:
            host['groups'].remove({'groupid':group})
            host['groups'].append({'groupid':group})
        except ValueError as e:
            host['groups'].append({'groupid':group})
    print('Atualizando os grupos do host ', host['name'])
    zapi.host.update(hostid=host['hostid'], groups=host['groups'])
    print('Host atualizado.')
