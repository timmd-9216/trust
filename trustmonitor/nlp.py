# nlp_base.py
import re
import spacy
import stanza
from tqdm import tqdm
from pysentimiento import create_analyzer  # Import pysentimiento
from .matcher import SourceMatcher
import json
import pandas as pd

MIN_SENT_LENGHT = 10

class NLP:
    ### GENERALES ###
    def __init__(self, language, libreria):
        self.language = language
        self.libreria = libreria

        if self.libreria not in ('spacy', 'stanza','pysentimiento'):
            raise NotImplementedError("Librería no implementada")
        if self.libreria == 'spacy':
            self._init_spacy()
        elif self.libreria == 'stanza':
            self._init_stanza()
        elif self.libreria == 'pysentimiento':
            self._init_pysentimiento()

    def analyze(self, text):
        if self.libreria == 'spacy':
            return self._analyze_spacy(text)
        elif self.libreria == 'stanza':
            return self._analyze_stanza(text)

    def extract_entities(self, doc):
        if self.libreria == 'spacy':
            return self._extract_entities_spacy(doc)
        elif self.libreria == 'stanza':
            return self._extract_entities_stanza(doc)

    def extract_entities_v2(self, doc):
        if self.libreria == 'spacy':
            return self._extract_entities_v2_spacy(doc)
        elif self.libreria == 'stanza':
            return self._extract_entities_v2_stanza(doc)

    def extract_tokens(self, doc):
        if self.libreria == 'spacy':
            return self._extract_tokens_spacy(doc)
        elif self.libreria == 'stanza':
            return self._extract_tokens_stanza(doc)

    def extract_adjectives(self, doc):
        if self.libreria == 'spacy':
            return self._extract_adjectives_spacy(doc)
        elif self.libreria == 'stanza':
            return self._extract_adjectives_stanza(doc)

    def count_entity_types(self, doc):
        if self.libreria == 'spacy':
            return self._count_entity_types_spacy(doc)
        elif self.libreria == 'stanza':
            return self._count_entity_types_stanza(doc)

    def count_adjective_types(self, doc, feature_type='Degree'):
        """
        Posibles feature_type:
            - Degree
            - Gender
            - Number
            - NumType
        """
        adjective_classification = {'uncategorized': 0}
        adjectives = self.extract_adjectives(doc)
        for adjective in adjectives:
            if feature_type not in adjective['features']:
                adjective_classification['uncategorized'] += 1
                continue
            adj_category = adjective['features'][feature_type]
            if adj_category not in adjective_classification:
                adjective_classification[adj_category] = 0
            adjective_classification[adj_category] += 1
        return adjective_classification

    def extract_entity_sentiments(self, doc):
        if self.libreria == 'spacy':
            return self._extract_entity_sentiments_spacy(doc)
        elif self.libreria == 'stanza':
            return self._extract_entity_sentiments_stanza(doc)

    def extract_places(self, doc):
        entities = self.extract_entities_v2(doc)
        return [entity for entity in entities if entity['type'] == 'Lugar']

    def extract_date(self, doc):
        raise NotImplementedError("extract_date not implemented")

    def extract_sources(self, doc):
        if self.libreria == 'stanza':
            return self._extract_explicit_sources_stanza(doc)
        else:
            return None

    def extract_links(self, doc):
        # Usamos re para encontrar links en el texto (aunque no tengan http, pueden comenzar con www.)
        # Tiene que ignorar caracteres especiales al final de la url
        regex_results = re.findall(r'(https?://\S+|www\.\S+)', doc.text)
        links = []
        for link in regex_results:
            link = link.rstrip('.,;!?()')
            links.append(link)
        return links

    def count_adjectives(self, doc):
        return len(self.extract_adjectives(doc))

    def count_entities(self, doc):
        return len(self.extract_entities(doc))

    def _translate_entity_type(self, entity_type):
        entities_translation = {
            'stanza':
                {
                    'PER': 'Persona',
                    'ORG': 'Organización',
                    'LOC': 'Lugar',
                    'MISC': 'Misceláneo'
                },
            'spacy':
                {
                    'PER': 'Persona',
                    'ORG': 'Organización',
                    'LOC': 'Lugar',
                    'MISC': 'Misceláneo'
                }
            }
        if entity_type not in entities_translation[self.libreria]:
            print(f'Entity type no reconocido: {entity_type}')
            return 'Otro'
        return entities_translation[self.libreria][entity_type]

    ### SPACY ###
    def _init_spacy(self):
        self.nlp = spacy.load(f'{self.language}_core_news_sm')
        self.libreria = 'spacy'

    def _analyze_spacy(self, text):
        return self.nlp(text)

    def _extract_entities_spacy(self, doc):
        entities = []
        for entity in doc.ents:
            entities.append(entity.text)
        return entities

    def _extract_entities_v2_spacy(self, doc):
        entities_v2 = []
        for entity in doc.ents:
            entities_v2.append({
                'text': entity.text,
                'type': self._translate_entity_type(entity.label_),
                'sentiment': None, # No implementado en spacy
                'start_char': entity.start_char,
                'end_char': entity.end_char
            })
        return entities_v2

    def _extract_tokens_spacy(self, doc):
        tokens = []
        for token in doc:
            tokens.append({'text': token.text, 'ner': token.ent_type_, 'start_char': token.idx, 'end_char': token.idx + len(token.text)})
        return tokens

    def _extract_adjectives_spacy(self, doc):
        adjectives = []
        for token in doc:
            if token.pos_ == 'ADJ':
                adejctive_text = token.text
                adjective_features = {}
                if token.morph.to_dict() is not None:
                    adjective_features = token.morph.to_dict()
                adjectives.append({
                    'text': adejctive_text,
                    'features': adjective_features
                })
        return adjectives

    def _count_entity_types_spacy(self, doc):
        entity_classification = {}
        for entity in doc.ents:
            entity_type = self._translate_entity_type(entity.label_)
            if entity_type not in entity_classification:
                entity_classification[entity_type] = 1
            else:
                entity_classification[entity_type] += 1
        return entity_classification

    def _extract_entity_sentiments_spacy(self, doc):
        raise Exception("No implementado para spacy - por ahora")
        entity_sentiments = {}
        for entity in doc.ents:
            if entity.text not in entity_sentiments:
                entity_sentiments[entity.text] = [entity.sentiment]
            else:
                entity_sentiments[entity.text].append(entity.sentiment)
        return entity_sentiments

    ### STANZA ###
    def _init_stanza(self):
        self.nlp = stanza.Pipeline(self.language, processors='tokenize,ner,sentiment,pos,lemma,depparse,constituency')
        self.libreria = 'stanza'

    def _analyze_stanza(self, text):
        return self.nlp(text)

    def _extract_entities_stanza(self, doc):
        entities = []
        for sentence in doc.sentences:
            for entity in sentence.ents:
                entities.append(entity.text)
        return entities

    def _extract_entities_v2_stanza(self, doc):
        entities_v2 = []
        for sentence in doc.sentences:
            for entity in sentence.ents:
                entities_v2.append({
                    'text': entity.text,
                    'type': self._translate_entity_type(entity.type),
                    'sentiment': sentence.sentiment,
                    'start_char': entity.start_char,
                    'end_char': entity.end_char
                })
        return entities_v2

    def _extract_tokens_stanza(self, doc):
        tokens = []
        for sentence in doc.sentences:
            for token in sentence.tokens:
                tokens.append({'text': token.text, 'ner': token.ner, 'start_char': token.start_char, 'end_char': token.end_char})
        return tokens

    def _extract_adjectives_stanza(self, doc):
        adjectives = []
        for sentence in doc.sentences:
            for word in sentence.words:
                if word.upos == 'ADJ':
                    adejctive_text = word.text
                    adjective_features = {}
                    if word.feats is not None:
                        feats = word.feats.split("|")
                        for feat in feats:
                            key, value = feat.split("=")
                            adjective_features[key] = value
                    adjectives.append({
                        'text': adejctive_text,
                        'features': adjective_features,
                        'start_char': word.start_char,
                        'end_char': word.end_char
                    })
        return adjectives

    def _count_entity_types_stanza(self, doc):
        entity_classification = {}
        for sentence in doc.sentences:
            for entity in sentence.ents:
                entity_type = self._translate_entity_type(entity.type)
                if entity_type not in entity_classification:
                    entity_classification[entity_type] = 1
                else:
                    entity_classification[entity_type] += 1
        return entity_classification

    def _extract_entity_sentiments_stanza(self, doc):
        entity_sentiments = {}
        for sentence in doc.sentences:
            for entity in sentence.ents:
                if entity.text not in entity_sentiments:
                    entity_sentiments[entity.text] = [sentence.sentiment]
                else:
                    entity_sentiments[entity.text].append(sentence.sentiment)
        return entity_sentiments
    
    def _extract_explicit_sources_stanza(self, doc):
        
        matcher = SourceMatcher(debug=False)
        sources_list = matcher.get_explicit_sources(doc)
        
        return sources_list
        

    ## pysentimiento
    def _init_pysentimiento(self):
        self.pysentimiento = create_analyzer(task="sentiment", lang="es")

    def _extract_corpus_sentiment(self, corpus):
        # article.nlp_annotations.sentiment incluye ahora analisis por oracion
        for article in tqdm(corpus.articles.values()):
            analysis_result = self.pysentimiento.predict(article.cuerpo)
            article.nlp_annotations.sentiment = {}
            article.nlp_annotations.sentiment['pysentimiento'] = {
                'label': analysis_result.output,
                'scores': analysis_result.probas,
                'sentences': []
            }

            sentences = article.cuerpo.split('.')
            for sentence in sentences:
                analysis_result = self.pysentimiento.predict(sentence)
                article.nlp_annotations.sentiment['pysentimiento']['sentences'].append({
                    'sentence': sentence,
                    'label': analysis_result.output,
                    'scores': analysis_result.probas,
                    'start_char': article.cuerpo.find(sentence),
                    'end_char': article.cuerpo.find(sentence) + len(sentence)
                })

            title_analysis_result = self.pysentimiento.predict(article.titulo)
            article.nlp_annotations.sentiment['pysentimiento']['titulo'] = {
                'label': title_analysis_result.output,
                'scores': title_analysis_result.probas

            }

    #stanza and spacy for both
    def analyze_corpus_cuerpo(self, corpus):
        """
        Analyze all articles within a given corpus, populating their NLPAnnotations.
        
        Parameters:
        - corpus: An instance of ArticlesCorpus, containing articles to be analyzed.
        """
        # Ensure the NLP library is initialized for sentiment analysis, if not already

        for article in tqdm(corpus.articles.values(), desc="Analyzing corpus"):
            # Analyze article content
            doc = self.analyze(article.cuerpo)
            entities = self.extract_entities_v2(doc)
            tokens = self.extract_tokens(doc)
            adjectives = self.extract_adjectives(doc)
            sources = self.extract_sources(doc)
            
            if self.libreria != 'spacy':
                entities_sentiment = self.extract_entity_sentiments(doc)
            else:
                entities_sentiment = []

            # Populate NLPAnnotations for the article
            article.nlp_annotations.doc[self.libreria] = doc
            article.nlp_annotations.entities[self.libreria] = entities
            article.nlp_annotations.entities_sentiment[self.libreria] = entities_sentiment
            article.nlp_annotations.adjectives[self.libreria] = adjectives
            article.nlp_annotations.sources[self.libreria] = sources
            

    #stanza and spacy for both

    def calculate_corpus_metrics(self, corpus):
        """
        Possible metrics categories: general, entities, adjectives, sentiment, sources
        """
        
        for article in tqdm(corpus.get_articles(), desc="Calculating corpus metrics"):
            
            article.add_metric(category='general', key='num_chars', value=len(article.cuerpo), reference=1000, full_name='Cantidad de caracteres del cuerpo')
            article.add_metric(category='general', key='num_chars_title', value=len(article.titulo), reference=30, full_name='Cantidad de caracteres del título')
            
            if 'stanza' in article.nlp_annotations.doc:
                article.add_metric(category='general', key='num_words', value=article.nlp_annotations.doc["stanza"].num_words, reference=500, full_name='Cantidad de palabras')
                article.add_metric(category='general', key='num_sentences', value=len(article.nlp_annotations.doc["stanza"].sentences), reference=30, full_name='Cantidad de oraciones')            
                adjectives_rate = len(article.nlp_annotations.adjectives) /article.nlp_annotations.doc["stanza"].num_words
                article.add_metric(category='adjectives',key='perc_adjectives', value= adjectives_rate*100,reference=0.07*100, full_name='Porcentaje de adjetivos en el texto')

            if 'pysentimiento' in article.nlp_annotations.sentiment:
                article.add_metric(category='sentiment',key='sentimiento_global_negativo', value= article.nlp_annotations.sentiment['pysentimiento']['scores']['NEG'],reference=0.33, full_name='Sentimiento global positivo')    
                article.add_metric(category='sentiment',key='sentimiento_global_neutro', value= article.nlp_annotations.sentiment['pysentimiento']['scores']['NEU'],reference=0.33, full_name='Sentimiento global positivo')    
                article.add_metric(category='sentiment',key='sentimiento_global_positivo', value= article.nlp_annotations.sentiment['pysentimiento']['scores']['POS'],reference=0.33, full_name='Sentimiento global positivo')    
                
            # todo add max and min sentimiento
            # todo add more metrics. 
            
            if 'stanza' in article.nlp_annotations.entities:
                article.add_metric(category='entities', key='num_entidades', value=len(article.nlp_annotations.entities['stanza']), reference=12, full_name='Cantidad de entidades en el texto')
                article.add_metric(category='entities', key='num_entidades_persona', value=len([e for e in article.nlp_annotations.entities["stanza"] if e["type"] == "Persona"]), reference=3, full_name='Cantidad de entidades Persona en el texto')
                article.add_metric(category='entities', key='num_entidades_organizacion', value=len([e for e in article.nlp_annotations.entities["stanza"] if e["type"] == "Organización"]), reference=3, full_name='Cantidad de entidades Organización en el texto')
                article.add_metric(category='entities', key='num_entidades_lugar', value=len([e for e in article.nlp_annotations.entities["stanza"] if e["type"] == "Lugar"]), reference=3, full_name='Cantidad de entidades Lugar en el texto')
                article.add_metric(category='entities', key='num_entidades_misc', value=len([e for e in article.nlp_annotations.entities["stanza"] if e["type"] == "Misceláneo"]), reference=3, full_name='Cantidad de entidades Misceláneo en el texto')

            if 'stanza' in article.nlp_annotations.adjectives:
                article.add_metric(category='adjectives', key='num_adjectives', value=len(article.nlp_annotations.adjectives['stanza']), reference=20, full_name='Cantidad de adjetivos en el texto')

            if 'stanza' in article.nlp_annotations.sources:
                article.add_metric(category='sources',key='num_afirmaciones', value= len(article.nlp_annotations.sources['stanza']), reference=2, full_name='Cantidad de citas identificadas')    
                article.add_metric(category='sources',key='num_afirmaciones_explicitas', value= len([s for s in article.nlp_annotations.sources["stanza"] if s["explicit"]]), reference=2, full_name='Cantidad de citas explícitas')
                article.add_metric(category='sources',key='num_referenciados', value= len([s for s in article.nlp_annotations.sources["stanza"] if 'referenciado' in s["components"]]), reference=2, full_name='Cantidad de Referenciados')    
                num_referenciados_unique = len(set([s["components"]["referenciado"]["text"] for s in article.nlp_annotations.sources["stanza"] if 'referenciado' in s["components"]]))
                article.add_metric(category='sources', key='num_referenciados_unique', value=num_referenciados_unique, reference=2, full_name='Cantidad de Referenciados Únicos')    
                article.add_metric(category='sources',key='num_conectores', value=len([s for s in article.nlp_annotations.sources["stanza"] if 'conector' in s["components"]]), reference=2, full_name='Cantidad de Conectores')
                num_conectores_unique = len(set([s["components"]["conector"]["text"] for s in article.nlp_annotations.sources["stanza"] if 'conector' in s["components"]]))
                article.add_metric(category='sources',key='num_conectores_unique', value=num_conectores_unique, reference=2, full_name='Cantidad de Conectores Únicos')    
              
            # metrics_df[article.index] = {}  
            # metrics = [d for x in article.nlp_annotations.metrics.values() for d in x.values()]
            
            # for metric in metrics:
            #     metrics_df[article.index][metric['name']] = metric['value']
        corpus._add_metrics_to_catalog()

    def _build_frontend_json(self, corpus):
        """
        Estructura del json:
        corpus.get_article(0).nlp_annotations.json = {
            "entities": {
                "entities_list": [
                        {"text": "Argentina", "type": "LOC", "start_char": 0, "end_char": 8},
                        {"text": "Javier Milei", "type": "PER", "start_char": 45, "end_char": 56},
                    ],
                "entities_freq": []
            },
            "adjectives": {
                "adjectives_list": [],
                "adjectives_freq": []
            },
            "sentiment": {
                "global_sentiment": ["TAG", 0.0],
                "highest_scoring_sentence_per_label": {
                    "POS": {
                        "score": 0.0,
                        "start_char": 0,
                        "end_char": 0
                    },
                    "NEG": {
                        "score": 0.0,
                        "start_char": 0,
                        "end_char": 0
                    },
                    "NEU": {
                        "score": 0.0,
                        "start_char": 0,
                        "end_char": 0
                    }
                }
            },
            "sources": {
                "n_sources": 0,
                "n_explicit_sources": 0,
                "sources_list": [
                    {
                        "text": "", 
                        "start_char": 0, 
                        "end_char": 0, 
                        "explicit": False, 
                        "components":{
                            "afirmacion": {
                                "text": "",
                                "start_char": 0,
                                "end_char": 0,
                            },
                            "conector": {
                                "text": "",
                                "start_char": 0,
                                "end_char": 0,
                            },
                            "referenciado":{
                                "text": "",
                                "start_char": 0,
                                "end_char": 0,
                            },
                        }
                    },
                ]
            }
        }        
        """
        for article in tqdm(corpus.articles.values(), desc="Building frontend json"):
            article.nlp_annotations.json = {}

            article.nlp_annotations.json['id'] = article.get_article_dict()['id']

            # Entities
            entities = article.nlp_annotations.entities['stanza']
            entities_freq = {}
            for entity in entities:
                key_entity = (entity['text'], entity['type'])
                if key_entity not in entities_freq:
                    entities_freq[key_entity] = 1
                else:
                    entities_freq[key_entity] += 1
            entities_freq = sorted(entities_freq.items(), key=lambda x: x[1], reverse=True)
            article.nlp_annotations.json['entities'] = {
                'entities_list': entities,
                'entities_freq': entities_freq
            }

            # Adjectives
            adjectives = article.nlp_annotations.adjectives['stanza']
            adjectives_freq = {}
            for adjective in adjectives:
                if adjective['text'] not in adjectives_freq:
                    adjectives_freq[adjective['text']] = 1
                else:
                    adjectives_freq[adjective['text']] += 1
            adjectives_freq = sorted(adjectives_freq.items(), key=lambda x: x[1], reverse=True)
            article.nlp_annotations.json['adjectives'] = {
                'adjectives_list': adjectives,
                'adjectives_freq': adjectives_freq
            }

            # Sentiment
            sentiment = article.nlp_annotations.sentiment['pysentimiento']
            global_sentiment = (
                sentiment['label'],
                sentiment['scores'][sentiment['label']]
            )
            # Estamos agregando el texto de la oración con mayor score por label para validaciones
            # Despues se puede sacar para no mandarlo innecesariamente al front
            highest_scoring_sentence_per_label = {
                'POS': {'score': 0.0, 'start_char': 0, 'end_char': 0, 'sentence': ''},
                'NEG': {'score': 0.0, 'start_char': 0, 'end_char': 0, 'sentence': ''},
                'NEU': {'score': 0.0, 'start_char': 0, 'end_char': 0, 'sentence': ''}
            }
            for label in highest_scoring_sentence_per_label:
                #print(sentiment['sentences'])
                for sentence in sentiment['sentences']:
                    #if len(sentence['sentence']) > MIN_SENT_LENGHT:   
                        if sentence['label'] == label and sentence['scores'][label] > highest_scoring_sentence_per_label[label]['score']:
                            highest_scoring_sentence_per_label[label]['score'] = sentence['scores'][label]
                            highest_scoring_sentence_per_label[label]['start_char'] = sentence['start_char']
                            highest_scoring_sentence_per_label[label]['end_char'] = sentence['end_char']
                            highest_scoring_sentence_per_label[label]['sentence'] = sentence['sentence']
                

            article.nlp_annotations.json['sentiment'] = {
                    'global_sentiment': global_sentiment,
                    'highest_scoring_sentence_per_label': highest_scoring_sentence_per_label,
                    'title_sentiment': sentiment['titulo']
                }

            article.nlp_annotations.json['sources'] = article.nlp_annotations.sources["stanza"]
            
            article.nlp_annotations.json['metrics'] = article.nlp_annotations.metrics
            
    def _annotate_corpus(self, corpus, file_name: str = None):
        
        # pysentimiento        
        if self.libreria != 'pysentimiento':
            self._init_pysentimiento()
        
        self._extract_corpus_sentiment(corpus)
        self.calculate_corpus_metrics(corpus)

        # stanza
        self._init_stanza()
        self.analyze_corpus_cuerpo(corpus)
        self.calculate_corpus_metrics(corpus)

        # spacy
        self._init_spacy()
        self.analyze_corpus_cuerpo(corpus)
        self.calculate_corpus_metrics(corpus)

        # Armar json para front
        self._build_frontend_json(corpus)

        # Save JSON to file if file_name is provided
        if file_name:
            with open(file_name, 'w', encoding='utf-8') as f:
                out_json = {}
                for article in tqdm(corpus.articles.values()):
                    if 'id' not in article.get_article_dict().keys():
                        print('Each article requires an id')
                    out_json[article.get_article_dict()['id']]  = article.nlp_annotations.json
                json.dump(out_json, f, ensure_ascii=False, indent=4)
