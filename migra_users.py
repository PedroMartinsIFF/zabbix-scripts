from pyzabbix import ZabbixAPI
from argparse import ArgumentParser
import json
import requests
import subprocess
import logging
import urllib3

# Configura o logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configura o parser de argumentos para a linha de comando
parser = ArgumentParser(description='Retorna lista de itens de n hosts')
parser.add_argument('--url-api', dest='url_api', help='URL Zabbix API')
#parser.add_argument('--user', dest='user', help='Zabbix user')
#parser.add_argument('--password', dest='password', help='Zabbix password')
args = parser.parse_args()

# Verifica se a URL da API foi fornecida
if args.url_api:
    zapi = ZabbixAPI(args.url_api, timeout=600.0)
    try:
        # Tenta fazer login na API do Zabbix
        zapi.login(user="", password="")
        logger.info("Logged")
    except Exception as e:
        # Caso o login falhe, exibe uma mensagem de erro e sai
        logger.error(f"Unable to login: {e}")
        exit(1)
else:
    # Se a URL da API não for fornecida, exibe uma mensagem de erro e sai
    logger.error("Erro ao logar na API.")
    exit(0)

# Função para verificar se um grupo contém 'API' no nome
def is_api_group(groups):
    for group in groups:
        if 'API' in group['name']:
            return False
    return True

# Função para obter usuários de um grupo específico
def get_users(id):
    lista_ldap = []
    users = zapi.user.get(usrgrpids=id, selectUsrgrps=['name'])
    for user in users:
        if is_api_group(user['usrgrps']):
            lista_ldap.append(user['username'])
    get_mails(lista_ldap)

# Função para obter os e-mails dos usuários usando ldapsearch
def get_mails(lista):
    lista_mail = {}
    for item in lista:
        ldap_user = item
        command = f"ldapsearch -x -h ldap.globoi.com -b 'cn={ldap_user},ou=Usuarios,dc=globoi,dc=com'"
        process = subprocess.run(command, shell=True, capture_output=True, text=True)
        if process.returncode == 0:
            logger.info("Command executed successfully!")
            output = process.stdout
            for line in output.splitlines():
                if line.startswith("mail:"):
                    email = line.split(":", 1)[1].strip()
                    lista_mail[ldap_user] = email
        else:
            logger.error(f"Command failed with return code {process.returncode}")
            logger.error(process.stderr)

    valida_auth_api(lista_mail)

# Função para verificar se um usuário existe na API do Zabbix
def usuario_existe(mail):
    try:
        user = zapi.user.get(filter={'username': mail})
        if not user:
            return True
        else:
            return False
    except Exception as e:
        logger.error(e)

# Função para validar a autenticação do usuário na API externa e editar o username
def valida_auth_api(lista):
    for user, email in lista.items():
        url = f"https://authapi.globoi.com/api/2.0/users/{email}"
        response = requests.get(url, verify=False)
        if response.status_code == 200:
            if usuario_existe(email):
                logger.info(f'Alterando o nome do user {user} para {email}')
                user = zapi.user.get(filter={'username': user})
                id = user[0]['userid']
                try:
                    zapi.user.update(userid=id,username=email)
                except Exception as e:
                    logger.error(e)
            else:
                logger.info(f'Usuario {user} já está dentro do padrão')
        else:
            logger.error(f"Failed to retrieve data: {response.status_code}")

# Função principal que inicia o processo
def main():
    id = '19'
    get_users(id)

if __name__ == '__main__':
    main()

# Logout da API do Zabbix
zapi.user.logout()
