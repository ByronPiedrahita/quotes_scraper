import scrapy

#Titulo = response.xpath('//h1/a/text()').get()
#Citas= response.xpath('//span[@class="text" and @itemprop="text"]/text()').getall()
#Tags = response.xpath('//div/span/a[@class="tag"]/text()').getall()
#next_page_button_link = response.xpath('//li[@class="next"]/a/@href').get()
#Autor = response.xpath('//small[@class="author"]/text()').getall()

class QuotesSpider(scrapy.Spider):
    # name es el nombre unico con el scrapy se va referir al spider dentro del proyect.
    # name debe ser unico.
    name = 'quotes'
    # Defiimos una lista de url a las cuales les vamos a realizar las peticiones http.
    start_urls = [
        'http://quotes.toscrape.com/page/1/'
    ]

    custom_settings = {
        'FEED_URI': 'quotes.json',                                      #El nombre del archivo DB
        'FEED_FORMAT': 'json',                                          #El fomato del archibo DB
        'CURRENT_REQUESTS': 24,                                         #El numero de vez permitido para obtener respuestas
        'MEMUSAGE_LIMIT_MB': 2048,                                      #Limite de uso de memoria
        'MEMUSAGE_NOTIFY_MAIL': ['alfildehierro@gmail.com'],            #Correo al que notifica cuando se sobrepasa el minimo de memoria
        'ROBOTSTXT_OBEY': True,                                         #Obedese las reglas del archivo robots.txt
        'USER_AGENT': 'PepitoPerez',                                    #La persona que hizo la peticion en cabecera
        'FEED_EXPORT_ENCODING': 'utf-8'                                 #Cambia el encoding del archivo tides y ñ
    }

    def parse_only_quotes(self, response, **kwargs):
        if kwargs:
            quotes = kwargs['quotes']
            authors = kwargs['authors']
        quotes.extend(response.xpath(
            '//span[@class="text" and @itemprop="text"]/text()').getall())
        quotes.extend(response.xpath(
            '//small[@class="author" and @itemprop="author"]/text()').getall())
        
        next_page_button_link = response.xpath(
            '//ul[@class="pager"]/li[@class="next"]/a/@href').get()
        
        if next_page_button_link:
            yield response.follow(next_page_button_link, callback=self.parse_only_quotes, cb_kwargs={'quotes':quotes, 'authors':authors})
        else:
            yield { 
                'quotes': quotes
            }

    # definir el metodo parse el cual nos sirve para analizar un archivo y extraer informacion valiosa a partir de el.
    def parse(self, response):

        title = response.xpath('//h1/a/text()').get()
        top_tags = response.xpath('//div[contains(@class, "tags-box")]//span[@class="text"]/a/text()').getall()
        quotes = response.xpath('//span[@class="text" and @itemprop="text"]/text()').getall()
        authors = response.xpath('//small[@class="author" and @itemprop="author"]/text()').getall()
        
        # Si existe dentro de la ejecución de este spider un atributo de nombre
        # top lo voy a guardar en mi variable top. Si no se envía el atributo en 
        # la ejecución se guarda None en top
        top = getattr(self, 'top', None)

        if top:
            top = int(top)
            top_tags = top_tags[:top]

        yield {
            'title': title,
            'top_tags': top_tags
        }

        next_page_button_link = response.xpath('//ul[@class="pager"]/li[@class="next"]/a/@href').get()
        # Importante preguntar si la variable next_page_button_link contiene algo 
        # ya que por logica en algun momento llegariamos a ultima pagina.
        if next_page_button_link:
            # El metodo follow nos permite seguir al link (lo que hace scrapy es 
            # dejar la url absoluta y cambiar el resto) 
            # Este metodo posee un callback es decir un metodo que se ejecutara 
            # automaticamente despues de haber cambiado de url.
            yield response.follow(next_page_button_link, callback=self.parse_only_quotes, cb_kwargs={'quotes':quotes, 'authors':authors})