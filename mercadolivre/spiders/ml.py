import scrapy

class MlSpider(scrapy.Spider):
    name = 'ml'
    #allowed_domains = ['mercadolivre.com']

    #URL inicial do scrapy
    
    start_urls = ['https://lista.mercadolivre.com.br/veiculos-em-minas-gerais/']

    def parse(self, response, **kwargs):

        for i in response.xpath('//li[@class="ui-search-layout__item"]'):
            titulo = i.xpath('.//h2[@class="ui-search-item__title ui-search-item__group__element"]//text()').get()
            valor = i.xpath('.//span[@class="price-tag-fraction"]//text()').getall()
            anokm = i.xpath('.//li[@class="ui-search-card-attributes__attribute"]//text()').getall()
            cidade = i.xpath('.//span[@class="ui-search-item__group__element ui-search-item__location"]//text()').get()
            foto = i.xpath('.//img/@data-src').get()
            link = i.xpath('.//a/@href').get()

            #corrigindo bug no PYTHON
            anokm.append("km") 
                        
            #dicionário de dados:
            yield {
                'titulo' : titulo,
                'valor' : valor,
                'ano' : anokm[0],
                'km' : anokm[1],
                'cidade' : cidade,
                'foto' : foto,
                'link' : link
            }
            
        
        proximapagina = response.xpath('//a[contains(@title, "Seguinte")]/@href').get()

        if proximapagina:
                yield scrapy.Request(url=proximapagina, callback=self.parse)