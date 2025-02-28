import json
#from dataclasses import dataclass
import pickle
import warnings

import pandas as pd
from spacy import displacy
from tqdm import tqdm

# @dataclass
# class NLPAnnotations():
#     doc: dict
#     entities: dict
#     entities_sentiment: dict
#     sentiment: dict
#     adjectives: dict
#     dates: dict

class NLPAnnotations():
    
    def __init__(self):
        self.doc = dict()
        self.entities = dict()
        self.entities_sentiment = dict()
        self.sentiment = dict()
        self.adjectives = dict()
        self.sources = dict()
        self.json = None
        self.metrics = dict(general=dict(), entities=dict(), sentiment=dict(), adjectives=dict(), sources=dict())
        
    def summary(self):
        print("NLP Annotations Summary:")
        print(f"Entities analyzed by: {[k for k, v in self.entities.items()]}")
        print(f"Entities Sentiment analyzed by: {[k for k, v in self.entities_sentiment.items()]}")
        print(f"General Sentiment analyzed by: {[k for k, v in self.sentiment.items()]}")
        print(f"Adjectives analyzed by: {[k for k, v in self.adjectives.items()]}")
        print(f"Sources analyzed by: {[k for k, v in self.sources.items()]}")
        print(f"Metrics: {[k for k, v in self.metrics.items()]}")
        
    def __repr__(self):
        self.summary()
        return ""
        
    def __str__(self):
        self.summary()
        return ""
    
    def to_dict(self):
        annotations_dict = self.__dict__.copy()
        annotations_dict.pop("doc")
        return annotations_dict
    
    def from_dict(self, nlp_annotations_dict):      
        for key in nlp_annotations_dict:
            if key not in ["entities", "entities_sentiment", "sentiment", "adjectives", "sources", "json", "metrics"]:
                raise KeyError(f"Key '{key}' not found in NLPAnnotations attributes.")
            setattr(self, key, nlp_annotations_dict[key])
        return self
    
        
class ManualAnnotations():
    
    def __init__(self):
        self.entities = dict()
        self.entities_sentiment = dict()
        self.sentiment = dict()
        self.adjectives = dict()
        self.sources = dict()
        
    def summary(self):
        print("Manual Annotations Summary:")
        print(f"Entities analyzed by: {[k for k, v in self.entities.items() if v is not None]}")
        print(f"Entities Sentiment analyzed by: {[k for k, v in self.entities_sentiment.items() if v is not None]}")
        print(f"General Sentiment analyzed by: {[k for k, v in self.sentiment.items() if v is not None]}")
        print(f"Adjectives analyzed by: {[k for k, v in self.adjectives.items() if v is not None]}")
        print(f"Sources analyzed by: {[k for k, v in self.sources.items() if v is not None]}")
        
    def __repr__(self):
        self.summary()
        return ""
        
    def __str__(self):
        self.summary()
        return ""
    
    def to_dict(self):
        annotations_dict = self.__dict__.copy()
        return annotations_dict
    
    def from_dict(self, manual_annotations_dict):
        for key in manual_annotations_dict:
            if key not in ["entities", "entities_sentiment", "sentiment", "adjectives", "sources"]:
                raise KeyError(f"Key '{key}' not found in ManualAnnotations attributes.")
            setattr(self, key, manual_annotations_dict[key])
        return self



class Article():
    
    def __init__(self, news_dict, **kwargs):
        
        for key in news_dict:
            if key == "nlp_annotations":
                self.nlp_annotations = NLPAnnotations().from_dict(news_dict[key])
            elif key == "manual_annotations":
                self.manual_annotations = ManualAnnotations().from_dict(news_dict[key])
            else:
                setattr(self, key, news_dict[key])      
                    
        for key in kwargs:
            setattr(self, key, kwargs[key])
        
        if not hasattr(self, "index"):
            self.index = None
            
        if not hasattr(self, "nlp_annotations"):
            self.nlp_annotations = NLPAnnotations()
        
        if not hasattr(self, "manual_annotations"):
            self.manual_annotations = ManualAnnotations()
            
    def __repr__(self):
        return f"Artículo: {self.titulo} - {self.medio} - {self.fecha}"

    def __str__(self) -> str:
        return f"Artículo: {self.titulo} - {self.medio} - {self.fecha}"
    
    def get_article_dict(self) -> dict:
        """Ya no aplica."""
        return self.__dict__.copy()
    
    def get_article_attrs(self) -> list:
        return list(self.__dict__.keys())
    
    def to_dict(self, include_annotations: bool = True):
        article_dict = self.__dict__.copy()
        if include_annotations:
            article_dict["nlp_annotations"] = self.nlp_annotations.to_dict()
            article_dict["manual_annotations"] = self.manual_annotations.to_dict()
        else:
            article_dict.pop("nlp_annotations")
            article_dict.pop("manual_annotations")
        
        return article_dict
    
    # def from_dict(self, article_dict):
    #     for key in article_dict:
            
    #         if key == "nlp_annotations":
    #             self.nlp_annotations.from_dict(article_dict[key])
                
    #         elif key == "manual_annotations":
    #             self.manual_annotations = ManualAnnotations().from_dict(article_dict[key])
                
    #         else:
    #             setattr(self, key, article_dict[key])
        
    #     return self
    
    def load_manual_annotations(self, manual_annotations, author, annotated_attribute):
        getattr(self.manual_annotations, annotated_attribute)[author] = manual_annotations
        
    def add_metric(self, category: str, key: str, value: float, reference: str = None, full_name: str = None):
        
        if category not in self.nlp_annotations.metrics.keys():
            raise ValueError(f"Category {category} not found in nlp_annotations.metrics")
        
        if full_name is None:
            full_name = key.replace("_", " ").capitalize()
        
        self.nlp_annotations.metrics[category][key] = {"name":key,
                                                       "value":value,
                                                       "reference":reference,
                                                       "full_name":full_name}
    
    def check_nlp_annotations(self):
        # Esta función debería revisar la instancia de nlp_annotations y devolver un print con el listado de anotaciones realizadas.
        pass
    
    # def _check_doc_attr(self):
    #     return hasattr(self, 'entities')
    
    # def _check_entities_attr(self):
    #     return hasattr(self, 'entities')
    
    # def analyze_cuerpo(self, nlp_processor):
    #     self.doc_cuerpo = nlp_processor.analyze(self.cuerpo)
    #     self.entities_cuerpo = nlp_processor.extract_entities_v2(self.doc_cuerpo)
    #     # self.entities_cuerpo = dict(entities_list = nlp_processor.extract_entities(self.doc_cuerpo),
    #     #                             entities_count = nlp_processor.count_entities(self.doc_cuerpo),
    #     #                             entity_type_counts = nlp_processor.count_entity_types(self.doc_cuerpo))
    
    def plot_entities_cuerpo(self, entities, **kwargs):
        
        # Revisar que exista el atributo entities_cuerpo
        # if not hasattr(self, 'entities_cuerpo'):
        #     raise ValueError("Analizar el cuerpo del artículo antes de graficar entidades")
        
        options = {'colors':{"Persona":"#fcba03", "Lugar":"#22B8C3", "Misceláneo":"#E421D3", "Organización":"#22BF51"}}
        
        plot_data = { 
                     "text":self.cuerpo,
                     "ents": [{'start':e['start_char'], 'end':e['end_char'], 'label':e['type']} for e in entities],
                     "title": None
                     }

        displacy.render(plot_data, style="ent", manual=True, page=True, options=options, **kwargs)
        
    def plot_sources_cuerpo(self, sources, **kwargs):
        
        # Revisar que exista el atributo entities_cuerpo
        # if not hasattr(self, 'entities_cuerpo'):
        #     raise ValueError("Analizar el cuerpo del artículo antes de graficar entidades")
        
        options = {'colors':{"Afirmacion":"#ffd642", "Conector":"#f55d32", "Referenciado":"#59d8f7", "Afirmacion Debil":"#ef9eff"}}
        
        sources = [region for region in sources if 'from_id' not in region.keys()]
        
        plot_data = { 
                     "text":self.cuerpo,
                     "ents": [{'start':e['start_char'], 'end':e['end_char'], 'label':e['type']} for e in sources],
                     "title": None
                     }

        displacy.render(plot_data, style="ent", manual=True, page=True, options=options, **kwargs)
    
        
    # def get_all_indicators(self):
    #     raise NotImplementedError("Librería no implementada")
    
    
    
class ArticlesCorpus():
    
    def __init__(self):
        self.articles = {}
        self.n_articles = 0
        
    def __repr__(self):
        return f"Corpus de Artículos: {self.n_articles} artículos"

    def __str__(self) -> str:
        return f"Corpus de Artículos: {self.n_articles} artículos"
        
    def __add__(self, corpus):
        """OJO -> Que pasa al sumar articulos con el mismo index?"""
        
        articles_list = [article.get_article_dict() for article in self.articles.values()]
        new_articles_list = [article.get_article_dict() for article in corpus.articles.values()]
        articles_list = articles_list + new_articles_list
   
        new_corpus = ArticlesCorpus()
        new_corpus.load_articles(articles_list)
        
        return new_corpus
    
    def _load_articles_from_list(self, list_of_news):
        for news in list_of_news:
            article = Article(news)
            #if hasattr(article, "index"):
            if article.index is not None:
                self.articles[article.index] = article
            else:
                self.articles[self.n_articles] = article
            self.n_articles += 1
            
    def _load_articles_from_dict(self, dict_of_news):  
        """Esta función permite cargar un corpus filtrado y generar un nuevo corpus"""
        """Esta función espera un diccionario con la estructura {index: Article}"""                  
        for article in dict_of_news.values():
            if article.index is not None:
                self.articles[article.index] = article
            else:
                self.articles[self.n_articles] = article
            self.n_articles += 1
        
    def load_articles(self, news):
        
        if isinstance(news, list):
            self._load_articles_from_list(news)
            
        elif isinstance(news, dict):
            self._load_articles_from_dict(news)
            
        else:
            raise ValueError("mode must be 'list' (list of dictionaries) or 'dict' (dictionary of Articles == corpus)")
            
        self._get_articles_catalog()
            
    def export_articles(self, filename: str, include_annotations: bool = True):
        'Save article list of dicts in json format to load in label studio.'
        warnings.warn("To export corpus to json use to_json method.")
        
        articles_dict = []

        for art in self.get_articles():
            art_keys_dict = {k:v for k,v in art.get_article_dict().items() if k not in ['nlp_annotations', 'manual_annotations']}
  
            if include_annotations:
                
                if 'nlp_annotations' in art.get_article_dict():
                    nlp_annotations = art.get_article_dict()['nlp_annotations']
                    art_keys_dict['nlp_annotations'] = {}
                    art_keys_dict['nlp_annotations']['entities'] = nlp_annotations.entities
                    art_keys_dict['nlp_annotations']['entities_sentiment'] = nlp_annotations.entities_sentiment
                    art_keys_dict['nlp_annotations']['sentiment'] = nlp_annotations.sentiment
                    art_keys_dict['nlp_annotations']['adjectives'] = nlp_annotations.adjectives
                    art_keys_dict['nlp_annotations']['sources'] = nlp_annotations.sources
                    art_keys_dict['nlp_annotations']['metrics'] = nlp_annotations.metrics

                if 'manual_annotations' in art.get_article_dict():
                    manual_annotations = art.get_article_dict()['manual_annotations']
                    art_keys_dict['manual_annotations'] = {}
                    art_keys_dict['manual_annotations']['entities'] = manual_annotations.entities
                    art_keys_dict['manual_annotations']['entities_sentiment'] = manual_annotations.entities_sentiment
                    art_keys_dict['manual_annotations']['sentiment'] = manual_annotations.sentiment
                    art_keys_dict['manual_annotations']['adjectives'] = manual_annotations.adjectives
                    art_keys_dict['manual_annotations']['sources'] = manual_annotations.sources
                    #art_keys_dict['manual_annotations']['dates'] = manual_annotations.dates               

            articles_dict.append(art_keys_dict) 

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(articles_dict, f, ensure_ascii=False, indent=4)
        
        
    # def save_articles(self, filename):
    #     'Save article list of dicts in pickle format.'
                
    #     news_dict = [article.get_article_dict() for article in self.articles.values()]

    #     with open(filename, 'wb') as handle:
    #         pickle.dump(news_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)
            
    def save_corpus(self, filename):
        'Save corpus object in pickle format.'
        warnings.warn('Deprecated, use to_pickle instead.')

        with open(filename, 'wb') as handle:
            pickle.dump(self, handle, protocol=pickle.HIGHEST_PROTOCOL)
            
    def load_corpus(self, filename):
        warnings.warn('Deprecated, use from_pickle instead.')
        # open pickle file
        with open(filename, 'rb') as f:
            corpus = pickle.load(f)
        
        return corpus
    
    def to_dict(self, include_annotations: bool = True):
        corpus_dict = {index: article.to_dict(include_annotations) for index, article in self.articles.items()}
        return corpus_dict

    def to_json(self, filename: str, include_annotations: bool = True):
        corpus_dict = self.to_dict(include_annotations)
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(corpus_dict, f, ensure_ascii=False, indent=4)

    def to_pickle(self, filename: str):
        with open(filename, 'wb') as handle:
            pickle.dump(self, handle, protocol=pickle.HIGHEST_PROTOCOL)
    
    def from_dict(self, corpus_dict: dict):
        # self.articles = {int(index): Article(article) for index, article in corpus_dict.items()}
        # self.n_articles = len(self.articles)
        # self._get_articles_catalog()
        # self._add_metrics_to_catalog()
        
        # return self
        
        corpus = ArticlesCorpus()
        corpus.articles = {int(index): Article(article) for index, article in corpus_dict.items()}
        corpus.n_articles = len(corpus.articles)
        corpus._get_articles_catalog()
        corpus._add_metrics_to_catalog()
        
        return corpus
        
    def from_json(self, filename: str):
        with open(filename, 'r', encoding="utf8") as f:
            corpus_dict = json.load(f)
        corpus = self.from_dict(corpus_dict)
        return corpus

    def from_pickle(self, filename: str):
        # open pickle file
        with open(filename, 'rb') as f:
            corpus = pickle.load(f)
        
        return corpus

            
    def load_manual_annotations(self, manual_annotations, author, annotated_attribute):
        # Faltan chequeos
        # Que exista el index en el corpus
        # Que coincidan los títulos de la noticia anotada con el titulo del articulo al que se le agrega.
        # Que pasa cuando no están todas las noticias anotadas o que faltan indices.
        # ...
                
        for index, annotations in manual_annotations.items():
            self.get_article(index).load_manual_annotations(annotations['annotations'], author, annotated_attribute)
                  
        
            
        
    def _get_articles_catalog(self):
        news_list = [self.articles[index].get_article_dict() for index in self.articles.keys()]
        index_list = [index for index in self.articles.keys()]
        
        # Sets index for each article in attribute.
        # Si ya tenían index se sobreescribe por el mismo, por lo que no hay cambios.
        for index in index_list:
            self.articles[index].index = index
        
        df = (pd.DataFrame(news_list)
              # Agregamos variables relevantes y damos formatos correctos.
              .assign(index_article = index_list,
                      fecha = lambda x: pd.to_datetime(x.fecha, format='%d/%m/%Y'),
                      # limpiamos los nombres de autores de las categorias.
              #        categorias = lambda x: x.apply(lambda y: [i for i in y.categorias if i not in y.autor], axis=1))
              #.assign(categorias = lambda x: x.categorias.apply(lambda y: '_'.join(y)),
              #        etiquetas = lambda x: x.etiquetas.apply(lambda y: '_'.join(y)))
              )
              .drop(columns=["nlp_annotations", "manual_annotations"])
              #[["index", "medio", "fecha", "categorias", "autor", "etiquetas", "titulo", "link_noticia"]]
              )
         
        self.catalog = df
        
    def _add_metrics_to_catalog(self):
        
        metrics_df = {}
        
        for article in self.get_articles():

            metrics_df[article.index] = {} 
            metrics = [d for x in article.nlp_annotations.metrics.values() for d in x.values()]

            for metric in metrics:
                metrics_df[article.index][metric['name']] = metric['value']
                
        
        metrics_df = pd.DataFrame.from_dict(metrics_df, orient="index")
        repeated_cols = [c for c in self.get_catalog().columns if c in metrics_df.columns]
        self.catalog = self.get_catalog().merge(metrics_df.drop(columns=repeated_cols), left_on="index_article", right_index=True, how="left")
        
    def reset_index(self):
        self.articles = {i:article for i, article in enumerate(self.get_articles())}
        for k in self.articles:
            self.articles[k].index = k
        
    def get_corpus(self):
        return self.articles.copy()
    
    def get_catalog(self):
        return self.catalog.copy()
    
    def get_article(self, index):
        return self.articles[index]
    
    def get_articles(self):
        return [article for article in self.articles.values()]
    
    def filter_by_index(self, index_list, to_corpus=False):
        filtered_news_dict = {index: self.articles[index] for index in index_list}
        
        # Con este argumento devuelve directamente un corpus.
        if to_corpus:
            corpus = ArticlesCorpus()
            corpus.load_articles(filtered_news_dict)
            return corpus
        
        else:
            return filtered_news_dict
    
    def filter_by_catalog(self, filtered_catalog, to_corpus=False):
        index_list = filtered_catalog.index_article.tolist()
        filtered = self.filter_by_index(index_list, to_corpus)   
        return filtered
    
    
    
    def summary(self):
        pass


    # def load_nlp_processor(self, nlp_processor):
    #     self.nlp_processor = nlp_processor
    #     print("NLP Processor loaded!")
        
    # def analyze_corpus_cuerpo(self):
    #     if not hasattr(self, 'nlp_processor'):
    #         raise ValueError("nlp_processor not loaded")
        
    #     for article in tqdm(self.articles.values()):
    #         article.analyze_cuerpo(self.nlp_processor)
            
    #     print("Corpus analyzed!")
    #     self._corpus_cuerpo_analized = True
            
            
    # def _update_catalog(self):
        
    #     pass
        