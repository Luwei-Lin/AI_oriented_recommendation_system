import re
from tkinter.messagebox import NO
from certifi import contents

import spacy
from spacy.matcher import Matcher
from spacy import displacy

def clean_tags_text(raw_tags, raw_title, raw_product_type):
    tags = ''
    title = ''
    product_type = ''
    
    
    if isinstance(raw_tags, str) and raw_tags is not None:
        tags = re.sub("," , " " , raw_tags.lower())
        
    if isinstance(raw_title, str)and raw_title is not None:
        title = raw_title.lower()
    if isinstance(raw_product_type, str) and raw_product_type is not None :
        product_type = re.sub("," , " " , raw_product_type.lower())
    
    reg_str = '{(.*?)}'
    tags = re.sub('"', "", tags)
    
    contents = re.findall(reg_str, tags)
    contents.append(title)
    contents.append(product_type)
    
    content_output = ', '.join(contents)
    
    return content_output

def clean_product_description(raw_product_description):
    #remove all ' or " 
    product_description = raw_product_description.lower()
    contents = re.sub('"', "", product_description)
    contents = re.sub("'", "", product_description)
    return contents

def create_patterns_matcher():
    
    product_patterns = [{'lemma' : {'IN' : ['shoe', 'top', 'bottom', 'clothing', 'beauty', 'accessory', 'homeware', 'other']}, 'POS': {'NOT_IN':['ADJ']}}]
    
    bottom_pattern_1 = [{'LEMMA': {'IN': [
            'legging', 
            'bottom', 
            'leg', 
            "short",
            "skirt",
            "jogger",
            "jean",
            "legging",
            "athletic boxer",
            "sweatpant"] } } ]
    bottom_pattern_2 = [{'LOWER' : 'athletic'},
                        {'IS_PUNCT' : True, 'OP' : '?'},
                        {'LOWER' : 'boxer'}]
    
    tops_pattern_1 = [
        {'LOWER': 't'},
        {'IS_PUNCT' : True, 'OP': '?'},
        {'LOWER': 'shirt'},
        ]
    tops_pattern_2 = [{'LEMMA': {'IN': [
        "jacket",
        "camisole",
        "shirt",
        "coat",
        "sweater",
        "blouse",
        "kimono",
        "cardigan",
        "hoodie",
        "vest",
        "poncho",
        "blazer",
        "sweatshirt",
        "2aistcoat",
        "bralette",
        "bra",
        "jersey",
        "t",
        "tee",
        'tank',
        "croptee",
        "croptop",
        "tanktop"]}}]
    tops_pattern_3 = [{'LEMMA': 'tank'}, {'IS_PUNCT': True, 'OP': '?'}, {'LEMMA': 'top'}]
    
    shoes_pattern_1 = [{ 'LEMMA': { 'IN' : [
        "slipper",
        "flat shoe",
        "sandal",
        "heel",
        "boot",
        "skate shoe",
        "wedge",
        "snowshoe",
        "clog",
        "sneaker",
        "oxford",
        "loafer"
    ]}}]
    shoes_pattern_2 = [{'LOWER': 'flat'},
        {'IS_PUNCT' : True, 'OP' : '?'},
        {'LOWER': 'shoe'},]
    shoes_pattern_3 = [{'LOWER': 'oxford'},
        {'IS_PUNCT' : True, 'OP' : '?'},
        {'LOWER': 'loafer'}]
    
    other_clothing_pattern_1 = [{'LEMMA' : {'IN': [
        "swimwear",
        "dress",
        "jumpsuit",
        "underwear",
        "overall",
        "activewear",
        "sleepwear",
        "romper"
    ]}}]
    other_clothing_pattern_2 = [{'LOWER': 'jumpsuit'},
                                {'IS_PUNCT': True, 'OP': '?'},
                                {'LOWER': 'and'},
                                {'IS_PUNCT': True, 'OP': '?'},
                                {'LOWER': 'romper'}]
    
    beauty_pattern_1 = [{"LOWER": 'skin'}, {'IS_PUNCT' : True, 'OP' : '?'}, {'LOWER': 'care'}]
    beauty_pattern_2 = [{"LOWER": 'beauty'}, {'IS_PUNCT' : True, 'OP' : '?'}, {'LEMMA': 'tool'}]
    beauty_pattern_3 = [{"LEMMA": 'cosmetic'}]
    beauty_pattern_4 = [{"LOWER": 'hair'}, {'IS_PUNCT' : True, 'OP' : '?'}, {'LOWER': 'care'}]
    beauty_pattern_5 = [{"LOWER": 'nail'}, {'IS_PUNCT' : True, 'OP' : '?'}, {'LOWER': 'care'}]
    
    accessories_pattern_1 = [{'LEMMA': { 'IN' : [
            "headwear",
            "jewelry",
            'bag',
            'scarf',
            'sock',
            'tight',
            'belt',
            'collar',
            'sticker',
            'cologne',
            'heel cover',
            'backpack',
            'glove',
            'headband',
            'mask',
            'sunglass',
            'shawl',
            'wallet',
            'tie',
            'pocket square',
            'watch',
            'shoe lace'
            ] }, 'POS': {'NOT_IN' :['VERB']}}] #tight, headwear
    accessories_pattern_2 = [{'lemma': 'heel'}, {'IS_PUNCT' : True, 'OP' : '?'}, {'lemma': 'cover'}]
    accessories_pattern_3 = [{'lemma': 'shoe'}, {'IS_PUNCT' : True, 'OP' : '?'}, {'lemma': 'lace'}]
    accessories_pattern_4 = [{'lemma': 'pocket'}, {'IS_PUNCT' : True, 'OP' : '?'}, {'lemma': 'square'}]
    
    homware_pattern_1 = [{'lemma': {'IN': [ 
                    'drinkware',
                    'soap',
                    'candle',
                    'blanket',
                    'towel',
                    'canteen',
                    'rug',
                    'mat'
                    ]}}]
    homware_pattern_2 = [{'lemma':'home'}, {'IS_PUNCT' : True, 'OP' : '?'}, {'lemma': 'decoration'}]
    homware_pattern_3 = [{'lemma':'bath'}, {'IS_PUNCT' : True, 'OP' : '?'}, {'lemma': 'bomb'}]
    homware_pattern_4 = [{'lemma':'bath'}, {'IS_PUNCT' : True, 'OP' : '?'}, {'lemma': 'robe'}]
    homware_pattern_5 = [{'lemma':'air'}, {'IS_PUNCT' : True, 'OP' : '?'}, {'lemma': 'freshener'}]
    homware_pattern_6 = [{'lemma':'shower'}, {'IS_PUNCT' : True, 'OP' : '?'}, {'lemma': 'curtain'}]
    homware_pattern_7 = [{'lemma':'bath'}, {'IS_PUNCT' : True, 'OP' : '?'}, {'lemma': 'mat'}]
    homware_pattern_8 = [{'lemma':'duvet'}, {'IS_PUNCT' : True, 'OP' : '?'}, {'lemma': 'cover'}]
    
    nlp = spacy.load("en_core_web_md")
    matcher = Matcher(nlp.vocab, validate=True)

    matcher.add("BOTTOMS_TYPE", [bottom_pattern_1, bottom_pattern_2])
    matcher.add("TOPS_TYPE", [tops_pattern_1, tops_pattern_2, tops_pattern_3])
    matcher.add("SHOES_TYPE", [shoes_pattern_1, shoes_pattern_2, shoes_pattern_3])
    matcher.add("OTHER_CLOTHING_TYPE", [other_clothing_pattern_1, other_clothing_pattern_2])
    matcher.add("BEAUTY_TYPE", [beauty_pattern_1, beauty_pattern_2, beauty_pattern_3, beauty_pattern_3, 
                                beauty_pattern_4, beauty_pattern_5])
    matcher.add("ACCESSORIES_TYPE", [accessories_pattern_1,  accessories_pattern_2,
                                    accessories_pattern_3, accessories_pattern_4])
    matcher.add('HOMEWARE_TYPE', [homware_pattern_1, homware_pattern_2, homware_pattern_3, homware_pattern_4,
                                homware_pattern_5, homware_pattern_6, homware_pattern_7, homware_pattern_8])
    matcher.add('PRODUCT_TYPE', [product_patterns])
    
    return matcher
    

def test_matcher(contents):
    assert(contents is not None)
    contents = contents.lower()
    nlp = spacy.load("en_core_web_md")
    doc = nlp(contents)
    type_matcher = create_patterns_matcher()
    for match_id, start, end in type_matcher(doc):
        print( doc[start:end].lemma_)
        
def main():
    test_text_1 = 'Looking for Paradise? Look no further than Paradise SweetLegs, \
    part of our amazing 2019 leggings collection! This print features white abstract shapes placed on top of blue, \
    indigo, coral, fuchsia, and peach ferns on a bright orange-red background.Paradise SweetLegs are the perfect getaway print, \
    and they look absolutely stunning paired with a long white tunic tank, baby pink Birkenstocks, \
    and a top knot featuring a matching Paradise scrunchie.* \
    Final Sale Item  Grab the matching Scrunchie and Own It!'
    nlp = spacy.load("en_core_web_sm")
    test_text_2 = "cotopaxi outerwear womens, cotopaxi women's teca half-zip windbreaker postcard, jackets"
    test_text_2 = re.sub(',', ' ', test_text_2)
    tokens = nlp (test_text_2)
    
    l = [(t, t.lemma_, t.pos_) for t in tokens]
    
    print (l)
    test_matcher(test_text_2)

main()