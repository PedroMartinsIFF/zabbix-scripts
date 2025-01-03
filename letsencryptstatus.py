import requests
from bs4 import BeautifulSoup

url = "https://letsencrypt.status.io/"

r = requests.get(url)

site = BeautifulSoup(r.text, "html.parser")


def get_info():
    search_components = site.find_all("p", {"class": "component_name"})
    search_status = site.find_all("p", {"class": "pull-right component-status"})

    if len(search_components) != len(search_status):
          print('Inconsistencia nos dados')
    else:
        cria_string(search_components,search_status)

def cria_string(search_components,search_status):
	result = '{ "data": ['
	for i in range(len(search_components)):
		new_line ='{"Application":' +'"'+ str(search_components[i].get_text())+'"'+ ',"Status":'+'"'+str(search_status[i].get_text())+'"}'
		result = result + new_line
		if (i+1) < len(search_components):
			result = result + ","
	result = result + "]}"
	print(result)	

get_info()
