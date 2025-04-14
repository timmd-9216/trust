import json

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from tqdm import tqdm


def open_chrome(headless: bool=True) -> webdriver.Chrome:
	options = webdriver.ChromeOptions()
	if headless:
		options.add_argument('headless')
	options.add_argument('--no-sandbox')
	options.add_argument('--disable-dev-shm-usage')
	options.add_argument('--disable-gpu')
	options.add_argument('--disable-extensions')
	options.add_argument('log-level=2')
	return webdriver.Chrome(options=options)


def get_links_noticias():
	"""
	Extrae los enlaces de noticias de la sección "Lo último" del sitio La Voz.

    La función realiza lo siguiente:
      - Itera sobre 60 páginas de la sección "Lo último" (de la página 1 a la 60).
      - Para cada página, abre un navegador Chrome automatizado y accede a la URL correspondiente.
      - Espera hasta que el contenedor principal contenga elementos de enlace a las noticias.
      - Utiliza un script en JavaScript para obtener todos los atributos 'href' de los enlaces con
        la clase 'story-card-entire-link'.
      - Almacena los enlaces extraídos en un conjunto para evitar duplicados.
	  - Retorna el conjunto con todos los enlaces de noticias encontrados.
	"""
  
	links_noticias = set()
	url_ultimas_noticias = 'https://www.lavoz.com.ar/lo-ultimo/'
	for i in tqdm(range(1, 61)):
		print(url_ultimas_noticias + str(i))
		with open_chrome() as driver:
			driver.get(url_ultimas_noticias + str(i))
			main = driver.find_element(By.CSS_SELECTOR, 'section.main-content')
			while not main.find_elements(By.CSS_SELECTOR, 'a.story-card-entire-link'):
				pass
			links_noticias_pagina = driver.execute_script("""
				const links = Array.from(document.querySelectorAll('a.story-card-entire-link'));
				const links_noticias = links.map(link => link.href);
				return links_noticias;
			""")
			driver.quit()
		links_noticias_pagina = set(links_noticias_pagina)
		links_noticias.update(links_noticias_pagina)
		return links_noticias



def get_links_noticias_from_txt(txt_file):
	links_noticias = set()
	with open(txt_file) as f:
		for line in f:
			links_noticias.add(line.strip())
	return links_noticias







def get_data_noticia(link: str) -> dict | None:
	"""
	Realiza el scraping de un artículo de noticias a partir de su URL y extrae sus datos.

	Args:
		link (str): URL a scrapear.

	Returns:
		dict: Diccionario con el contenido del artículo.
	"""
	# Realiza la solicitud GET a la URL de la noticia y parsea el contenido HTML.
	soup = BeautifulSoup(requests.get(link).content, 'html.parser')
 
	if soup.find('h1').text == 'ERROR 404':
		return None

	else:
 
		# Extrae los datos de la noticia.
		data_noticia = {}
		data_noticia['link'] = link
		data_noticia['seccion'] = soup.find('div', {'class': 'story-section'}).text
		data_noticia['titulo'] = soup.find('header', {'class': 'story-title-restyling'}).text
		data_noticia['subtitulo'] = soup.find('h2', {'class': 'story-subtitle-restyling'}).text
		data_noticia['fecha_hora'] = soup.find('div', {'class': 'story-datetime-restyling'}).text
		data_noticia['autor'] = soup.find('div', {'class': 'story-author-restyling'}).text
		data_noticia['link_img'] = soup.find('div', {'class': 'story-promo'}).find('img')['src']
		data_noticia['caption_img'] = soup.find('div', {'class': 'story-promo'}).find('figcaption').text
		data_noticia['cuerpo'] = ''
		data_noticia['cuerpo_raw_html'] = []
		data_noticia['id'] = ''
		data_noticia['index'] = ''
		
		# Extrae el cuerpo de la noticia.
		cuerpo = soup.find('div', {'class': 'story'}).find('section')
	
		# Itera sobre los elementos hijos del cuerpo de la noticia.
		for elemento in cuerpo.find_all(recursive=False): 
		
			data_noticia['cuerpo_raw_html'].append(str(elemento))
	
			# Verifica si el elemento <p> contiene solo un <a>
			if elemento.name == 'p' and len(elemento.find_all(recursive=False)) == 1 and elemento.find('a'):
				continue  # Omite este párrafo
			
			if elemento.name in ('p', 'span', 'h2', 'h1', 'h5'):
				data_noticia['cuerpo'] += elemento.text + '\n'
		
			elif elemento.name in (
				'ul', 'li', 'ol', 'b', 'i', 'h3', 'h4', 'blockquote', 'br',
				'a', 'div', 'script', 'article', 'g', 'path', 'u', 'section',
				'figure', 'img', 'genoa-player', 'vf-conversation-starter',
				'figcaption', 'svg', 'iframe', 'figure', 'button'
			):
				pass
			else:
				print('Elemento no reconocido:')
				print(link)
				print(elemento.name)
				print(elemento.text)
	
		return data_noticia



def _transform_date(date_str: str) -> str:
    
	month_map = {
        'enero': '01',
		'febrero': '02',
		'marzo': '03',
		'abril': '04',
		'mayo': '05',
		'junio': '06',
		'julio': '07',
		'agosto': '08',
		'septiembre': '09',
		'octubre': '10',
		'noviembre': '11',
		'diciembre': '12'
	}
    
	day, month, year = date_str.split(' de ')
	month_num = month_map[month.lower()]
	return f"{day}-{month_num}-{year}"
 
 
def postprocess_scraped_data(data: list[dict]) -> list[dict]:
    
    for i, article in enumerate(data, start=1):
        article["id"] = f'lavoz_{i}'
        article["index"] = i
        article["fecha"], article["hora"] = article["fecha_hora"].split(",")
        article["fecha"] = _transform_date(article["fecha"])
        
    return data
        
        
def save_data(data: list[dict], output_file: str) -> None:
	"""
	Guarda los datos de las noticias en un archivo JSON.
	"""
	
	with open(output_file, 'w', encoding='utf8') as f:
		json.dump(data, f, ensure_ascii=False)
 
 
 
if __name__ == "__main__":    
    
    import json
    import time

    from tqdm import tqdm

    
    urls = [
		"https://www.lavoz.com.ar/deportes/futbol/juan-rodriguez-el-privilegio-de-pertenecer-a-talleres-y-los-goles-que-llegaron/",
		"https://www.lavoz.com.ar/ciudadanos/regionales/la-provincia-comprometio-mas-de-300-millones-de-pesos-para-obras-en-el-departamento-rio-segundo/",
		"https://www.lavoz.com.ar/deportes/futbol/javier-altamirano-jugador-de-estudiantes-deja-terapia-intensiva-luego-de-su-convulsion/",
  		"https://www.lavoz.com.ar/ciudadanos/es-saludable-o-no-eliminar-la-carne-de-la-alimentacion/",
    	"https://www.lavoz.com.ar/negocios/renault-busca-democratizar-el-acceso-a-la-movilidad-electrica-en-argentina/"

	]
    
    scraped_data = []
    
    for url in tqdm(urls):
        data = get_data_noticia(url)
        scraped_data.append(data)
        time.sleep(3)
        
    #save_data(scraped_data, 'prueba_scraped.json')
    
    print(scraped_data)
    