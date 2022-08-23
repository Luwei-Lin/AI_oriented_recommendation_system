###########################################################################
# This script can generate NER training data set from processed.csv file
# 1. It will train the data can create model to the directory ./output
# 2. It will evaluate the model-best and model-last
#  
# Please make sure the input file path and type is correct,
# We are using the all predetermined paterns in directory "pattern_files"
# Also, make sure dataset path correct. In the same directory(or same path.
# Author: Luis Lin
# Date: Aug 17, 2022
###########################################################################

import spacy
import re
import pandas as pd
import json
from spacy.tokens import DocBin
from spacy.cli.train import train
import os

product_to_all = {}
main_cat_to_num = {}
original_labels_v2 = {}
patterns_words = set()
colors_words = set()
sizes_words = set()

nlp = spacy.load("en_core_web_lg")
entity_rulers = nlp.add_pipe("entity_ruler", validate=True)
nlp.remove_pipe("ner")

from typing import List
def check_puct(word: str)-> List:
    '''
    input : the string of product_type like "t-shirt", "tee shirt"
    function: build pattern syntax correctly
    output: List[{"LEMMA": "t"}, {"IS_PUNCT": True}, {"LEMMA":"shirt"}] 
    '''
    res = []
    if '-' in word:
        temp_list = word.split("-")
        num = 1
        for word in temp_list:
            res.append({"LEMMA":word})
            if num < len(temp_list):
                res.append({"IS_PUNCT": True, "OP": "?"})
            num += 1
    else:
        res.append({"LEMMA":word})
    
    return res 

def check_puct_and_lower_pattern(word: str) ->List:
    '''
    input : the string of product_type like "t-shirt", "tee shirt"
    function: build pattern syntax correctly
    output: List[{"LOWER": "t"}, {"IS_PUNCT": True}, {"LOWER":"shirt"}] 
    '''
    res = []
    if '-' in word:
        temp_list = word.split("-")
        num = 1
        for word in temp_list:
            res.append({"LOWER":word})
            if num < len(temp_list):
                res.append({"IS_PUNCT": True, "OP": "?"})
            num += 1
    else:
        res.append({"LOWER":word})
    
    return res 
def initilialize_containers():
    
    global product_to_all
    global main_cat_to_num
    global original_labels_v2
    global patterns_words
    global colors_words
    global sizes_words
    
    #Open Original files.
    f1 = open("json_files/product_to_all.json")
    f2 = open("json_files/main_categories_to_num.json")
    f3 = open("json_files/labels_v2.json")
    #get dictionary {"shoes": list[all categories]}
    product_to_all = json.load(f1)
    main_cat_to_num = json.load(f2)
    original_labels_v2 = json.load(f3)
    
    with open("patterns_files/patterns_for_clothes.txt") as pa:
        patterns_words =  {l.lower().removesuffix('\n') for l in pa.readlines()}
    
    with open("patterns_files/colors.txt") as colors_file:
        colors_words = {c.lower().removesuffix('\n') for c in colors_file.readlines()}
    for o in original_labels_v2.get('color'):
        colors_words.add(o.lower().strip()) 
    
    with open("patterns_files/sizes.txt") as sizes_file:
        sizes_words = {s.replace('"', '').removesuffix(",\n").replace("\n","") for s in sizes_file.readlines()}
    
    #list all known patterns we need to detect.
    shoes_words = product_to_all.get("shoes")
    tops_words = product_to_all.get("tops")
    bottoms_words = product_to_all.get("bottoms")
    other_clothing_words = product_to_all.get("other_clothing")
    beauty_words = product_to_all.get("beauty")
    accessories_words = product_to_all.get("accessories")
    homeware_words = product_to_all.get("homeware")
    others_words = product_to_all.get("others")

    shoes_words.append("shoes")
    tops_words.append("tops")
    bottoms_words.append("bottoms")
    others_words.append("others")
    beauty_words.append("beauty")
    accessories_words.append("accessory")
    homeware_words.append("home")
    other_clothing_words.append("other_clothing")
    
    genders_words = [o.lower().strip() for o in original_labels_v2.get("gender")]
    main_cats_words = list(main_cat_to_num.keys())
    colors_words = list(colors_words)
    patterns_words = list(patterns_words)
    sizes_words = list(sizes_words)


    shoes_patterns = []
    shoes_phrases_words = []
    shoes_single_words = []
    for item in shoes_words:
        if len(item.split()) > 1:
            shoes_phrases_words.append(item)
        else:
            shoes_single_words.append(item)
    for item in shoes_phrases_words:
        t = {"label": "SHOES", "pattern": [p for word in item.split() for p in check_puct(word)], "id": item}
        shoes_patterns.append(t)
        
    for word in shoes_single_words:
        t = {"label": "SHOES", "pattern": [p for p in check_puct(word)], "id": word}
        shoes_patterns.append(t)

    for item in shoes_phrases_words:
        t = {"label": "SHOES", "pattern": [p for word in item.split() for p in check_puct_and_lower_pattern(word)], "id": item}
        shoes_patterns.append(t)
        
    for word in shoes_single_words:
        t = {"label": "SHOES", "pattern": [p for p in check_puct_and_lower_pattern(word)], "id": word}
        shoes_patterns.append(t)
        
    for item in shoes_patterns:
        try:
            entity_rulers.add_patterns([item])
        except ValueError:
            print(item)
    
    bottoms_patterns = []
    bottoms_phrases_words = []
    bottoms_single_words = []
    for item in bottoms_words:
        if len(item.split()) > 1:
            bottoms_phrases_words.append(item)
        else:
            bottoms_single_words.append(item)
    for item in bottoms_phrases_words:
        t = {"label": "BOTTOMS", "pattern": [p for word in item.split() for p in check_puct(word)], "id": item}
        bottoms_patterns.append(t)
        
    for word in bottoms_single_words:
        t = {"label": "BOTTOMS", "pattern": [p for p in check_puct(word)], "id": word}
        bottoms_patterns.append(t)

    for item in bottoms_phrases_words:
        t = {"label": "BOTTOMS", "pattern": [p for word in item.split() for p in check_puct_and_lower_pattern(word)], "id": item}
        bottoms_patterns.append(t)
        
    for word in bottoms_single_words:
        t = {"label": "BOTTOMS", "pattern": [p for p in check_puct_and_lower_pattern(word)], "id": word}
        bottoms_patterns.append(t)
    for item in bottoms_patterns:
        try:
            entity_rulers.add_patterns([item])
        except ValueError:
            print(item)
    
    other_clothing_patterns = []
    other_clothing_phrases_words = []
    other_clothing_single_words = []
    for item in other_clothing_words:
        if len(item.split()) > 1:
            other_clothing_phrases_words.append(item)
        else:
            other_clothing_single_words.append(item)
    for item in other_clothing_phrases_words:
        t = {"label": "OTHER_CLOTHING", "pattern": [p for word in item.split() for p in check_puct(word)], "id": item}
        other_clothing_patterns.append(t)
        
    for word in other_clothing_single_words:
        t = {"label": "OTHER_CLOTHING", "pattern": [p for p in check_puct(word)], "id": word}
        other_clothing_patterns.append(t)
        
    for item in other_clothing_phrases_words:
        t = {"label": "OTHER_CLOTHING", "pattern": [p for word in item.split() for p in check_puct_and_lower_pattern(word)], "id": item}
        other_clothing_patterns.append(t)
        
    for word in other_clothing_single_words:
        t = {"label": "OTHER_CLOTHING", "pattern": [p for p in check_puct_and_lower_pattern(word)], "id": word}
        other_clothing_patterns.append(t)
        
    for item in other_clothing_patterns:
        try:
            entity_rulers.add_patterns([item])
        except ValueError:
            print(item)
    
    beauty_patterns = []
    beauty_phrases_words = []
    beauty_single_words = []
    for item in beauty_words:
        if len(item.split()) > 1:
            beauty_phrases_words.append(item)
        else:
            beauty_single_words.append(item)
    for item in beauty_phrases_words:
        t = {"label": "BEAUTY", "pattern": [p for word in item.split() for p in check_puct(word)], "id": item}
        beauty_patterns.append(t)
        
    for word in beauty_single_words:
        t = {"label": "BEAUTY", "pattern": [p for p in check_puct(word)], "id": word}
        beauty_patterns.append(t)
    for item in beauty_phrases_words:
        t = {"label": "BEAUTY", "pattern": [p for word in item.split() for p in check_puct_and_lower_pattern(word)], "id": item}
        beauty_patterns.append(t)
        
    for word in beauty_single_words:
        t = {"label": "BEAUTY", "pattern": [p for p in check_puct_and_lower_pattern(word)], "id": word}
        beauty_patterns.append(t)
        
    for item in beauty_patterns:
        try:
            entity_rulers.add_patterns([item])
        except ValueError:
            print(item)
    
    home_patterns = []
    home_phrases_words = []
    home_single_words = []
    for item in homeware_words:
        if len(item.split()) > 1:
            home_phrases_words.append(item)
        else:
            home_single_words.append(item)
    for item in home_phrases_words:
        t = {"label": "HOME", "pattern": [p for word in item.split() for p in check_puct(word)], "id": item}
        home_patterns.append(t)
        
    for word in home_single_words:
        t = {"label": "HOME", "pattern": [p for p in check_puct(word)], "id": word}
        home_patterns.append(t)
    for item in home_phrases_words:
        t = {"label": "HOME", "pattern": [p for word in item.split() for p in check_puct_and_lower_pattern(word)], "id": item}
        home_patterns.append(t)
        
    for word in home_single_words:
        t = {"label": "HOME", "pattern": [p for p in check_puct_and_lower_pattern(word)], "id": word}
        home_patterns.append(t)
        
    for item in home_patterns:
        try:
            entity_rulers.add_patterns([item])
        except ValueError:
            print(item)
    
    accessories_patterns = []
    accessories_phrases_words = []
    accessories_single_words = []
    for item in accessories_words:
        if len(item.split()) > 1:
            accessories_phrases_words.append(item)
        else:
            accessories_single_words.append(item)
    for item in accessories_phrases_words:
        t = {"label": "ACCESSORIES", "pattern": [p for word in item.split() for p in check_puct(word)], "id": item}
        accessories_patterns.append(t)
        
    for word in accessories_single_words:
        t = {"label": "ACCESSORIES", "pattern": [p for p in check_puct(word)], "id": word}
        accessories_patterns.append(t)
    for item in accessories_phrases_words:
        t = {"label": "ACCESSORIES", "pattern": [p for word in item.split() for p in check_puct_and_lower_pattern(word)], "id": item+"v2"}
        accessories_patterns.append(t)
        
    for word in accessories_single_words:
        t = {"label": "ACCESSORIES", "pattern": [p for p in check_puct_and_lower_pattern(word)], "id": word+"v2"}
        accessories_patterns.append(t)
        
    for item in accessories_patterns:
        try:
            entity_rulers.add_patterns([item])
        except ValueError:
            print(item)
    
    others_patterns = []
    others_phrases_words = []
    others_single_words = []
    for item in others_words:
        if len(item.split()) > 1:
            others_phrases_words.append(item)
        else:
            others_single_words.append(item)
    for item in others_phrases_words:
        t = {"label": "OTHERS", "pattern": [p for word in item.split() for p in check_puct(word)], "id": item}
        others_patterns.append(t)
        
    for word in others_single_words:
        t = {"label": "OTHERS", "pattern": [p for p in check_puct(word)], "id": word}
        others_patterns.append(t)

    for item in others_phrases_words:
        t = {"label": "OTHERS", "pattern": [p for word in item.split() for p in check_puct_and_lower_pattern(word)], "id": item+"v2"}
        others_patterns.append(t)
        
    for word in others_single_words:
        t = {"label": "OTHERS", "pattern": [p for p in check_puct_and_lower_pattern(word)], "id": word+"v2"}
        others_patterns.append(t)
    for item in others_patterns:
        try:
            entity_rulers.add_patterns([item])
        except ValueError:
            print(item)
            
    genders_patterns = []
    genders_phrases_words = []
    genders_single_words = []
    for item in genders_words:
        if len(item.split()) > 1:
            genders_phrases_words.append(item)
        else:
            genders_single_words.append(item)
    for item in genders_phrases_words:
        t = {"label": "GENDER", "pattern": [p for word in item.split() for p in check_puct(word)], "id": item}
        genders_patterns.append(t)
        
    for word in genders_single_words:
        t = {"label": "GENDER", "pattern": [p for p in check_puct(word)], "id": word}
        genders_patterns.append(t)

    for item in genders_phrases_words:
        t = {"label": "GENDER", "pattern": [p for word in item.split() for p in check_puct_and_lower_pattern(word)], "id": item}
        genders_patterns.append(t)
        
    for word in genders_single_words:
        t = {"label": "GENDER", "pattern": [p for p in check_puct_and_lower_pattern(word)], "id": word}
        genders_patterns.append(t)
    for item in genders_patterns:
        try:
            entity_rulers.add_patterns([item])
        except ValueError:
            print(item)
            
    patterns_patterns = []
    patterns_phrases_words = []
    patterns_single_words = []
    for item in patterns_words:
        if len(item.split()) > 1:
            patterns_phrases_words.append(item)
        else:
            patterns_single_words.append(item)
    for item in patterns_phrases_words:
        t = {"label": "PATTERN", "pattern": [p for word in item.split() for p in check_puct(word)], "id": item}
        patterns_patterns.append(t)
        
    for word in patterns_single_words:
        t = {"label": "PATTERN", "pattern": [p for p in check_puct(word)], "id": word}
        patterns_patterns.append(t)
        
    for item in patterns_phrases_words:
        t = {"label": "PATTERN", "pattern": [p for word in item.split() for p in check_puct_and_lower_pattern(word)], "id": item+"v2"}
        patterns_patterns.append(t)
        
    for word in patterns_single_words:
        t = {"label": "PATTERN", "pattern": [p for p in check_puct_and_lower_pattern(word)], "id": word+"v2"}
        patterns_patterns.append(t)
        
    for item in patterns_patterns:
        try:
            entity_rulers.add_patterns([item])
        except ValueError:
            print(item)
    
    colors_patterns = []
    colors_phrases_words = []
    colors_single_words = []
    for item in colors_words:
        if len(item.split()) > 1:
            colors_phrases_words.append(item)
        else:
            colors_single_words.append(item)
    for item in colors_phrases_words:
        t = {"label": "COLOR", "pattern": [p for word in item.split() for p in check_puct(word)], "id": item}
        colors_patterns.append(t)
        
    for word in colors_single_words:
        t = {"label": "COLOR", "pattern": [p for p in check_puct(word)], "id": word}
        
        colors_patterns.append(t)

    for item in colors_phrases_words:
        t = {"label": "COLOR", "pattern": [p for word in item.split() for p in check_puct_and_lower_pattern(word)], "id": item}
        colors_patterns.append(t)
        
    for word in colors_single_words:
        t = {"label": "COLOR", "pattern": [p for p in check_puct_and_lower_pattern(word)], "id": word}
        colors_patterns.append(t)
    for item in colors_patterns:
        try:
            entity_rulers.add_patterns([item])
        except ValueError:
            print(item)
    
    sizes_patterns = []
    #only s, m, l, large, small, medium describe size word can be added to sizes_word
    for word in sizes_words:
        if word in ['S', 'M', 'L']: 
            t = {"label":"SIZE","pattern":word, "id":word}
        else:
            t = {"label":"SIZE","pattern":[{"LOWER": word}], "id":word}
        sizes_patterns.append(t)
    for item in sizes_patterns:
        try:
            entity_rulers.add_patterns([item])
        except:
            print(item)
            
class Training_sample:
    annotations_count = {}
    text = ""
    annotations = []
    def __init__(self, text, annotations):
        self.text = text
        self.annotations = annotations
        self.annotations_count = {}
        if len(annotations) != 0:
            for start, end, label in annotations:
                if label not in self.annotations_count.keys():
                    self.annotations_count.update({label:1})
                else:#existed
                    temp = self.annotations_count.get(label) + 1
                    self.annotations_count.update({label:temp})
                    
    def get_text(self)->str:
        return self.text
    def get_annotations(self)->List:
        return self.annotations
    def get_annotations_count(self)->dict:
        return self.annotations_count
    def get_labels(self) -> set:
        return set(self.annotations_count.keys())
    def get_format(self) -> tuple:
        return (self.text, self.annotations)

def parse_train_data(text):
    """
    Parse raw text to training format

    Args:
        text (str): text_based product description

    Returns:
        Tuple: (text, [label and position])
    """
    doc = nlp(text)
    #ignore for now 
    #detections = [(doc[start:end].start_char, doc[start:end].end_char, 'TOPS') for idx, start, end in type_matcher(doc) ]
    
    detections = [(ent.start_char, ent.end_char, ent.label_) for ent in doc.ents]
    #detections =  [(span.start_char, span.end_char, 'TOPS') for span in spacy.util.filter_spans(spans)] #remove duplicates or overlaps using spacy.util.filter_spans
    
    regex_string = r"(\d+(?:\.|\/|)\d+|\d+) ?(?:\-|x) ?(\d+(?:\.|\/|)\d+|\d+) ?(?:\-|x) ?(\d+(?:\.|\/|)\d+|\d+) ?(?:mm|MM|cm|CM|[Ii]nches|in|\"|)|(\d+(?:\.|\'|\/|)\d+ ?(?:\%|cm|CM|mm|MM|[Ii]nches|inch|in|\"))|(\d*(?:X{1,3}[SL]))|\d+(?:$|\.|\/|\d+) ?\d+|(\d+(?:\.|\/|)\d+|\d+) ?(?:\-|x) ?(\d+(?:\.|\/|)\d+|\d+) ?(?:mm|MM|cm|CM|[Ii]nches|in|\"|)"
    size_matches = re.finditer(regex_string, text)
    size_detections = [(match.start(), match.end(),'SIZE') for match in size_matches]
    detections = detections + size_detections
    detections.sort(key = lambda x: x[0])
    return (doc.text, detections)

def create_training(dataset: List[tuple])->DocBin:
    db = DocBin()
    unpassed_text = []
    for text, annotations in dataset:
        doc = nlp(text)
        ents = []
        for start, end, label in annotations:
            span = doc.char_span(start, end, label=label, alignment_mode="expand")#,alignment_mode="strict")
            if span is None:
                continue
            else:
                ents.append(span)
        try:
            doc.ents = ents
        except:
            unpassed_text.append(text)
        db.add(doc)
    #db.to_disk("./train.spacy")
    print("unpassed sample: ", len(unpassed_text))
    return db

def loop_dataset(df):
    """
    This function will loop all product descriptions and generate NER trainning dataset.
    Args:
        df (panda dataframe): preprocessed dataset, the product description already cleaned.
    """
    should_have_labels = {'COLOR', 'SIZE', 'GENDER', 'PATTERN'}
    training_data_1 = []
    training_data_2 = []
    training_data_3 = []
    training_data_4 = []
    training_data_5 = []

    for row in range(df.shape[0]):
        text = df.iloc[row]['raw_text']
        #if the raw_text is empty then just ignore
        if not isinstance(text, str):
            #empty_rows.append(row)
            continue
        text, annotations = parse_train_data(text)
        ts = Training_sample(text, annotations)
        intersection_set = ts.get_labels().intersection(should_have_labels)
        if len(intersection_set) == 1:
            training_data_1.append(ts.get_format())
        elif len(intersection_set) == 2:
            training_data_2.append(ts.get_format())
        elif len(intersection_set) == 3:
            training_data_3.append(ts.get_format())
        elif len(intersection_set) == 4:
            training_data_4.append(ts.get_format())
        else:
            training_data_5.append(ts.get_format())
    print("training_data_1",len(training_data_1))
    print("training_data_2",len(training_data_2))
    print("training_data_3",len(training_data_3))
    print("training_data_4",len(training_data_4))
    print("training_data_5(else)",len(training_data_5))
    t2 = len(training_data_2)
    t2_60 = int(len(training_data_2) * 0.6)
    t2_80 = int(len(training_data_2) * 0.8)
    t3 = len(training_data_3)
    t3_60 = int(len(training_data_3) * 0.6)
    t3_80 = int(len(training_data_3) * 0.8)
    t4 = len(training_data_4)
    t4_60 = int(len(training_data_4) * 0.6)
    t4_80 = int(len(training_data_4) * 0.8)
    
    unseen = training_data_2[t2_80:] + training_data_3[t3_80:] + training_data_4[t4_80:]
    print("train_len: ", t2_60 + t3_60 + t4_60, "valid: ", ((t2_80 + t3_80 + t4_80) - (t2_60 + t3_60 + t4_60)), "unseen: ",  len(unseen))
    #the data the machine never seen, not (train/valid)
    
    train_data = create_training((training_data_2[0:t2_60] + training_data_3[0: t3_60] + training_data_4[0: t4_60]))
    train_data.to_disk("./train_data/train.spacy")

    valid_data = create_training((training_data_2[t2_60:t2_80] + training_data_3[t3_60:t3_80] + training_data_4[t4_60: t4_80]))
    valid_data.to_disk("./train_data/dev.spacy")

    evaluate_data = create_training(unseen)
    evaluate_data.to_disk("./train_data/evaluate.spacy")
    
def train_spacy():
    print("start training models...")
    train(config_path="./train_data/config.cfg", output_path="./output_model",overrides={"paths.train": "./train_data/train.spacy", "paths.dev": "./train_data/dev.spacy"})

def evaluate_model():
    print("evaluating model-best...")
    os.system("python -m spacy evaluate ./output_model/model-best ./train_data/evaluate.spacy")
    print("evaluating model-last...")
    os.system("python -m spacy evaluate ./output_model/model-last ./train_data/evaluate.spacy")
    
def main():
    initilialize_containers()
    
    ########for debugging use#####
    #text = input()
    #print(parse_train_data(text))
    ########for debugging use#####
    
    #make sure the path of dataset is correct
    df = pd.read_csv("./(V1.8)all_products_data_set.csv")
    #create training data to the directory ./train_data/
    loop_dataset(df)
    #start to train model based on dataset we created.
    train_spacy()
    #model will save to ./output_model
    evaluate_model()
# run the program
# main()