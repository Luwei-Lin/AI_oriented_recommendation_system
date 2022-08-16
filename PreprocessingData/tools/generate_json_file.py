import json
from typing import List
import spacy

label3_to_label2_map = {}

pt = {}
st = {}
def initialize():
    global pt
    global st 
    f = open("./json_files/labels_v2.json")
    label = json.load(f)
    pt = label.get("product_type")
    st = label.get("sub_product_type")

def check_and_concat_punct(temp:List[str]) -> str:
    """
    input: list, e.g. ['t', '-', 'shirt'], ['high', '-', 'rise', 'shoe']
    function: deal with the list with '-' punct
    output: "t-shirt" "high-rise shoe" "a-b-c color" 
    """
    temp_string = ""
    if temp.__contains__('-') and len(temp) == 3:
        temp_string = ''.join(temp)
    elif temp.__contains__('-') and len(temp) > 3:
        
        pos = temp.index('-')
        #if there is wrong position of '-'
        if pos < 1:
            temp_string = ' '.join(temp)
            return temp_string
        
        puct_string = temp[pos - 1] + temp[pos] + temp[pos + 1]
        rest_string = ' '.join(temp[pos + 2:])
        temp_string = puct_string + ' '+ rest_string
    else:
        temp_string = ' '.join(temp)
    
    return temp_string 


def lemma_string(original_string:str) -> List:
    """
    input: original string e.g. 'scandals', 'jackets/coats'
    funct: clean the string to the original words and put to list
    output: ['scandal'], ['jacket', 'coats'] 
    """
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(original_string.lower())
    temp = []
    for token in doc:
        if token.text == '&' or token.text == 'and' or token.text == '/' or token.text == ',' or token.text == ":":
            continue
        if token.text == "glasses" or token.text == 'booty' or token.text == 'jackets' or token.text == "cycling"\
            or token.text == "sunglasses" or token.text == "earrings" or token.text == 'coats' or token.text == "hipster": #some of them should be represented in plural format
            temp.append(token.text)
        else:
            temp.append(token.lemma_)
    return temp

sub_cat_all_keys = [key for key in st[0].keys()]
sub_cat_shoes_keys = sub_cat_all_keys[0:4]
sub_cat_tops_keys= sub_cat_all_keys[4:7]
sub_cat_other_clothing_keys = sub_cat_all_keys[7:8] + sub_cat_all_keys[13:14]
sub_cat_bottoms_keys = sub_cat_all_keys[8:13]
sub_cat_acc_keys = sub_cat_all_keys[14: 19]
sub_cat_beauty_keys = sub_cat_all_keys[19: ]
all_main = {key for key in pt[0].keys()}

all_sub_main = set()
#dict { 'shoes': {(all shoe types whatever it is the 2nd or 3rd class label)} }
products_to_all = {}
#dict { 'shoes': 1, ''}
main_categories_map_to_num = {}
#dict { 'heels': 1, 't-shirt': } specific item maps to the number
specific_products_map_to_num = {}
pt_index = 0
for key in pt[0].keys():
    product_name_2nd_list = pt[0].get(key)
    pt_key = key
    pt_value_set = set()
    
    for item_string in product_name_2nd_list:
        
        temp = lemma_string(item_string)
        temp_string = check_and_concat_punct(temp)
        
        #update set
        all_sub_main.add(temp_string)
        #update the value in the pair[]
        pt_value_set.add(temp_string)
    
    #main_to_sub map
    products_to_all.update({pt_key:pt_value_set})
    #product_to_num map
    pt_index += 1
    main_categories_map_to_num.update({pt_key:pt_index})

main_categories_map_to_num.update({"others" : 8})
main_categories_map_to_num.update({"unknown" : 0})
#if key in [scandals, sneakers, heels, boots], or [boots, shirts, sweaters, jackets, coats]
#print("Second: all main_categories\n", all_sub_main)

all_sub = set()
for key in st[0].keys():
    product_name_3rd_list = st[0].get(key) # get list of []
    for item_string in product_name_3rd_list: 
        #loop all item_string in order
        temp = lemma_string(item_string)
        temp_string = check_and_concat_punct(temp)
        temp_list = lemma_string(key)
        temp_string2 = check_and_concat_punct(temp_list)
        all_sub.add(temp_string)
        all_sub.add(temp_string2)
#print("Third: all sub catrgories\n", all_sub)


def update_products_to_all(string_list : List, main_key: str)->None:
    """
    Function: put all sub_categories to the relative the main_categories set
    Args:
        string_list (List): the list of all sub_categories
        main_key (str): the key of the main_categories
    """
    assert len(string_list) > 0
    assert products_to_all.get(main_key) is not None
    for item_string in string_list:
        temp = lemma_string(item_string)
        temp_string = check_and_concat_punct(temp) 
        products_to_all.get(main_key).add(temp_string)


def save_to_json():
    #save files
    with open("json_files/product_to_all.json", "w") as f1:
        json.dump(products_to_all, f1, indent=4)
    #parsed = json.dumps(products_to_all, indent=4)
    with open("json_files/main_categories_to_num.json","w") as f2:
        json.dump(main_categories_map_to_num,f2, indent=4)

    with open("json_files/specific_product_map_to_num.json", "w") as f3:
        json.dump(specific_products_map_to_num, f3, indent=4)
        
    with open("json_files/label3_to_label2.json", "w") as f4:
        json.dump(label3_to_label2_map, f4, indent=4)