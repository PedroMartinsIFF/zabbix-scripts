#!/usr/bin/python3
import oci
import json


def initialize_oci_config(region):
    try:
        # Tenta inicializar as configurações da OCI
        config = {
        "user": 'ocid1.user.oc1..aaaaaaaaiitqtrimhb3ygrux5jcib5b4icy4mjzwaon62tqitdtjvif7vyrq',
        "key_file": '/Users/pedromartins/Documents/Trabalho/zabbix-scripts/credenciais/key.pem',
        "fingerprint": '47:78:66:99:cd:4c:59:d6:8a:fd:59:6b:f2:7b:5d:e7',
        "tenancy": 'ocid1.tenancy.oc1..aaaaaaaand4xcanpaqckfaohjrk66dccmt65my7m7ckz5p3n2hf5ccza6skq',
        "region": region
        }
        oci.config.validate_config(config)
        return config
    except oci.exceptions.ConfigFileInvalid as e:
        print('Erro: Arquivo de configuração inválido. Verifique o conteúdo do arquivo')

def init_limit_client(config):
    limits_client = oci.limits.LimitsClient(config)
    return limits_client

def get_limits_definitions(config,client):
    limits_definitions = client.list_limit_definitions(compartment_id='ocid1.tenancy.oc1..aaaaaaaand4xcanpaqckfaohjrk66dccmt65my7m7ckz5p3n2hf5ccza6skq')
    data = json.loads(str(limits_definitions.data))
    return data

def get_limits_usage_rate(config,client,data):
    result = '{ "data": ['
    cont = 0
    for limit in data:
        try:
            limits = client.get_resource_availability(compartment_id='ocid1.tenancy.oc1..aaaaaaaand4xcanpaqckfaohjrk66dccmt65my7m7ckz5p3n2hf5ccza6skq',service_name=limit['service_name'],limit_name=limit['name'])
            json_data = json.loads(str(limits.data))
            new_line ='{"service_name":' +'"'+ str(limit['service_name'])+'"'+ ',"limit_name":'+'"'+str(limit['name'])+'"'+ ',"available":'+'"'+str(json_data['available'])+'"'+ ',"used":'+'"'+str(json_data['used'])+'"'+'}'
            #print(f"{limit['service_name']},{limit['name']},{json_data['available']},{json_data['used']},{json_data['fractional_availability']},{json_data['fractional_usage']}")
            result = result + new_line
            cont +=1
            if (cont+1) < len(data):
                result = result + ","
        except:
            print(limit)
    result = result + "]}"
    return result

def main():
    region = 'sa-saopaulo-1'
    config = initialize_oci_config(region)
    client = init_limit_client(config)
    limits = get_limits_definitions(config,client)
    print(get_limits_usage_rate(config,client,limits))

main()
