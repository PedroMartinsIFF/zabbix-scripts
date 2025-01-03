from pyzabbix import ZabbixAPI
from argparse import ArgumentParser
import json

parser = ArgumentParser(description='Gera uma lista com os Hostgroups, numero de hosts, hosts desabilitados, erros e numero de itens')
parser.add_argument('--url-api', dest='url_api', help='URL Zabbix API')
parser.add_argument('--user', dest='user', help='Zabbix user')
parser.add_argument('--password', dest='password', help='Zabbix password')
parser.add_argument('--file', dest='file', help='Lista de Hostgroups')
parser.add_argument('--output-file', dest='saida', help='Adicionar o path para o arquivo de saida')


args = parser.parse_args()

if args.url_api:
	zapi = ZabbixAPI(args.url_api, timeout=600.0)
	try:
		zapi.login(args.user, args.password)
		print("Logged")
	except Exception:
		print("Unable to login: %s")
		exit(1)
else:
	print("Erro ao logar na API.")
	exit(0)

ids = []
names = []
with open(args.file) as hosts:
    for line in hosts:
        stripped_line = line.rstrip()
        try:
            id = zapi.hostgroup.get(output=["groupid"], filter={"name" : stripped_line})
            names.append(stripped_line)
            ids.append(id[0]['groupid'])
        except:
            print("Hostgroup não encontrado", stripped_line)


count = []
LEN_HOSTS = []
LEN_HOSTS_DISABLE = []
errors = []
for id in ids:
    itens = zapi.item.get(groupids=id,output=['item_id'])
    count.append(len(itens))
    HOSTS = zapi.host.get(output=["host", "error", "snmp_error", "ipmi_error", "jmx_error"], groupids=id, selectInterfaces=["ip", "dns", "type"],
                    filter={'status': 0})
    LEN_HOSTS.append(len(HOSTS))
    HOSTS_DISABLE = zapi.host.get(output=["host"], groupids=id, filter={'status': 1}, selectInterfaces=["ip"])
    qtde_no_errors = 0
    LEN_HOSTS_DISABLE.append(len(HOSTS_DISABLE))
    for HOST in HOSTS:
        for INTERFACE in HOST['interfaces']:
            if INTERFACE['type'] == '1':
                interfaceType = "Agent"
                errorInterface = HOST['error'] or "No Error"
            elif INTERFACE['type'] == '2':
                interfaceType = "SNMP"
                errorInterface = HOST['snmp_error'] or "No Error"
            elif INTERFACE['type'] == '3':
                interfaceType = "IPMI"
                errorInterface = HOST['ipmi_error'] or "No Error"
            else:
                interfaceType = "JMX"
                errorInterface = HOST['jmx_error'] or "No Error"
            # Esse print só serve se quiser ler o erro dos agentes.
            #print(HOST['host'], "- ", INTERFACE['ip'], "- ", INTERFACE['dns'], "- ", interfaceType, "- ", errorInterface)
            if errorInterface != "No Error":
                qtde_no_errors += 1
    errors.append(qtde_no_errors)

# Ordem Hostgroup,Hosts,Hosts Disabled,Hosts com Erro,Numero de itens
with open(args.saida, 'w') as arquivo:
    print("Hostgroup,Hosts,Hosts Disabled,Hosts com Erro,Numero de itens", file=arquivo)
    for i in range (len(count)):
        print(f'{names[i]},{LEN_HOSTS[i]},{LEN_HOSTS_DISABLE[i]},{errors[i]},{count[i]}',file=arquivo)
zapi.user.logout()
