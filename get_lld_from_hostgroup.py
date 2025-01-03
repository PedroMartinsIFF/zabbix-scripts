from pyzabbix import ZabbixAPI
from argparse import ArgumentParser
import json
import csv

parser = ArgumentParser(description='Retorna "key" + "lifetime" da LLD de hostgroups')
parser.add_argument('--url-api', dest='url_api', required = True, help='URL Zabbix API - ex.: https://api.zabbix.globoi.com')
parser.add_argument('--user', dest='user', required = True, help='Zabbix User')
parser.add_argument('--password', dest='password', required = True, help='Zabbix User Password')
parser.add_argument('--hostgroup', dest='hostgroup', required = True, help='Hostgroup name')
parser.add_argument('--discovery', dest='discovery', required = True, help='Nome do Discovery')
parser.add_argument('--output-file', dest='saida', required = True, help='Adicionar o path para o arquivo de saida')

# Exemplo de uso
# --url-api https://api.zabbix.staging.globoi.com --user USUARIO --password SENHA --hostgroup "NOME_HOSTGROUP" \
# --discovery "NOME_DISCOVERY" --output-file "NOME_ARQUIVO_SAIDA.csv"

args = parser.parse_args()

# Login
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

# GET hostgroupid
id = zapi.hostgroup.get(output=["groupid"], filter={"name": args.hostgroup})

# GET hosts
hosts = zapi.host.get(output=["host"], groupids=id[0]["groupid"], filter={"status": 0})

# Escreve arquivo de saída
with open(args.saida, 'w') as arquivo:
    for host in hosts:
        # GET key (key_) + Keep lost resources period (lifetime)
        get_lld = zapi.discoveryrule.get(output=["key_", "lifetime"], hostids=host["hostid"], filter={"name": args.discovery})
        if get_lld != []:
            print(f'{host["host"]};{get_lld[0]["key_"]};{get_lld[0]["lifetime"]}',file=arquivo)
        else:
            print(f'{host["host"]};Discovery {args.discovery} não encontrado',file=arquivo)

# Logout
zapi.user.logout()
