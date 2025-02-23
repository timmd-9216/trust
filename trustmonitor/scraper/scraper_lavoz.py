import json
import os
from typing import Optional

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from tqdm import tqdm

from trustmonitor.scraper.helpers import _transform_date


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



def get_links_noticias_from_txt(txt_file: str) -> list:
    links_noticias = []
    with open(txt_file) as f:
        for line in f:
            links_noticias.append(line.strip())
    return links_noticias




def download_htmls_from_links(links: list, output_dir: str) -> None:
    """
    Esta función permite descargar los archivos HTML de las noticias a partir de los enlaces proporcionados.
    El único objetivo es realizar el request una única vez y obtener los archivos completos, para probar y evaluar el scrapping.

    Args:
        links (set): Links a scrapear.
        output_dir (str): Directorio de salida para guardar los archivos HTML y el json.
    """
    
    if not os.path.exists(f"{output_dir}/htmls"):
        os.makedirs(f"{output_dir}/htmls")
    
    urls_list = []
    i = 0
    
    links = links[i:]
    
    for link in tqdm(links):
    
        html = requests.get(link).content
        filename = f"{output_dir}/htmls/lavoz_{i}.html"
        
        urls_list.append(
            {
                "url": link,
                "filename": filename
            }
        )

        # Guardar el contenido en un archivo HTML
        with open(filename, "wb") as file:
            file.write(html)
            
        i += 1
        time.sleep(3)
        
        with open(f"{output_dir}/urls_files_list.json", "w") as file:
            json.dump(urls_list, file, indent=4)



def get_scraped_data_noticia(link: str, html_file: Optional[str]) -> dict | None:
    """
    Realiza el scraping de un artículo de noticias a partir de su URL y extrae sus datos.
    En caso de que ya se tengan scrapeados los htmls para evitar hacer nuevos requests, se puede 
    pasar el archivo (con su link correspondiente) y obtener la información.
    
    Args:
        link (str): URL a scrapear.
        html_file (Optional[str]): Archivo html para evitar realizar un request al procesar los datos.

    Returns:
        dict | None: Diccionario con el contenido del artículo. En caso de que el link no esté vigente devuelve None.
    """
    
    if html_file:
        # Si se pasa un archivo HTML, lo abre y parsea.
        with open(html_file, 'r', encoding='utf8') as f:
            soup = BeautifulSoup(f, 'html.parser')
    else:
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




 
 
def postprocess_scraped_data(data: list[dict]) -> list[dict]:
    """
    Función de postprocesamiento de los datos scrapeados de las noticias de la voz.
    - Agrega id.
    - Agrega index.
    - Normaliza la fecha y hora.

    Args:
        data (list[dict]): _description_

    Returns:
        list[dict]: _description_
    """
    
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
 
 
 #def scraping_pipeline_lavoz(output_file: str) -> None:
     
     
    
 
 
 
if __name__ == "__main__":    
    
    import json
    import time

    from tqdm import tqdm

    # urls = [
    # 	"https://www.lavoz.com.ar/deportes/futbol/juan-rodriguez-el-privilegio-de-pertenecer-a-talleres-y-los-goles-que-llegaron/",
    # 	"https://www.lavoz.com.ar/ciudadanos/regionales/la-provincia-comprometio-mas-de-300-millones-de-pesos-para-obras-en-el-departamento-rio-segundo/",
    # 	"https://www.lavoz.com.ar/deportes/futbol/javier-altamirano-jugador-de-estudiantes-deja-terapia-intensiva-luego-de-su-convulsion/",
      # 	"https://www.lavoz.com.ar/ciudadanos/es-saludable-o-no-eliminar-la-carne-de-la-alimentacion/",
    # 	"https://www.lavoz.com.ar/negocios/renault-busca-democratizar-el-acceso-a-la-movilidad-electrica-en-argentina/"

    # ]
    
    # scraped_data = []
    
    # for url in tqdm(urls):
    #     data = get_data_noticia(url)
    #     scraped_data.append(data)
    #     time.sleep(3)
        
    # #save_data(scraped_data, 'prueba_scraped.json')
    
    # print(scraped_data)
    
    # TODO Cambiar rutas por relativas del proyecto desde root.
    urls = get_links_noticias_from_txt(r"C:\Users\jcc\JuanCruz\repositorios-activos\timmd\trust\notebooks\htmls\urls.txt")
    print(urls)
    download_htmls_from_links(urls, r"C:\Users\jcc\OneDrive\Escritorio\prueba")