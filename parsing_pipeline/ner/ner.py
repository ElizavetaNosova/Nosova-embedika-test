import os
from navec import Navec
from slovnet import NER
from collections import defaultdict
from typing import Dict, List


current_file_dir = os.path.dirname(os.path.realpath(__file__))
MODELS_DIR = os.path.abspath(os.path.join(current_file_dir, "models"))
ner = None


def init_ner():
    navec = Navec.load(os.path.join(MODELS_DIR, 'navec_news_v1_1B_250K_300d_100q.tar'))
    ner = NER.load(os.path.join(MODELS_DIR, 'slovnet_ner_news_v1.tar'))
    ner.navec(navec)
    return ner


def markup(text:str):
    global ner
    if not ner:
        ner = init_ner()
    return ner(text)


def extract_entities(text:str):
    markup_output = markup(text)
    entities = defaultdict(list)
    for span in markup_output.spans:
        type_ = span.type
        entity = text[span.start:span.stop]
        entities[type_].append(entity)
    return dict(entities)
