

import spacy
from spacy import displacy
import entity_options as e
import webbrowser

def test_the_input(product_description:str):
    nlp = spacy.load("./output_model/model-best")

    doc1 = nlp(product_description)
    ents = []
    for ent in doc1.ents:
        ents.append((ent.start_char, ent.end_char, ent.text, ent.label_))
    print(doc1.text, ents)
    #displacy.serve([doc1], options=e.get_entity_options(),style="ent", port=5000, host="127.0.0.1")
    #type 127.0.0.1:5000 on the webbroswer

example = "bohemian "
test_the_input(example)