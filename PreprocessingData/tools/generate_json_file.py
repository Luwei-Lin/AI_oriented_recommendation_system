
######################################################################################################
# This script is used for generating the pre-determined json files, which will be used for next script
# Generate processed dataset because these json files are the fundations to do standardlization process
# Make Sure the "Lables_v2.json" and "labels_2nd.json" are availble for processing.
# "lables_v2": which contains the relationship of the main_categories and sub_categories 
# "lables_2nd": which contains the relationship of the sencondary labels and the third layer lables.
# Speed: 466 (7 mins)seconds for current labels_v2.json and labels_2nd.json based on M1 Pro chips
# Author: Luwei Lin luwei2@ualberta.ca
# Date: Aug 15, 2022
######################################################################################################

import json
from typing import List
import spacy
import time
start_time = time.time()
#the detail to 
label3_to_label2_map = {}

all_sub_main = set()
#dict { 'shoes': {(all shoe types whatever it is the 2nd or 3rd class label)} }
products_to_all = {}
#dict { 'shoes': 1, ''}
main_categories_map_to_num = {}
#dict { 'heels': 1, 't-shirt': } specific item maps to the number
specific_products_map_to_num = {}
main_cat = {}
labels_2nd = {}

label3_to_label2_map = {}
pt = {}
st = {}

def read_file():
    global pt
    global st 
    global main_cat
    global labels_2nd
    f1 = open("./json_files/labels_v2.json")
    f2 = open("./json_files/labels_2nd.json")
    labels_2nd = json.load(f2)
    main_cat = [k for k in labels_2nd.keys()]
    label = json.load(f1)
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


def initialize_container():
    global st
    global pt
    global products_to_all
    global main_cat
    global specific_products_map_to_num
    global main_categories_map_to_num
    global labels_2nd
    global label3_to_label2_map
    
    sub_cat_all_keys = [key for key in st[0].keys()]
    sub_cat_shoes_keys = sub_cat_all_keys[0:4]
    sub_cat_tops_keys= sub_cat_all_keys[4:7]
    sub_cat_other_clothing_keys = sub_cat_all_keys[7:8] + sub_cat_all_keys[13:14]
    sub_cat_bottoms_keys = sub_cat_all_keys[8:13]
    sub_cat_acc_keys = sub_cat_all_keys[14: 19]
    sub_cat_beauty_keys = sub_cat_all_keys[19: ]
    all_main = {key for key in pt[0].keys()}
    print("all_main: ", all_main)

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
    #add all sub categories to the main 8 categories.
    for key in sub_cat_all_keys:#loop all keys in sub_main_categories, 
        if key in sub_cat_tops_keys:#if the key belongs to tops
            product_name_3rd_list = st[0].get(key)
            update_products_to_all(product_name_3rd_list + sub_cat_tops_keys, 'tops')
        elif key in sub_cat_shoes_keys:
            product_name_3rd_list = st[0].get(key)
            update_products_to_all(product_name_3rd_list + sub_cat_shoes_keys, 'shoes')
        elif key in sub_cat_bottoms_keys:
            product_name_3rd_list = st[0].get(key)
            update_products_to_all(product_name_3rd_list + sub_cat_bottoms_keys, 'bottoms')
        elif key in sub_cat_other_clothing_keys:
            product_name_3rd_list = st[0].get(key)
            update_products_to_all(product_name_3rd_list + sub_cat_other_clothing_keys, 'other_clothing')
        elif key in sub_cat_acc_keys:
            product_name_3rd_list = st[0].get(key)
            update_products_to_all(product_name_3rd_list + sub_cat_acc_keys, 'accessories')
        elif key in sub_cat_beauty_keys:
            product_name_3rd_list = st[0].get(key)
            update_products_to_all(product_name_3rd_list + sub_cat_beauty_keys, 'beauty') 
    for key in products_to_all.keys():
        assert products_to_all.get(key) != None
        products_to_all.update({key: list(products_to_all.get(key))})
    
    '''
    Build the hashmap all products has mapped to the number of categories
    '''
    for key in products_to_all.keys():
        map_number_of_this_key = main_categories_map_to_num.get(key)
        assert products_to_all.get(key) is not None
        #include the main_categories to number;
        specific_products_map_to_num.update({key: map_number_of_this_key})
        for item in products_to_all.get(key):
            specific_products_map_to_num.update({item: map_number_of_this_key})
    
    for cat in main_cat:
        temp_dict = labels_2nd.get(cat)
        assert labels_2nd != None
        for k in temp_dict.keys():
            item_list = temp_dict.get(k)
            
            for item_string in item_list:
                temp = lemma_string(item_string)
                temp_string = check_and_concat_punct(temp)
                label3_to_label2_map.update({temp_string:k})
            
            temp_key = lemma_string(k)
            key = check_and_concat_punct(temp_key)
            label3_to_label2_map.update({key:k})
    for key in ["homeware"]:
        item_list = products_to_all.get(key)
        assert item_list != None
        for item in item_list:
            label3_to_label2_map.update({item: "Homeware"})
    for k in label3_to_label2_map.keys():
        if k not in specific_products_map_to_num.keys():
            print(k)

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

def main():
    read_file()
    initialize_container()
    print("The whole provess takes %s seconds " % (time.time() - start_time))
    save_to_json()
main()