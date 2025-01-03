import requests


def get_token():
    url = "https://horus.staging.globoi.com/api/auth/token"
    payload = {
        "params": {
            "email": "pedro.santos.martins@g.globo",
            "secret": "JCwV7rejBXoeUE46ydr5WT"
        }
    }

    response = requests.post(url, json=payload, verify=False)

    if response.status_code == 200:
        print("Success:", response.json())
        token = response.json()['data']['token']
        return token
    else:
        print("Failed:", response.status_code, response.text)

def get_application_id(token):
    url = "https://horus-api-develop.apps.tsuru.gcp.i.globo/teams"
    headers = {
        "Authorization":"Bearer " + token 
    }
    response = requests.post(url, headers = headers, verify=False)

    if response.status_code == 200:
        print("Success:", response.json())
    else:
        print("Failed:", response.status_code, response.text)

def create_linux(token):
    #Failed: 201 {"data":{"application":{"id":"43ad807a-cd1b-11ee-af95-42010a62c4fc","name":"Sentry"},"created_by":"pedro.santos.martins@g.globo","creation_date":"2024-10-30T17:13:36","host":"TESTE-CREATE-LINUX-PEDRO","id":"1893ab77-6663-4716-a8df-fd179394c671","name":"TESTE-CREATE-LINUX-PEDRO","servicenow_team":{"name":"Opera\u00e7\u00e3o InfraCloud"},"status":"Habilitado","zabbix_host_id":"881384"}}
    url_linux = "https://horus.staging.globoi.com/api/hosts/create/linux"
    payload_test_linux = {
        "params": {
            "host": "CREATE-LINUX-AUTOMATED-PEDRO-34-1",
            "ip": "10.97.16.52",
            "application_id": "43ad807a-cd1b-11ee-af95-42010a62c4fc",
            "servicenow_team": "Operação InfraCloud",
            "alarm_cpu_and_memory": True
        }
    }

    headers = {
        "Authorization":"Bearer " + token 
    }
    response = requests.post(url_linux, headers = headers,json=payload_test_linux, verify=False)

    if response.status_code == 200:
        print("Success:", response.json())
    else:
        print("Failed:", response.status_code, response.text)

def create_windows(token):
    #subiu sem template
    #Failed: 201 {"data":{"application":{"id":"43ad807a-cd1b-11ee-af95-42010a62c4fc","name":"Sentry"},"created_by":"pedro.santos.martins@g.globo","creation_date":"2024-10-30T17:21:01","host":"TESTE-CREATE-WINDOWS-PEDRO","id":"cb6a0c00-5809-42be-91c5-c4a4a9cdb7b6","name":"TESTE-CREATE-WINDOWS-PEDRO","servicenow_team":{"name":"Opera\u00e7\u00e3o InfraCloud"},"status":"Habilitado","zabbix_host_id":"881385"}}
    url_linux = "https://horus-api-develop.apps.tsuru.gcp.i.globo/hosts/create/windows"
    payload_test_linux = {
        "params": {
            "host": "TESTE-CREATE-WINDOWS-PEDRO",
            "ip": "LQPAEVNSR009",
            "application_id": "43ad807a-cd1b-11ee-af95-42010a62c4fc",
            "servicenow_team": "Operação InfraCloud",
            "alarm_cpu_and_memory": True
        }
    }

    headers = {
        "Authorization":"Bearer " + token 
    }
    response = requests.post(url_linux, headers = headers,json=payload_test_linux, verify=False)

    if response.status_code == 200:
        print("Success:", response.json())
    else:
        print("Failed:", response.status_code, response.text)

def create_mysql(token):
    #subiu sem template
    #Failed: 201 {"data":{"application":{"id":"43ad807a-cd1b-11ee-af95-42010a62c4fc","name":"Sentry"},"created_by":"pedro.santos.martins@g.globo","creation_date":"2024-10-30T17:21:01","host":"TESTE-CREATE-WINDOWS-PEDRO","id":"cb6a0c00-5809-42be-91c5-c4a4a9cdb7b6","name":"TESTE-CREATE-WINDOWS-PEDRO","servicenow_team":{"name":"Opera\u00e7\u00e3o InfraCloud"},"status":"Habilitado","zabbix_host_id":"881385"}}
    url_linux = "https://horus-api-develop.apps.tsuru.gcp.i.globo/hosts/create/mysql"
    payload_test_linux = {
        "params": {
            "host": "basicos-03_mysql_globoi.com",
            "ip": "10.98.200.129",
            "application_id": "43ad807a-cd1b-11ee-af95-42010a62c4fc",
            "alarm_cpu_and_memory": True,
            "database": "basicos-03_mysql_globoi.com",
            "user": "asasad",
            "password" : "12343"
        }
    }

    headers = {
        "Authorization":"Bearer " + token 
    }
    response = requests.post(url_linux, headers = headers,json=payload_test_linux, verify=False)

    if response.status_code == 200:
        print("Success:", response.json())
    else:
        print("Failed:", response.status_code, response.text)


def create_redisl(token):
    #Failed: 500 {"error":"Error getting proxy for monitoring","message":"Proxy not available for host 10.98.200.129"}   
    url_linux = "https://horus-api-develop.apps.tsuru.gcp.i.globo/hosts/create/redis"
    payload_test_linux = {
        "params": {
            "host": "TESTE-CREATE-REDIS-PEDRO",
            "host": "10.98.202.201",
            "application_id": "43ad807a-cd1b-11ee-af95-42010a62c4fc",
            "password": "123445"
        }
    }

    headers = {
        "Authorization":"Bearer " + token 
    }
    response = requests.post(url_linux, headers = headers,json=payload_test_linux, verify=False)

    if response.status_code == 200:
        print("Success:", response.json())
    else:
        print("Failed:", response.status_code, response.text)

def create_ssl(token):
    #ailed: 400 {"error":"Error on insert statement","message":"(pymysql.err.IntegrityError) (1062, \"Duplicate entry 'ssl_api.status.salesforce3.com' for key 'host.host_UNIQUE'\")\n[SQL: INSERT INTO host (id, host, name, zabbix_host_id, application_id, host_status_id, user_id, servicenow_team_id) VALUES (%(id)s, %(host)s, %(name)s, %(zabbix_host_id)s, %(application_id)s, %(host_status_id)s, %(user_id)s, %(servicenow_team_id)s)]\n[parameters: {'id': UUID('adf51078-09ad-4e90-8b88-f55fd1212312'), 'host': 'ssl_api.status.salesforce3.com', 'name': 'ssl_api.status.salesforce3.com', 'zabbix_host_id': '881393', 'application_id': '43ad807a-cd1b-11ee-af95-42010a62c4fc', 'host_status_id': 0, 'user_id': '50a43189-bbc7-40ef-8b49-78e91a633431', 'servicenow_team_id': None}]\n(Background on this error at: https://sqlalche.me/e/20/gkpj)"}    
    url_linux = "https://horus-api-develop.apps.tsuru.gcp.i.globo/hosts/create/ssl"
    payload_test_linux = {
        "params": {
            "url": "https://api.status.salesforce3.com",
            "application_id": "43ad807a-cd1b-11ee-af95-42010a62c4fc",
            "days_to_expire": 5
        }
    }

    headers = {
        "Authorization":"Bearer " + token 
    }
    response = requests.post(url_linux, headers = headers,json=payload_test_linux, verify=False)

    if response.status_code == 200:
        print("Success:", response.json())
    else:
        print("Failed:", response.status_code, response.text)

def create_dns(token):
    #Failed: 500 {"error":"Error getting proxy for monitoring","message":"Proxy not available for host 200.219.148.10"}  
    url_linux = "https://horus-api-develop.apps.tsuru.gcp.i.globo/hosts/create/dns"
    payload_test_linux = {
        "params": {
            "dns_server": "ns1.globoi.com",
            "application_id": "43ad807a-cd1b-11ee-af95-42010a62c4fc",
            "domain": "ns1.globoi.com",
            "dns_server_name": "teste"
        }
    }

    headers = {
        "Authorization":"Bearer " + token 
    }
    response = requests.post(url_linux, headers = headers,json=payload_test_linux, verify=False)

    if response.status_code == 200:
        print("Success:", response.json())
    else:
        print("Failed:", response.status_code, response.text)

def create_mongo(token):
    #Failed: 500 {"error":"Error getting proxy for monitoring","message":"Proxy not available for host 200.219.148.10"}  
    url_linux = "https://horus-api-develop.apps.tsuru.gcp.i.globo/hosts/create/mongodb"
    payload_test_linux = {
        "params": {
            "host": "actionsapi-02-170981154513.dev.mongodb.globoi.com",
            "application_id": "43ad807a-cd1b-11ee-af95-42010a62c4fc",
            "user":"usr_zabbix",
            "password":"vgaRSbwv"

        }
    }

    headers = {
        "Authorization":"Bearer " + token 
    }
    response = requests.post(url_linux, headers = headers,json=payload_test_linux, verify=False)

    if response.status_code == 200:
        print("Success:", response.json())
    else:
        print("Failed:", response.status_code, response.text)


def delete(token):
    #Failed: 500 {"error":"Error getting proxy for monitoring","message":"Proxy not available for host 200.219.148.10"}  
    url_linux = "https://horus.staging.globoi.com/api/hosts"
    payload_test_linux = {
        "params": {
            "name": "CREATE-LINUX-AUTOMATED-PEDRO-34-1"
        }
    }

    headers = {
        "Authorization":"Bearer " + token 
    }
    response = requests.delete(url_linux, headers = headers,json=payload_test_linux, verify=False)

    if response.status_code == 200:
        print("Success:", response.json())
    else:
        print("Failed:", response.status_code, response.text)
token =get_token()

#get_application_id(token)
create_linux(token)
delete(token)
#create_windows(token)
#create_mysql(token)
#create_redisl(token)
#create_ssl(token)
#create_dns(token)
#create_mongo(token)
