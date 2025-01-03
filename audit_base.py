from argparse import ArgumentParser
from re import L
from pyzabbix import ZabbixAPI
import logging
import linecache
import os
import json
import pickle
from datetime import datetime, timedelta

parser = ArgumentParser(description='Relatorio de hosts adicionados e removidos do zabbix no dia')
parser.add_argument('--url-api', dest='url_api', help='URL Zabbix API')
parser.add_argument('--user', dest='user', help='Zabbix user')
parser.add_argument('--password', dest='password', help='Zabbix password')
parser.add_argument('--log-level',dest='log', help='Log Level')
parser.add_argument('--log-path',dest='log_path', help='Log Path')
parser.add_argument('--groups',dest='groupid', help='Groupid')
args = parser.parse_args()
logging.basicConfig(filename=args.log_path, encoding='utf-8', level=args.log)

list_proxies = ['CM-RJ-','CM-RJ_GSAT','CM-DEV','AS-SP','TVG-BH','AWS','AZ','GCP','OCI','TVG-EG','TVG-SP','TVG-LQ']
cache = {}
file = "cache/pickle.dat"

def clearcache():
    """Clear the cache entirely."""
    cache.clear()

def zbx_login(url,user,password):
    if url:
        global zapi
        zapi = ZabbixAPI(url, timeout=600.0)
        try:
            zapi.login(user, password)
            return zapi
        except Exception as e:
            logging.error("Unable to login: %s" % (e))
            exit(0)
        else:
            logging.info("Logged")

def convert_json(proxies):
    total = len(hosts)
    logging.info("Total host count: %s" % total)
    for i in range(len(hosts)):
        id = hosts[i]['proxy_hostid']
        j = 0 
        found = 0
        if hosts[i]['proxy_hostid'] != '0':
            while found == 0:
                if proxies[j]['proxyid'] == id:
                    found = 1
                    hosts[i]['proxy_hostid'] = proxies[j]['host']
                else:
                    j+=1
        else:
            logging.warning("Error ocurred while converting host to json format %s", hosts[i])
    number_of_hosts_per_proxy(proxies)


def number_of_hosts_per_proxy(proxies):
    for i in range(len(proxies)):
        proxy_name = proxies[i]['host']
        count_enabled = 0
        count_disabled = 0
        for j in range(len(hosts)):
            if hosts[j]['proxy_hostid'] == proxy_name:
                if hosts[j]['status'] == '0':
                    count_enabled+=1
                else:
                    count_disabled+=1
        list_test=[]
        list_test.append(proxy_name)
        list_test.append(count_enabled)
        list_test.append(count_disabled)
        list_count.append(list_test)

def soma_regioes():
    for i in range(len(list_proxies)):
        list_content = []
        count_enabled = 0
        count_disabled = 0
        for j in range(len(list_count)):
            if list_proxies[i] in list_count[j][0]:
                count_enabled = count_enabled + list_count[j][1]
                count_disabled = count_disabled + list_count[j][2]
        list_content.append(list_proxies[i])
        list_content.append(count_enabled)
        list_content.append(count_disabled)
        list_format.append(list_content)


def cria_dicionario():
    result = '{ "data": ['
    for i in range(len(list_format)):
        new_line = '{ "Region": "'+ str(list_format[i][0]) + '",  "Enabled":'+ str(list_format[i][1])+ ', "Disabled":'+str(list_format[i][2]) +'}'
        result = result + new_line
        if (i+1) < len(list_format):
            result = result + ","
    result = result+ ']}'
    logging.info(result)
    print(result)

def is_file_empty(file_path):
    """ Check if file is empty by confirming if its size is 0 bytes"""
    # Check if file exist and it is empty
    return os.path.exists(file_path) and os.stat(file_path).st_size == 0


def get_proxies():
    if is_file_empty(file):
        logging.info("File is empty - Getting proxies and filling cache")
        time_now = datetime.now()
        proxies = zapi.proxy.get(output=['proxyids','host'])
        with open(file, 'wb' ) as f:
            pickle.dump(proxies,f)
            pickle.dump(time_now,f)
            f.close()
        convert_json(proxies)
    else:
        with open(file, 'rb' ) as f:
            proxies = pickle.load(f)
            date = pickle.load(f)
            f.close()
        check_date = datetime.now() - timedelta(days=30)
        print(check_date)
        if check_date < date:
            logging.info("File not empty - Cache is newer than 30 days - Using cache")
            return proxies
        else:
            logging.info("File not empty - Cache is older than 30 days - Deleting cache and redoing get_proxies()")
            with open(file, 'w' ) as f:
                pass
            get_proxies()
 


def get_hosts(group):
    return zapi.host.get(output=['host','status','proxy_hostid'],groupids=group)

zapi = zbx_login(args.url_api,args.user,args.password)

#Get all proxies



#Get hosts from groups

list_count = []
list_format = []
try:
    hosts = get_hosts(args.groupid)
    get_proxies()
    soma_regioes()
    cria_dicionario()
    logging.info('End of execution')
except Exception as e:
    logging.warning('Error during execution: %s' % (e))
zapi.user.logout()

