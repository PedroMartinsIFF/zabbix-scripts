#!/usr/local/bin/python3

from os import path, environ
from sys import argv, exit
from pyzabbix import ZabbixAPI
from argparse import ArgumentParser
from logprint import LogPrint
import json
import csv

parser = ArgumentParser(description = 'GET/UPDATE SPECIFIC MACRO FOR TEMPLATES OR HOSTS (BY GROUPID)')
parser.add_argument('--url', required = True, dest = 'url', help = 'Zabbix server address')
parser.add_argument('--user', required = True, dest = 'user', help = 'Zabbix user')
parser.add_argument('--password', required = True, dest = 'password', help = 'Zabbix password')
parser.add_argument('--update-hosts', dest='update_hosts', default='false', help='Option for update macro of hosts')
parser.add_argument('--update-templates', dest='update_templates', default='false', help='Option for update macro of templates')
parser.add_argument('--no-verbose', dest='verbose', action='store_false', help='Dont show any logs on screen')
parser.add_argument('--verbose', dest='verbose', action='store_true')
parser.add_argument('--loglevel', dest='loglevel', default='ERROR', help='Debug level. DEBUG/INFO/WARNING/ERROR/CRITICAL')
args = parser.parse_args()

TIMEOUT = 10
LOGFILE = "/tmp/%s.log" % path.basename(argv[0])
logger = LogPrint(echo=args.verbose, logfile=LOGFILE, loglevel=args.loglevel.upper())

if args.url and args.user and args.password:
    url = args.url
    user = args.user
    password = args.password
else:
    user = environ.get('ldap_user', None)
    password = environ.get('ldap_pass', None)

def zapi_login(url, user, password):
    try:
        zapi = ZabbixAPI(url,timeout=TIMEOUT)
        logger.debug(f"Logging on {url} as {user}")
        zapi.login(user,password)
        logger.info(f"Logged on {url} as {user}")
        return zapi
    
    except Exception as e:
        logger.error(f"Unable to login on {url} as {user}: {e}")
        exit(1)

def zapi_logout(obj):
    try:
        obj.user.logout()
        print(f"#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#")
        logger.info('Logged out')
    
    except Exception as e:
        logger.error(f'Failed to logout: {e}')

#GET HOSTS INFOS BY GROUPID AND FILTER WITH NAME OF MACRO
def get_hosts_infos(group_id, macro_name, macro_value, obj):
    try:
        hosts_encontrados = []
        for host in obj.host.get(
            output=["host","hostid"],
            groupids=group_id,
            selectMacros=['hostmacroid', 'macro', 'value'],
            filterMacros={"macro": macro_name},
            filter={'status': 0}):

            for macro in host['macros']:
                if macro['macro'] == macro_name and macro['value'] == macro_value:
                    hosts_encontrados.append(host)

        return(hosts_encontrados)

    except Exception as e:
        logger.error(f'ERROR: {e}')

#VIEW HOSTS INFOS BECAUSE THE PARAMETER --update-hosts == false
def view_hosts_infos(hosts_info):
    try:
        print(f"#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#")
        if hosts_info:
            logger.info(f"PARAM --UPDATE-HOSTS == FALSE, ENTAO APENAS EXIBO")
            logger.info(f"[VIEW] HOSTS ENCONTRADOS:")
            for host in hosts_info:
                host_id = host['hostid']
                host_name = host['host']
                logger.info(f'HOST_ID: {host_id} ; HOST_NAME: {host_name}')
            logger.info(f'NENHUM UPDATE REALIZADO EM HOSTS')
        else:
            print(f"NENHUM HOST ENCONTRADO")
    
    except Exception as e:
        logger.error(f'ERROR: {e}')

#UPDATE MACRO VALUE FOR HOST BECAUSE THE PARAMETER --update-hosts == true
def update_hosts_infos(hosts_info, macro_name, macro_value, new_macro_value, obj):
    try:
        print(f"#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#")
        if hosts_info:
            logger.info(f"PARAM --UPDATE-HOSTS == TRUE, ENTAO VOU ATUALIZAR CONFORME ABAIXO")
            logger.info(f'[UPDATE] HOSTS A SEREM ATUALIZADOS')
            for host in hosts_info:
                host_id = host['hostid']
                host_name = host['host']
                for macro in host['macros']:
                    if macro['macro'] == macro_name:
                        macro['value'] = new_macro_value
                        obj.usermacro.update({
                            "hostmacroid": macro['hostmacroid'],
                            "macro": macro['macro'],
                            "value": new_macro_value
                        })
                        logger.info(f"HOST_ID: {host['hostid']} ; HOST_NAME: {host['host']} ; MACRO: '{macro_name}' ATUALIZADA PARA: '{new_macro_value}'")
                
            logger.info(f'HOSTS ATUALIZADOS')
        else:
            print(f"NENHUM HOST ENCONTRADO")

    except Exception as e:
        logger.error(f'ERROR: {e}')

#GET TEMPLATES INFOS BY FILTER WITH NAME AND VALUE OF MACRO
def get_templates_infos(macro_name, macro_value, obj):
    try:
        templates_encontrados = []
        for template in obj.template.get(
            output=["name","templateid"],
            selectMacros='extend',
            filter={'macros': [
                {'macro': macro_name},
                {'value': macro_value}
                ]}):

            for macro in template['macros']:
                if macro['macro'] == macro_name and macro['value'] == macro_value:
                    templates_encontrados.append(template)

        return(templates_encontrados)

    except Exception as e:
        logger.error(f'ERROR: {e}')

#VIEW TEMPLATES INFOS BECAUSE THE PARAMETER --update-templates == false
def view_templates_infos(templates_info):
    try:
        print(f"#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#")
        if templates_info:
            logger.info(f"PARAM --UPDATE-TEMPLATES == FALSE, ENTAO APENAS EXIBO")
            logger.info(f"[VIEW] TEMPLATES ENCONTRADOS:")
            for template in templates_info:
                template_id = template['templateid']
                template_name = template['name']
                logger.info(f'TEMPLATE_ID: {template_id} ; TEMPLATE_NAME: {template_name}')
            logger.info(f'NENHUM UPDATE REALIZADO EM TEMPLATES')
        else:
            print(f"NENHUM TEMPLATE ENCONTRADO")
    
    except Exception as e:
        logger.error(f'ERROR: {e}')

#UPDATE MACRO VALUE FOR TEMPLATE BECAUSE THE PARAMETER --update-templates == true
def update_templates_infos(templates_info, macro_name, macro_value, new_macro_value, obj):
    try:
        print(f"#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#")
        if templates_info:
            logger.info(f"PARAM --UPDATE-TEMPLATES == TRUE, ENTAO VOU ATUALIZAR CONFORME ABAIXO")
            logger.info(f'[UPDATE] TEMPLATES A SEREM ATUALIZADOS')
            for template in templates_info:
                template_id = template['templateid']
                template_name = template['name']
                for macro in template['macros']:
                    if macro['macro'] == macro_name:
                        macro['value'] = new_macro_value
                        obj.usermacro.update({
                            "hostmacroid": macro['hostmacroid'],
                            "macro": macro['macro'],
                            "value": new_macro_value
                        })
                        logger.info(f"TEMPLATE_ID: {template['templateid']} ; TEMPLATE_NAME: {template['name']} ; MACRO: '{macro_name}' ATUALIZADA PARA: '{new_macro_value}'")
                
            logger.info(f'TEMPLATES ATUALIZADOS')
        else:
            print(f"NENHUM TEMPLATE ENCONTRADO")

    except Exception as e:
        logger.error(f'ERROR: {e}')

def main():
    exit_code = 0
    group_id = 1658 #_Servico/BD ODBC MySQL
    macro_name = '{$DB_DRIVER}'
    macro_value = '/lib/x86_64-linux-gnu/libmyodbc8w.so'
    new_macro_value = '/usr/lib/x86_64-linux-gnu/odbc/libmaodbc.so'
    update_hosts = args.update_hosts
    update_templates = args.update_templates
    
    try:
        instance = zapi_login(url, user, password)
        hosts_info = get_hosts_infos(group_id, macro_name, macro_value, obj=instance)
        if update_hosts == 'false':
            view_hosts_infos(hosts_info)
        elif update_hosts == 'true':
            update_hosts_infos(hosts_info, macro_name, macro_value, new_macro_value, obj=instance)

        templates_info = get_templates_infos(macro_name, macro_value, obj=instance)
        if update_templates == 'false':
            view_templates_infos(templates_info)
        elif update_templates == 'true':
            update_templates_infos(templates_info, macro_name, macro_value, new_macro_value, obj=instance)

    except Exception as e:
        logger.error(f'ERROR: {e}')
        exit_code = 1
    
    finally:
        zapi_logout(instance)
        exit(exit_code)

main()
