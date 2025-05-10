# Trust Docs - v0

# Introducción

El proyecto Trust se desarrolla en búsqueda de una herramienta de asistencia para editores de medios periodísticos, aplicando técnicas de inteligencia artificial (AI). Su objetivo principal es ayudar y acelerar el proceso de revisión de noticias periodísticas en la edición previo a su publicación. 

Esto se logra realizando un análisis automático de los componentes del artículo periodístico aplicando técnicas de procesamiento de lenguaje natural (NLP) para la extracción de *features* de sus componentes y la construcción de métricas que representan la calidad periodística estimada por el modelo.

Actualmente este proyecto contiene el *backend* encargado de la ingesta, procesamiento y entrega de una o más noticias recibidas.
# Procesamiento de Artículos

Actualmente la aplicación desarrollada permite el procesamiento de uno o más artículos, permitiendo la extracción de atributos de sus elementos mediante el uso de modelos de procesamiento de lenguaje natural pre-entrenados. 

El servicio está desarrollado en Python utilizando Flask y contiene un único *endpoint* que recibe el/los artículo/s, realiza el procesamiento y devuelve el resultado en formato *json*. 

Por el momento la herramienta utiliza 3 motores para el análisis de textos:

- Stanza
- Spacy
- Pysentimiento

## Stanza

Es una librería de procesamiento de lenguaje natural desarrollada por el Stanford NLP Group. Está diseñada para ser fácil de usar y altamente precisa, ofreciendo modelos preentrenados para muchos idiomas. Entre sus funciones se pueden destacar:

- Tokenización
- Lematización
- Análisis morfosintáctico (POS tagging)
- Reconocimiento de entidades nombradas (NER)
- Análisis de dependencias gramaticales
- Segmentación de oraciones

Stanza se destaca por su arquitectura modular, basada en redes neuronales profundas, y su compatibilidad con los datos multilingües.

https://stanfordnlp.github.io/stanza/

## Spacy

Es una librería de procesamiento de lenguaje natural en Python, diseñada para ser rápida, robusta y orientada a aplicaciones de producción. Ofrece modelos preentrenados para múltiples idiomas y permite realizar tareas clave de NLP con gran eficiencia.

Algunas de sus características principales incluyen:

- Tokenización
- Lematización
- Análisis morfosintáctico (POS tagging)
- Reconocimiento de entidades nombradas (NER)
- Análisis de dependencias gramaticales
- Vectorización de palabras con modelos de embeddings

Esta librería está optimizada para velocidad y escalabilidad en aplicaciones reales, no solo para investigación.

https://spacy.io/

## Pysentimiento

Es una librería de Python diseñada para análisis de sentimiento y detección de emociones en textos, especialmente en español y otros idiomas. Está construida sobre modelos preentrenados de *Transformers* (como BERT y RoBERTa), facilitando el uso de modelos de clasificación de texto sin necesidad de configurar arquitecturas complejas.

Sus características principales incluyen:

- Análisis de sentimiento (positivo, negativo, neutro)
- Detección de emociones (alegría, tristeza, enojo, etc.)
- Detección de odio (*hate speech detection*)
- Modelos disponibles para varios idiomas, principalmente español, inglés y portugués

https://github.com/pysentimiento/pysentimiento

# Detecciones

A partir del uso en conjunto de las herramientas que proveen las librerías previamente mencionadas, sumado a desarrollos propios y heurísticas, Trust realiza y organiza múltiples detecciones sobre el/los articulo/s recibidos.

## Entidades

El módulo de detección de entidades se encarga de extraer del cuerpo de la noticia las entidades nombradas del artículo. Esto incluye Personas, Organizaciones, Lugares y Entidades Misceláneas.

### Potencial Línea de Continuación - Mapa de Entidades

Posibilidad de generar un mapa de las entidades presentes en un corpus de artículos. Cada entidad podría estar asociada a los artículos en los que aparece, a qué otras entidades aparecen con ella, qué sentimiento tiene vinculado, en qué calidad aparece en el artículo (mencionado en citas o como referenciado).

Esta línea puede estar asociada a una base de datos curada de entidades relevantes, que permitan avanzar en un postprocesamiento de **unificación de entidades**. Esta base de datos puede estar vinculada con información extraída automáticamente de wikipedia. 

Otro paso sería vincular la entidades relevantes mediante un mapa pero utilizando los artículos de wikipedia en vez del corpus de noticias, de manera que se puedan encontrar nuevas relaciones de entidades.

## Adjetivos

La detección de adjetivos en el texto busca identificar calificativos que puedan modificar sustantivos importantes en la construcción narrativa de la noticia. El análisis de adjetivos proporciona una capa adicional de interpretación sobre el tono y la subjetividad de la redacción.

### Potencial Línea de Continuación

- Clasificación más específica de los tipos de adjetivos detectados.

## Sentimiento

Este módulo es el encargado de realizar un análisis automático del sentimiento presente en el texto de la noticia. Utiliza modelos de clasificación para determinar la polaridad general (positiva, negativa o neutra) del artículo completo.

### Potencial Línea de Continuación

- Nuevas componentes o métricas a partir agregar el resultado del análisis de sentimiento de cada una de las oraciones del texto por separado.
- Nuevas componentes o métricas a partir agregar el resultado del análisis de sentimiento de cada párrafo del texto por separado.
- Análisis focalizado del sentimiento asociado a segmentos específicos del texto, como oraciones o párrafos, para detectar cambios de tono o énfasis emocional en diferentes partes del artículo.
- Investigar la utilidad de una medida de concordancia entre los sentimientos para transmitir confianza (grado de coherencia entre el sentimiento del título, cuerpo, oraciones, párrafo).
- Profundizar sentimientos asociados a entidades de la noticia.

## Fuentes

Las fuentes periodísticas de una noticia resultan un importante indicador a la hora de determinar la solidez de la información transmitida en un artículo. Es por eso que Trust contiene un módulo específico para el uso de las detecciones previas para la construcción de detecciones automáticas de citas en el texto procesado.

El método utilizado por Trust incorpora las detecciones de Entidades, Estructura del Texto (POS) y patrones generales para detectar citas directas o explícitas. Las mismas tienen como condición la presencia de comillas que definan la afirmación.

> “No hay una prioridad de un torneo sobre otro. Solamente pensamos en Vélez. El torneo local no lo podemos descuidar. Cuando llegue el momento de los Libertadores lo veremos de la mejor manera” sostuvo Rodríguez.
> 

Además de la afirmación, son detectados el conector y el referenciado de la cita.

### Potencial Línea de Continuación

Investigar las posibilidades de detección de citas indirectas o implícitas, como sería la siguiente estructura que contiene una transformación de la cita del ejemplo anterior.

> Rodríguez sostiene que no hay una prioridad de un torneo sobre otro y que únicamente piensa en Vélez.
> 

Algunas posibilidades para avanzar en esta línea:

- Generación de base de datos de verbos utilizados en citas directas y que generalmente están incluidos en citas indirectas.
- Uso de *LLMs* para detección de citas indirectas.

# Input

El siguiente es un ejemplo del input que se está utilizando en el modelo para el procesamiento. Cada noticia contiene los componentes link, sección, título, cuerpo, autor, id, fecha, entre otros.

```json
[
    {
        "link": "https://www.lavoz.com.ar/deportes/futbol/juan-rodriguez-el-privilegio-de-pertenecer-a-talleres-y-los-goles-que-llegaron/",
        "seccion": " Mundo D  /  Fútbol  / Talleres",
        "titulo": "Talleres. Juan Rodríguez, el privilegio de pertenecer a Talleres y los goles que llegaron",
        "subtitulo": "El defensor fue comprado por el club a los 30 años para pelear en todos los frentes. “Tenía mis dudas por la edad”, se sinceró el ex Defensa. ",
        "fecha_hora": "22 de marzo de 2024,07:41",
        "autor": "Redacción LAVOZ",
        "link_img": "https://www.lavoz.com.ar/resizer/v2/4ZVQHY4YAJB6NKYTRNDHGWNA2M.jpg?quality=75&smart=true&auth=8994663f0c13d835ca05d94805212bba5bf96b8384114dd0e0a57dc2ae850657&width=980&height=640",
        "caption_img": "Juan Rodríguez. Talleres compró su pase para ser protagonista en Copa de la Liga Profesional, Argentina, Libertadores, Liga Profesional y Supercopa Internacional. ",
        "cuerpo": "En este 2024, Talleres arrancó con Copa de la Liga Profesional, siguió por Copa Argentina, continuará con la Libertadores -arranca el 4/4 ante Sao Pablo-, la Liga Profesional y vendrá la final de la Supercopa Internacional ante un River, que fue donde empezó.\n“No hay una prioridad de un torneo sobre otro. Solamente pensamos en Vélez. El torneo local no lo podemos descuidar. Cuando llegue el momento de los Libertadores lo veremos de la mejor manera”, sostuvo Rodríguez, este miércoles en el CARD, a poco de comenzar la preparación del juego con Vélez, el que sería el sábado 30 de marzo, tras el parate por la doble fecha Fifa de amistosos de selecciones.\n-¿Qué te pareció el grupo que le tocó en Libertadores?\n
        ...
        \n-Tenía mis dudas por la edad. Por ser defensor, que cuesta un poco más y después por una futura venta. Pero sí me tenía fe por por lo que había rendido, así que estoy muy contento. Es la segunda venta.\n-Llegaron tus goles, empezaste a darle un extra a Talleres...\n-No solamente yo, sino que casi todos los defensores . Vos pasó el semestre pasado que, por ahí, los defensores no hicimos tantos goles o no aportamos muchos en eso. Creo que este semestre arrancamos bastante bien. Eso ayuda al equipo y a la confianza.\n",
        "cuerpo_raw_html": [
            "<p><a href=\"https://www.transfermarkt.com.ar/juan-gabriel-rodriguez/profil/spieler/189448\" target=\"_blank\">Juan Gabriel Rodríguez (30 años) se hizo un lugar en el Mundo Talleres. </a>Llegó el año pasado, fue parte del equipo subcampeón de la Liga Profesional, pero también libró una dura lucha contra algunas lesiones que lo condicionaron. Sin embargo, cuando se venció su préstamo, el presidente Andrés Fassi ejecutó la opción y después de duras negociaciones, el pase del “Negro” fue comprado por Talleres.</p>",
            "<p>En este 2024, Talleres arrancó con Copa de la Liga Profesional, siguió por Copa Argentina, continuará con la Libertadores -arranca el 4/4 ante Sao Pablo-, la Liga Profesional y vendrá la final de la Supercopa Internacional ante un River, que fue donde empezó.</p>",
	          ...
            ,
            "<article class=\"story-card related\"><a class=\"story-card-entire-link\" href=\"/deportes/futbol/talleres-ya-piensa-en-un-velez-lider-como-esta-bruno-barticciotto/\" rel=\"\"></a><div class=\"story-card-image\"><a href=\"/deportes/futbol/talleres-ya-piensa-en-un-velez-lider-como-esta-bruno-barticciotto/\" rel=\"\" title=\"Bruno Barticciotto, en rehabilitación. El delantero de Talleres tuvo un comienzo de año difícil. Podría estar a disposición ante Vélez\"><figure><img alt=\"Bruno Barticciotto, en rehabilitación. El delantero de Talleres tuvo un comienzo de año difícil. Podría estar a disposición ante Vélez\" decoding=\"async\" fetchpriority=\"low\" height=\"154\" loading=\"lazy\" src=\"https://www.lavoz.com.ar/resizer/v2/3UO6YEZ66BCNZAJG3SVDUCDR3E.jpg?quality=75&amp;smart=true&amp;auth=6dbfc0929cbade8499bcd5142088f3f101864247c21ffe0d9fa866a0fca3c84f&amp;width=154&amp;height=154\" width=\"154\"/></figure></a></div><div class=\"story-card-content\"><h4 class=\"story-card-section\"><a href=\"/deportes/futbol/\" rel=\"\" title=\"Fútbol\">Fútbol</a></h4><h3 class=\"story-card-title\"><a href=\"/deportes/futbol/talleres-ya-piensa-en-un-velez-lider-como-esta-bruno-barticciotto/\" rel=\"\" title=\"Talleres ya piensa en un Vélez líder, cómo está Bruno Barticciotto\"><span>Talleres.<!-- --> </span>Talleres ya piensa en un Vélez líder, cómo está Bruno Barticciotto</a></h3><div class=\"story-card-author\"><a href=\"/autor/edidigital/\" title=\"Redacción LAVOZ\">Redacción LAVOZ</a></div></div></article>"
        ],
        "id": "lavoz_1",
        "index": 1,
        "fecha": "22-03-2024",
        "hora": "07:41",
        "reviewed": false
    },
```

# Output Actual

Podemos ver un ejemplo del output completo para una noticia.

```json
"id": "lavoz_1",
"entities": {
    "entities_list": [
        {
            "text": "Talleres",
            "type": "Organización",
            "sentiment": 2,
            "start_char": 14,
            "end_char": 22
        },
        ...
        {
            "text": "Copa de la Liga Profesional",
            "type": "Misceláneo",
            "sentiment": 2,
            "start_char": 35,
            "end_char": 62
        }
	    ],
      "entities_freq": [
          [
              [
                  "Vélez",
                  "Persona"
              ],
              4
          ],
          ...
          [
              [
                  "Talleres",
                  "Organización"
              ],
              2
          ]
},
"adjectives": {
    "adjectives_list": [
        {
            "text": "local",
            "features": {
                "Number": "Sing"
            },
            "start_char": 346,
            "end_char": 351
        },
        ...
        {
            "text": "mejor",
            "features": {
                "Degree": "Cmp",
                "Number": "Sing"
            },
            "start_char": 439,
            "end_char": 444
        }
     ],
			"adjectives_freq": [
			                [
			                    "bueno",
			                    6
			                ],
			                ...
			                [
			                    "mejor",
			                    2
			                ]
			]
},
"sentiment": {
            "global_sentiment": [
                "NEU",
                0.6979541778564453
            ],
            "highest_scoring_sentence_per_label": {
                "POS": {
                    "score": 0.9584013223648071,
                    "start_char": 780,
                    "end_char": 825,
                    "sentence": " Estoy muy contento con el grupo que nos tocó"
                },
                "NEG": {
                    "score": 0.9649368524551392,
                    "start_char": 2524,
                    "end_char": 2580,
                    "sentence": " La realidad es que el fútbol argentino es muy irregular"
                },
                "NEU": {
                    "score": 0.8391280770301819,
                    "start_char": 1200,
                    "end_char": 1240,
                    "sentence": " Después veremos cuando llegue el tiempo"
                }
            },
            "title_sentiment": {
                "label": "POS",
                "scores": {
                    "NEG": 0.008031394332647324,
                    "NEU": 0.09081562608480453,
                    "POS": 0.901153028011322
                }
            }
        },
"sources": [
	    {
	        "text": "“No hay una prioridad de un torneo sobre otro. Solamente pensamos en Vélez. El torneo local no lo podemos descuidar. Cuando llegue el momento de los Libertadores lo veremos de la mejor manera”, sostuvo Rodríguez",
	        "start_char": 260,
	        "end_char": 471,
	        "length": 211,
	        "pattern": "Q.VP",
	        "explicit": true,
	        "components": {
	            "afirmacion": {
	                "text": "“No hay una prioridad de un torneo sobre otro. Solamente pensamos en Vélez. El torneo local no lo podemos descuidar. Cuando llegue el momento de los Libertadores lo veremos de la mejor manera”",
	                "start_char": 260,
	                "end_char": 452,
	                "label": "Afirmacion"
	            },
	            "conector": {
	                "text": "sostuvo",
	                "start_char": 454,
	                "end_char": 461,
	                "label": "Conector"
	            },
	            "referenciado": {
	                "text": "Rodríguez",
	                "start_char": 462,
	                "end_char": 471,
	                "label": "Referenciado"
	            }
	        }
	    },
	    ...
	]
},
"metrics": {
        "general": {
            "num_chars": {
                "name": "num_chars",
                "value": 3968,
                "reference": 1000,
                "full_name": "Cantidad de caracteres del cuerpo"
            },
            "num_chars_title": {
                "name": "num_chars_title",
                "value": 89,
                "reference": 30,
                "full_name": "Cantidad de caracteres del título"
            },
            "num_words": {
                "name": "num_words",
                "value": 812,
                "reference": 500,
                "full_name": "Cantidad de palabras"
            },
            "num_sentences": {
                "name": "num_sentences",
                "value": 51,
                "reference": 30,
                "full_name": "Cantidad de oraciones"
            }
        },
        "entities": {
            "num_entidades": {
                "name": "num_entidades",
                "value": 25,
                "reference": 12,
                "full_name": "Cantidad de entidades en el texto"
            },
            "num_entidades_persona": {
                "name": "num_entidades_persona",
                "value": 10,
                "reference": 3,
                "full_name": "Cantidad de entidades Persona en el texto"
            },
            "num_entidades_organizacion": {
                "name": "num_entidades_organizacion",
                "value": 3,
                "reference": 3,
                "full_name": "Cantidad de entidades Organización en el texto"
            },
            "num_entidades_lugar": {
                "name": "num_entidades_lugar",
                "value": 3,
                "reference": 3,
                "full_name": "Cantidad de entidades Lugar en el texto"
            },
            "num_entidades_misc": {
                "name": "num_entidades_misc",
                "value": 9,
                "reference": 3,
                "full_name": "Cantidad de entidades Misceláneo en el texto"
            }
        },
        "sentiment": {
            "sentimiento_global_negativo": {
                "name": "sentimiento_global_negativo",
                "value": 0.03656395897269249,
                "reference": 0.33,
                "full_name": "Sentimiento global positivo"
            },
            "sentimiento_global_neutro": {
                "name": "sentimiento_global_neutro",
                "value": 0.6979541778564453,
                "reference": 0.33,
                "full_name": "Sentimiento global positivo"
            },
            "sentimiento_global_positivo": {
                "name": "sentimiento_global_positivo",
                "value": 0.2654818594455719,
                "reference": 0.33,
                "full_name": "Sentimiento global positivo"
            }
        },
        "adjectives": {
            "perc_adjectives": {
                "name": "perc_adjectives",
                "value": 0.24630541871921183,
                "reference": 7.000000000000001,
                "full_name": "Porcentaje de adjetivos en el texto"
            },
            "num_adjectives": {
                "name": "num_adjectives",
                "value": 40,
                "reference": 20,
                "full_name": "Cantidad de adjetivos en el texto"
            }
        },
        "sources": {
            "num_afirmaciones": {
                "name": "num_afirmaciones",
                "value": 1,
                "reference": 2,
                "full_name": "Cantidad de citas identificadas"
            },
            "num_afirmaciones_explicitas": {
                "name": "num_afirmaciones_explicitas",
                "value": 1,
                "reference": 2,
                "full_name": "Cantidad de citas explícitas"
            },
            "num_referenciados": {
                "name": "num_referenciados",
                "value": 1,
                "reference": 2,
                "full_name": "Cantidad de Referenciados"
            },
            "num_referenciados_unique": {
                "name": "num_referenciados_unique",
                "value": 1,
                "reference": 2,
                "full_name": "Cantidad de Referenciados Únicos"
            },
            "num_conectores": {
                "name": "num_conectores",
                "value": 1,
                "reference": 2,
                "full_name": "Cantidad de Conectores"
            },
            "num_conectores_unique": {
                "name": "num_conectores_unique",
                "value": 1,
                "reference": 2,
                "full_name": "Cantidad de Conectores Únicos"
            }
        }
      }
    }
  }
}
```

## Entidades

El componente de entidades del output incluye una lista de las mismas con su ubicación en el texto y una lista de sus frecuencias en el artículo.

```json
"entities": {
    "entities_list": [
        {
            "text": "Talleres",
            "type": "Organización",
            "sentiment": 2,
            "start_char": 14,
            "end_char": 22
        },
        ...
        {
            "text": "Copa de la Liga Profesional",
            "type": "Misceláneo",
            "sentiment": 2,
            "start_char": 35,
            "end_char": 62
        }
	    ],
      "entities_freq": [
          [
              [
                  "Vélez",
                  "Persona"
              ],
              4
          ],
          ...
          [
              [
                  "Talleres",
                  "Organización"
              ],
              2
          ]
},
```

## Adjetivos

El componente de adjetivos del output incluye una lista de los mismos con su ubicación en el texto y una lista de sus frecuencias en el artículo.

```json
"adjectives": {
    "adjectives_list": [
        {
            "text": "local",
            "features": {
                "Number": "Sing"
            },
            "start_char": 346,
            "end_char": 351
        },
        ...
        {
            "text": "mejor",
            "features": {
                "Degree": "Cmp",
                "Number": "Sing"
            },
            "start_char": 439,
            "end_char": 444
        }
     ],
			"adjectives_freq": [
			                [
			                    "bueno",
			                    6
			                ],
			                ...
			                [
			                    "mejor",
			                    2
			                ]
			]
},
```

## Sentimiento

Las detecciones del sentimiento incluyen el sentimiento global del artículo, el sentimiento del título y las oraciones de la nota con mayor puntación en cada una de las 3 clases posibles para el sentimiento (POS, NEU, NEG).

```json
"sentiment": {
    "global_sentiment": [
        "NEU",
        0.6979541778564453
    ],
    "highest_scoring_sentence_per_label": {
        "POS": {
            "score": 0.9584013223648071,
            "start_char": 780,
            "end_char": 825,
            "sentence": " Estoy muy contento con el grupo que nos tocó"
        },
        "NEG": {
            "score": 0.9649368524551392,
            "start_char": 2524,
            "end_char": 2580,
            "sentence": " La realidad es que el fútbol argentino es muy irregular"
        },
        "NEU": {
            "score": 0.8391280770301819,
            "start_char": 1200,
            "end_char": 1240,
            "sentence": " Después veremos cuando llegue el tiempo"
        }
    },
    "title_sentiment": {
        "label": "POS",
        "scores": {
            "NEG": 0.008031394332647324,
            "NEU": 0.09081562608480453,
            "POS": 0.901153028011322
        }
    }
},
```

## Fuentes

Estructura de la detección de fuentes del artículo. Actualmente citas directas detectadas.

```json
"sources": [
	    {
	        "text": "“No hay una prioridad de un torneo sobre otro. Solamente pensamos en Vélez. El torneo local no lo podemos descuidar. Cuando llegue el momento de los Libertadores lo veremos de la mejor manera”, sostuvo Rodríguez",
	        "start_char": 260,
	        "end_char": 471,
	        "length": 211,
	        "pattern": "Q.VP",
	        "explicit": true,
	        "components": {
	            "afirmacion": {
	                "text": "“No hay una prioridad de un torneo sobre otro. Solamente pensamos en Vélez. El torneo local no lo podemos descuidar. Cuando llegue el momento de los Libertadores lo veremos de la mejor manera”",
	                "start_char": 260,
	                "end_char": 452,
	                "label": "Afirmacion"
	            },
	            "conector": {
	                "text": "sostuvo",
	                "start_char": 454,
	                "end_char": 461,
	                "label": "Conector"
	            },
	            "referenciado": {
	                "text": "Rodríguez",
	                "start_char": 462,
	                "end_char": 471,
	                "label": "Referenciado"
	            }
	        }
	    },
	    ...
	]
```

## Métricas

Conjunto de métricas generadas a partir de las detecciones del modelo. Se categorizan en los subgrupos:

- general
- entities
- sentiment
- adjectives
- sources

```json
"metrics": {
        "general": {
            "num_chars": {
                "name": "num_chars",
                "value": 3968,
                "reference": 1000,
                "full_name": "Cantidad de caracteres del cuerpo"
            },
            "num_chars_title": {
                "name": "num_chars_title",
                "value": 89,
                "reference": 30,
                "full_name": "Cantidad de caracteres del título"
            },
            "num_words": {
                "name": "num_words",
                "value": 812,
                "reference": 500,
                "full_name": "Cantidad de palabras"
            },
            "num_sentences": {
                "name": "num_sentences",
                "value": 51,
                "reference": 30,
                "full_name": "Cantidad de oraciones"
            }
        },
        "entities": {
            "num_entidades": {
                "name": "num_entidades",
                "value": 25,
                "reference": 12,
                "full_name": "Cantidad de entidades en el texto"
            },
            "num_entidades_persona": {
                "name": "num_entidades_persona",
                "value": 10,
                "reference": 3,
                "full_name": "Cantidad de entidades Persona en el texto"
            },
            "num_entidades_organizacion": {
                "name": "num_entidades_organizacion",
                "value": 3,
                "reference": 3,
                "full_name": "Cantidad de entidades Organización en el texto"
            },
            "num_entidades_lugar": {
                "name": "num_entidades_lugar",
                "value": 3,
                "reference": 3,
                "full_name": "Cantidad de entidades Lugar en el texto"
            },
            "num_entidades_misc": {
                "name": "num_entidades_misc",
                "value": 9,
                "reference": 3,
                "full_name": "Cantidad de entidades Misceláneo en el texto"
            }
        },
        "sentiment": {
            "sentimiento_global_negativo": {
                "name": "sentimiento_global_negativo",
                "value": 0.03656395897269249,
                "reference": 0.33,
                "full_name": "Sentimiento global positivo"
            },
            "sentimiento_global_neutro": {
                "name": "sentimiento_global_neutro",
                "value": 0.6979541778564453,
                "reference": 0.33,
                "full_name": "Sentimiento global positivo"
            },
            "sentimiento_global_positivo": {
                "name": "sentimiento_global_positivo",
                "value": 0.2654818594455719,
                "reference": 0.33,
                "full_name": "Sentimiento global positivo"
            }
        },
        "adjectives": {
            "perc_adjectives": {
                "name": "perc_adjectives",
                "value": 0.24630541871921183,
                "reference": 7.000000000000001,
                "full_name": "Porcentaje de adjetivos en el texto"
            },
            "num_adjectives": {
                "name": "num_adjectives",
                "value": 40,
                "reference": 20,
                "full_name": "Cantidad de adjetivos en el texto"
            }
        },
        "sources": {
            "num_afirmaciones": {
                "name": "num_afirmaciones",
                "value": 1,
                "reference": 2,
                "full_name": "Cantidad de citas identificadas"
            },
            "num_afirmaciones_explicitas": {
                "name": "num_afirmaciones_explicitas",
                "value": 1,
                "reference": 2,
                "full_name": "Cantidad de citas explícitas"
            },
            "num_referenciados": {
                "name": "num_referenciados",
                "value": 1,
                "reference": 2,
                "full_name": "Cantidad de Referenciados"
            },
            "num_referenciados_unique": {
                "name": "num_referenciados_unique",
                "value": 1,
                "reference": 2,
                "full_name": "Cantidad de Referenciados Únicos"
            },
            "num_conectores": {
                "name": "num_conectores",
                "value": 1,
                "reference": 2,
                "full_name": "Cantidad de Conectores"
            },
            "num_conectores_unique": {
                "name": "num_conectores_unique",
                "value": 1,
                "reference": 2,
                "full_name": "Cantidad de Conectores Únicos"
            }
        }
```

# Futuras Implementaciones / Ideas

## Google Fact Checker

Es importante aprovechar las herramientas ya disponibles en el ámbito de la confirmación o medidas de confiabilidad de noticias. Es por eso que resulta interesante investigar e incorporar las capacidades de la herramienta Google Fact Checker en las funciones de Trust.

https://toolbox.google.com/factcheck/explorer/search/list:recent;hl=es

## Integraciones / Análisis con LLMs

Actualmente Trust utiliza técnicas de aprendizaje supervizado (ML) mediante la aplicación de modelos previamente entrenados en tareas específicas (no generales como pueden ser los *Large Language Models* como *Gemini* o *ChatGPT*).

Una posibilidad como línea de investigación para el proyecto puede ser la integración de la herramienta con este tipo de sistemas. Esto podría potencialmente incorporar capacidades en la herramienta como:

- Resumen de la nota.
- Consultas usando lenguaje natural sobre el texto del artículo.
- Análisis alternativo de cualquiera de los componentes detectados actualmente.
- Análisis de tendencias o coherencia.

## Mayor análisis con Pysentimiento

Incorporar más tasks disponibles con pysentimiento:

- Hate Speech Detection
- Irony Detection
- Emotion Analysis
- Contextualized Hate Speech Detection

Incluso se podría probar su versión de NER y POS tagging y el Targeted Sentiment Analysis.

## Visualizaciones

Entrega desde el *backend* visualizaciones con referencias (a partir del corpus de noticias) para representar y comparar gráficamente un artículo en el conjunto (por ejemplo dentro de su sección).
