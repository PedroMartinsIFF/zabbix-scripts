from ast import alias
from multiprocessing.reduction import ACKNOWLEDGE
from time import clock_getres
from xml.etree.ElementTree import Comment
from pyzabbix import ZabbixAPI
from argparse import ArgumentParser
from datetime import date, time, datetime, timedelta
import csv
import datetime

parser = ArgumentParser(description='Retorna lista de itens de n hosts')
parser.add_argument('--url-api', dest='url_api', help='URL Zabbix API')
parser.add_argument('--user', dest='user', help='Zabbix user')
parser.add_argument('--password', dest='password', help='Zabbix password')
parser.add_argument('--saida', dest='saida', help='Arquivo de saida')
args = parser.parse_args()

if args.url_api:
	zapi = ZabbixAPI(args.url_api, timeout=600.0)
	try:
		zapi.login(args.user, args.password)
		print("Logged")
	except Exception as e:
		print(e)
		exit(1)
else:
	print("Erro ao logar na API.")
	exit(0)

#hostListAck = [[{'eventid': '966574', 'acknowledges': [{'clock': '1656955378', 'message': ',', 'alias': 'ketlen.belarmino'}]}], [{'eventid': '866709', 'acknowledges': [{'clock': '1656955367', 'message': 'l', 'alias': 'ketlen.belarmino'}]}]]
#problemsHost = zapi.event.get(output = ['acknowledges'],hostids=['51656'], acknowledged = 'true',time_till='1648782000' ,select_acknowledges = ['clock','message', 'alias'],selectHosts=['name'], selectRelatedObject=['status'], limit=2)


def getHostData():
	problemsHost = zapi.event.get(output = ['acknowledges','name'],groupids=['1567'],time_till='1646103600', acknowledged = 'true' ,select_acknowledges = ['clock','message', 'alias'],selectHosts=['name', 'status'], selectRelatedObject=['status', 'triggerid','value'])
	print(len(problemsHost))
	count=0
	for i in range(len(problemsHost)):
		status = problemsHost[i]['relatedObject']['status']
		status_host = problemsHost[i]['hosts'][0]['status']
		status_problem = problemsHost[i]['relatedObject']['value']
		if status == '0' and status_host== '1' and status_problem =='1':
			print(problemsHost[i]['relatedObject']['triggerid'])
			count+=1
	print(count)
	return problemsHost

def auditData(dataHosts):
	with open(args.saida, 'w') as arquivo:
		print("HOSTNAME,ALIAS,COMMENT,CLOCK,TRIGGER", file=arquivo)
		for i in range (len(dataHosts)):
			status = dataHosts[i]['relatedObject']['status']
			status_host = dataHosts[i]['hosts'][0]['status']
			status_problem = dataHosts[i]['relatedObject']['value']
			if status == '0' and status_host== '1' and status_problem =='1':
				try:
					len_count=len(dataHosts[i]['hosts'])
					hostname=dataHosts[i]['hosts'][len_count-1]['name']
					trigger=dataHosts[i]['relatedObject']['triggerid']
					len_count=len(dataHosts[i]['acknowledges'])
					alias=dataHosts[i]['acknowledges'][len_count-1]['alias']
					comment=dataHosts[i]['acknowledges'][len_count-1]['message']
					clock=dataHosts[i]['acknowledges'][len_count-1]['clock']
					clock_date = datetime.datetime.fromtimestamp(int(clock)).isoformat()
					print(f'{hostname},{alias},{comment},{clock_date},{trigger}',file=arquivo)
				except:
					print('Erro ao retornar info do host',hostname )
					print(f'{hostname},{"---"},{"---"},{"---"},{trigger}',file=arquivo)


def disableTrigger(dataHosts):
	for i in range(len(dataHosts)):
		id = dataHosts[i]['relatedObject']['triggerid']
		status = dataHosts[i]['relatedObject']['status']
		status_host = dataHosts[i]['hosts'][0]['status']
		status_problem = dataHosts[i]['relatedObject']['value']
		if status == '0' and status_host== '1' and status_problem =='1':
			zapi.trigger.update(triggerid=id,status=1)



def initApp():
	dataHosts = getHostData()
	auditData(dataHosts)
	disableTrigger(dataHosts)
	#hostsAck = timeStampTreatment(dataHosts)
	#creatArchiveAck = creatArchive(dataHosts)

	
initApp()
zapi.user.logout()
