from pyzabbix import ZabbixAPI  # Importa a biblioteca ZabbixAPI para interagir com a API do Zabbix
from argparse import ArgumentParser  # Importa ArgumentParser para lidar com argumentos de linha de comando
import json  # Importa json para manipulação de dados JSON

# Configura o parser de argumentos para a linha de comando
parser = ArgumentParser(description='Cria um novo usergroup baseado nas permissões de um usergroup de referencia')
parser.add_argument('--url-api', dest='url_api', help='URL Zabbix API')  # URL da API do Zabbix
parser.add_argument('--user', dest='user', help='Zabbix user')  # Usuário do Zabbix
parser.add_argument('--password', dest='password', help='Zabbix password')  # Senha do Zabbix
parser.add_argument('--name', dest='name', help='Nome do novo grupo')  # Nome do novo grupo de usuários
parser.add_argument('--usergroup-id', dest='usergroup_id', help='UserGroup com os direitos para serem clonados')  # ID do grupo de usuários de referência
args = parser.parse_args()  # Analisa os argumentos fornecidos

# Verifica se a URL da API foi fornecida
if args.url_api:
    zapi = ZabbixAPI(args.url_api, timeout=600.0)  # Conecta à API do Zabbix com um timeout de 600 segundos
    try:
        zapi.login(args.user, args.password)  # Tenta fazer login na API do Zabbix
        print("Logged")  # Informa que o login foi bem-sucedido
    except Exception:
        print("Unable to login: %s")  # Informa que o login falhou
        exit(1)  # Encerra o programa com código de erro 1
else:
    print("Erro ao logar na API.")  # Informa que a URL da API não foi fornecida
    exit(0)  # Encerra o programa com código de erro 0

# Obtém informações sobre o grupo de usuários de referência
info_group = zapi.usergroup.get(usrgrpids=args.usergroup_id, selectRights=['id', 'permission'])

# Extrai os direitos do grupo de usuários de referência
rights_group = info_group[0]['rights']

# Cria um novo grupo de usuários com os mesmos direitos do grupo de referência
zapi.usergroup.create(name=args.name, rights=rights_group)

# Faz logout da API do Zabbix
zapi.user.logout()
