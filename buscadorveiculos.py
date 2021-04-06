import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
import json
from difflib import SequenceMatcher
from selenium import webdriver
import time
from datetime import date
import re
from lxml import etree

listaJson = []
totalgeral = 0

#====================================================
#      BUSCANDO DADOS DO MARKETPLACE OLX
#====================================================

def buscarDadosOLX(pages = 2, regiao = "MG"):
    global totalgeral
    regiaoBuscar = {"MG" : "belo-horizonte-e-regiao"}
    prefix = {"MG" : "mg"}
    print("INICIANDO CAPTURA - OLX")
    totalveiculos = 0

    for x in range(0, pages):
        print(" LOOP NÚMERO: " + str(x))
        url = "https://" + prefix[regiao]+".olx.com.br/"+regiaoBuscar[regiao]+"/autos-e-pecas/carros-vans-e-utilitarios"
        if x == 0:
            print("Somente a primeira pagina")
        else:
            url = "https://" + prefix[regiao]+".olx.com.br/"+regiaoBuscar[regiao]+"/autos-e-pecas/carros-vans-e-utilitarios?o="+str(x)
        
        print (url)

        PARAMS = {
            "authority" : prefix[regiao]+".olx.com.br",
            "method" : "GET",
            "path" : "/"+regiaoBuscar[regiao]+"/autos-e-pecas/carros-vans-e-utilitarios",
            "scheme":"https",
            "referer":"https://"+prefix[regiao]+".olx.com.br/autos-e-pecas/carros-vans-e-utilitarios",
            "sec-fetch-mode":"navigate",
            "sec-fetch-site":"same-origin",
            "sec-fetch-user":"?1",
            "upgrade-insecure-requests":"1",
            "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.105 Safari/537.36"
            }

        page = requests.get(url = url, headers = PARAMS)
        soup = BeautifulSoup(page.content,'lxml')
        itens = soup.findAll("li", {"class": "sc-1fcmfeb-2 juiJqh"})


        def pegaDado(pagina, campobusca, tag):

            scores = pagina.select('span:contains("'+campobusca+'")')
            divs = [score.parent for score in scores]
            html = [div.parent for div in divs]
            dado = BeautifulSoup(str(html), 'html.parser')
            if tag=="a": return dado.a.get_text()
            if tag=="span": return dado.span.get_text()

        for a in itens:
        
            try:
                
                urlVeiculo = a.find("a")["href"] #POTENCIAL PARA PEGAR LISTA DE ITENS
                
                pageitem = requests.get(url = urlVeiculo, headers = PARAMS)
                pagina = BeautifulSoup(pageitem.content,'lxml')

                scores = pagina.select('span:contains("Modelo")')
                divs = [score.parent for score in scores]
                html = [div.parent for div in divs]
                dado = BeautifulSoup(str(html), 'html.parser')
                nomeVeiculo = dado.a.get_text()

                scores = pagina.select('span:contains("Ano")')
                divs = [score.parent for score in scores]
                html = [div.parent for div in divs]
                dado = BeautifulSoup(str(html), 'html.parser')
                anoVeiculo = dado.a.get_text()

                scores = pagina.select('span:contains("Quilometragem")')
                divs = [score.parent for score in scores]
                html = [div.parent for div in divs]
                dado = BeautifulSoup(str(html), 'html.parser')
                dado.select("sc-ifAKCX cmFKIN")
                kmVeiculo = dado.get_text()
                kmVeiculo = kmVeiculo.replace("Quilometragem","")

                scores = pagina.select('h2:contains("R$ ")')
                divs = [score.parent for score in scores]
                html = [div.parent for div in divs]
                dado = BeautifulSoup(str(html), 'html.parser')
                precoVeiculo = dado.h2.get_text()
                precoVeiculo = precoVeiculo.replace("R$ ","")

                scores = pagina.select('dt:contains("Município")')
                divs = [score.parent for score in scores]
                html = [div.parent for div in divs]
                dado = BeautifulSoup(str(html), 'html.parser')
                regiaoVeiculoCidade = dado.dd.get_text()
                regiaoVeiculo = regiaoBuscar[regiao]

                scores = pagina.select('span:contains("Publicado em")')
                divs = [score.parent for score in scores]
                html = [div.parent for div in divs]
                dado = BeautifulSoup(str(html), 'html.parser')
                dado.select("sc-1oq8jzc-0 jvuXUB sc-ifAKCX fizSrB")
                diaPostagem = dado.span.get_text()

                horaPostagem = diaPostagem.split(" ")[4]
                diaPostagem =  diaPostagem.split(" ")[2]
                
                json = {
                    "fonte":"OLX",
                    "dia_postagem" : diaPostagem,
                    "hora_postagem" : horaPostagem,
                    "nomeVeiculo" : nomeVeiculo,
                    "kmVeiculo" : kmVeiculo,
                    "precoVeiculo": precoVeiculo,
                    "regiaoVeiculo":regiaoVeiculo,
                    "regiaoVeiculoCidade":regiaoVeiculoCidade,
                    "urlVeiculo":urlVeiculo,
                    "anoVeiculo":anoVeiculo,
                    "transmissaoVeiculo":"n",
                    "combustivelVeiculo":"n",
                }
                listaJson.append(json)

                totalveiculos += 1

               
                
            except:
                print("erro na busca OLX ")
            
    print("Captura OLX concluída:")
    print(str(totalveiculos) + " veículos capturados.")
    totalgeral = totalgeral + totalveiculos
    print("========================")

#====================================================
#      BUSCANDO DADOS DO MERCADOLIVRE
#====================================================


def buscarDadosMercadoLivre(pages = 2, regiao = "BH"):
    global totalgeral
    regiaoBuscar = {"BH" : "carros-caminhonetes-em-belo-horizonte-minas-gerais/", "CTBA" : "regiao-de-curitiba-e-paranagua"}
    prefix = {"BH" : "mg", "CTBA" : "pr", "SP" : "sp"}
    #https://lista.mercadolivre.com.br/veiculos/carros-caminhonetes-em-belo-horizonte-minas-gerais/
    totalveiculos = 0

    print("INICIANDO CAPTURA: MERCADOLIVRE")

    for x in range(0, pages):
        url = "https://lista.mercadolivre.com.br/veiculos/"+regiaoBuscar[regiao]
        if x == 0:
            print("primeira página")
        else:
            url = "https://lista.mercadolivre.com.br/veiculos/"+regiaoBuscar[regiao]+"_Desde_"+str((x*48)+1)

        path = "/veiculos/" + url.split("/veiculos/")[1]
        authority = url.split("/veiculos/")[0]

        PARAMS = {
            "authority" : authority,
            "method" : "GET",
            "path" : path,
            "scheme":"https",
            "referer":url,
            "sec-fetch-mode":"navigate",
            "sec-fetch-site":"same-origin",
            "sec-fetch-user":"?1",
            "upgrade-insecure-requests":"1",
            "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.105 Safari/537.36"
         }
        
        page = requests.get(url = url, headers = PARAMS)
        soup = BeautifulSoup(page.content,'lxml')
        
        results = soup.findAll("section", {"class":"ui-search-results ui-search-results--without-disclaimer"})

        try:
            itens = results[0].findAll("div", class_="ui-search-result__wrapper")
        except:
            print("Erro na busca da classe na URL: "+url)

        for a in itens:
            try:
                nomeVeiculo = a.findAll("h2", class_="ui-search-item__title ui-search-item__group__element")[0].contents[0]
                precoVeiculo = a.findAll("span", class_="price-tag-fraction")[0].contents[0]
                anoVeiculo = a.findAll("li", class_="ui-search-card-attributes__attribute")[0].contents[0]
                kmVeiculo = a.findAll("li", class_="ui-search-card-attributes__attribute")[1].contents[0]
                kmVeiculo = kmVeiculo.replace(" Km","").strip()
                urlVeiculo = a.findAll("a", class_="ui-search-result__content ui-search-link")[0]["href"]
                regiaoVeiculo = a.findAll("span",class_="ui-search-item__group__element ui-search-item__location")[0].contents[0]
                regiaoVeiculoCidade = regiaoBuscar[regiao]
                
                json = {
                    "fonte":"MercadoLivre",
                    "dia_postagem" : "n",
                    "hora_postagem" : "n",
                    "nomeVeiculo" : nomeVeiculo,
                    "kmVeiculo" : kmVeiculo,
                    "precoVeiculo": precoVeiculo,
                    "regiaoVeiculo":regiaoVeiculo,
                    "regiaoVeiculoCidade":regiaoVeiculoCidade,
                    "urlVeiculo":urlVeiculo,
                    "anoVeiculo":anoVeiculo,
                    "transmissaoVeiculo":"n",
                    "combustivelVeiculo":"n",
                }

                listaJson.append(json)
                totalveiculos += 1

            except:
                print("Erro de captura: Mercado Livre")

            
        
        print("Captura MERCADOLIVRE concluída:")
        print(str(totalveiculos) + " veículos capturados.")
        totalgeral = totalgeral + totalveiculos
        print("========================")

#====================================================
#      BUSCANDO DADOS - FACEBOOK MARKETPLACE
#====================================================

def buscarFacebook(rolagem = 2, regiao = "BH"):
    global totalgeral
    regiaoBuscar = {"BH" : "belohorizonte"}
    totalveiculos = 0
    
    #https://pt-br.facebook.com/marketplace/belohorizonte/carros/

    url = "https://pt-br.facebook.com/marketplace/"+regiaoBuscar[regiao]+"/carros/"
    print(url)
    driver = webdriver.Firefox(executable_path='C:\Python27\Tools\geckodriver\geckodriver.exe')
    
    #pegar a página web
    driver.get(url)
    

    print("INICIANDO CAPTURA: FACEBOOK MARKETPLACE")

    for a in range(0,rolagem):
        driver.execute_script('window.scrollTo("0", document.body.scrollHeight+'+str(1000*a)+');')
        time.sleep(0.5)

    #pega o conteúdo do navegador, página já com o scroll
    result = driver.page_source
    soup = BeautifulSoup(result, 'lxml')
    
    for div in soup.findAll("div", class_="kbiprv82"):
        try:
            precoVeiculo = div.findAll("span", class_="d2edcug0 hpfvmrgz qv66sw1b c1et5uql lr9zc1uh a8c37x1j keod5gw0 nxhoafnm aigsh9s9 d3f4x2em fe6kdd0r mau55g9w c8b282yb iv3no6db jq4qci2q a3bd9o3v ekzkrbhg oo9gr5id")[0].contents[0]
            precoVeiculo = precoVeiculo.replace(".","")
            precoVeiculo = precoVeiculo.replace("R$","")
            precoVeiculo = precoVeiculo.replace(" ","")
            precoVeiculo = float(precoVeiculo)
            
            nomeVeiculo = div.findAll("span", class_="a8c37x1j ni8dbmo4 stjgntxs l9j0dhe7")[0].contents[0]
            regiaoVeiculoCidade = div.findAll("span", class_="a8c37x1j ni8dbmo4 stjgntxs l9j0dhe7 ltmttdrg g0qnabr5 ojkyduve")[0].contents[0]
            regiaoVeiculoCidade = regiaoVeiculoCidade.split(", ")[0]

            urlVeiculo = "https:/www.facebook.com"+div.find("a")["href"]

            try:
                kmVeiculo = div.findAll("span", class_="a8c37x1j ni8dbmo4 stjgntxs l9j0dhe7 ltmttdrg g0qnabr5 ojkyduve")[1].contents[0]
                kmAjustada = ""
                if "km" in kmVeiculo:
                    kmAjustada = kmVeiculo.split("km")[0].replace(",","")
                    if "mil" in kmVeiculo:
                        kmAjustada = kmAjustada.replace("mil","")
                    kmVeiculo = float(kmAjustada)*1000
            
            except:
                print("erro km em : " + nomeVeiculo)
                kmVeiculo = "n"

            anoVeiculo = float(nomeVeiculo.split(" ")[0])
            nomeVeiculo = str(nomeVeiculo)[5:]
            
            json = {
                    "fonte":"FacebookMarketplace",
                    "dia_postagem" : "n",
                    "hora_postagem" : "n",
                    "nomeVeiculo" : nomeVeiculo,
                    "kmVeiculo" : kmVeiculo,
                    "precoVeiculo": precoVeiculo,
                    "regiaoVeiculo":"n",
                    "regiaoVeiculoCidade":regiaoVeiculoCidade,
                    "urlVeiculo":urlVeiculo,
                    "anoVeiculo":anoVeiculo,
                    "transmissaoVeiculo":"n",
                    "combustivelVeiculo":"n",
            }
            
            listaJson.append(json)

        except: 
            print("Erro de captura: Facebook Marketplace")    

    driver.quit()
    print("Captura FACEBOOK concluída:")
    print(str(totalveiculos) + " veículos capturados.")
    totalgeral = totalgeral + totalveiculos
    print("========================")


buscarFacebook(rolagem=120)
buscarDadosMercadoLivre(pages = 10)
buscarDadosOLX(pages = 10)
print("===========================")
print("VEICULOS CAPTURADOS:")
print("===========================")
print(totalgeral)
print("===========================")

#exportando no final...:
df = pd.DataFrame(listaJson)
df.to_excel("veiculos.xlsx")
df.to
