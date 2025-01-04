# trust-monitor
Our goal is to develop a prototype that uses AI to identify specific quality indicators within news stories within the newsroom environment. This AI Monitor will be tailored specifically for newsroom editors, helping them to identify issues such as a lack of sources, an excess of adjectives, or discrepancies in information that can be addressed using online tools such as Fact-Checker Explorer.

## Index

- [trust-monitor](#trust-monitor)
  - [Index](#index)
  - [Installation](#installation)
  - [Usage](#usage)
  - [Project Structure](#project-structure)

## Installation
1. Clone the Repository
2. Navigate to the Project Directory
3. Create a Virtual Environment (Optional but Recommended):
```bash
python -m venv venv
```
Create a virtual environment named venv. To activate the virtual environment:
* On Windows:
```bash
.\venv\Scripts\activate
```
* On macOS and Linux:
```bash
source venv/bin/activate
```
4. Install Project and Dependencies (inside the project directory):
```bash
pip install -e .
```
5. Download SpaCy Language Model (for Spanish):
If you plan to use the project with Spanish language processing, you need to download the SpaCy language model. Run the following command:
```bash
python -m spacy download es_core_news_sm
```




## Usage

Execute the main script to run the project.
```bash
python main.py
```

Alternatively, you can try it in a Live Python Terminal, as follows:

```bash
from trustmonitor.nlp import NLP

nlp = NLP('es', 'spacy')
doc = nlp.analyze("El presidente de la Cámara de Propietarios de la República Argentina aseguró...")
entities = nlp.extract_entities(doc)
entities_count = nlp.count_entities(doc)
adjectives = nlp.extract_adjectives(doc)
adjective_count = nlp.count_adjectives(doc)
adjective_type_counts = nlp.count_adjective_types(doc)
entity_type_counts = nlp.count_entity_types(doc)
entity_sentiments = nlp.extract_entity_sentiments(doc)
```

## Project Structure

```bash
/trustmonitor
    |-- nlp.py
    |-- import_utils.py
    |-- articles.py
/data
    |-- docs
    |-- manual
    |-- raw
|-- main.py
|-- requirements.txt
|-- setup.py
|-- README.md
```

## Output Response 
[see doc.](./Trust_API_Anotacion_Noticias_Documentacion.pdf)
