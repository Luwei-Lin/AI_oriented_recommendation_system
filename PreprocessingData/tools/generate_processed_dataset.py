
#################################################################
# This script can generate processed_dataset.csv from original.csv, which including a). html_cleaner, b). color_similarity_matching(colors-standardization), 
# c). product_similarity_mapping(product-standardization) 
# 1. product_labels are separated to three layers, the first layer is the main categories, the second layer is the sub-category, and the third layer(optional) is the details of the product-name
# 2. colour_labels are the results from colour-name query to colornames.org and color-distance similarity algorithm calculation, which is a color standardization process.
# 3. html_cleaner will extract product description (raw_text based) and save content in 'raw_text' column
#
# Please make sure the input file path and type is correct,
# We are using the all predetermined labels in directory "json_files"
# Also, make sure product_to_all.json and main_to_num.json
# in the same directory(or same path.) Since these two files
# are the standardize information we use and the product label 
# map to the number we predefined.
# 
# Speed : 1000 data in 1107 seconds (18 mins) with M1 pro Chip, total 28426 data took 12310 seconds(3 hr 25 mins)
# Author: Luis Lin
# Date: Aug 7, 2022
#################################################################
import json
import spacy 
from difflib import SequenceMatcher
from typing import List
import pandas as pd
from string_grouper import match_strings, match_most_similar
import numpy as np
import text_cleaner as tc
import re
import time
import requests
from bs4 import BeautifulSoup
import multiprocessing as mp
#from pandarallel import pandarallel
start_time = time.time()

#the main_categories with all sub_categories dict
products_to_all = {}
#the main_categories relate to numbers dict
main_categories_map_to_num = {}
#all categories of product including the name of main_cat
all_cat = set()
#each specific item maps to the main_categories_number
specific_products_map_to_num = {}
#generate label_2nd class from specific labels
label3_to_label2_map = {}
#generate colorname_to_hex from our predetermined colors name json file
colorname_to_hex_map = {}

def parallelize_dataframe(df:pd.DataFrame, func, n_cores=mp.cpu_count())->pd.DataFrame:
    """This is a parallelize calculated function

    Args:
        df (pd.DataFrame): the dataframe of pandas, we are going to use.
        func (_type_): for each line calculation, we are going to implement.
        n_cores (_type_, optional): Defaults to mp.cpu_count().

    Returns:
        pd.DataFrame: After calculation, the return new dataframe.
    """
    df_split = np.array_split(df, n_cores)
    pool = mp.Pool(n_cores)
    df = pd.concat(pool.map(func, df_split))
    pool.close()
    pool.join()
    return df
#######################################################################################################
# Color Section
######################################################################################################

def color_text_cleaner(colors: str)->str:
    """
    Input: colors(str), format {"Colours_1", "Colours_2"}
    Function: text processing and get the colour information separated by comma ','
    Output: Colours(str), format "colours_1, colours_2"
    """
    temp = (colors.lower().removeprefix("{").removesuffix("}"))
    res = re.sub('"', "", re.sub("/",",",temp))
    return res
#reset df all "colors" colomn format

def reset_colors_format(df: pd.DataFrame):
    '''
    Input: panda.DataFrame
    Function: By using tc function above to reset all cells in 'colors' colomn
    Output: None
    '''
    for row in range(df.shape[0]):
        if not isinstance(df.loc[row]["colors"], str):
            df.loc[row,'colors'] = ""
            continue
        e = df.loc[row]["colors"]
        c = color_text_cleaner(e)
        df.loc[row,'colors'] = c

def requery_color_name(df: pd.DataFrame)->None:
    ''' 
    Input: dataframe (panda.Dataframe)
    Function: check color cells inside the dataframe row by row, send requery to the colornames.org to get colour hex and save it as the set()
    Output: None 
    '''
    for row in range(df.shape[0]):
        
        res = set()
        pattern = set()
        
        colors_str = df.loc[row]["colors"]
        if colors_str == "":
            continue
        colors_list = colors_str.split(",")
        
        #print(row, colors_list)
        for item in colors_list:
            #Method 1: if we can find the colors_name locally, then we just use this color name and hexCode 
            if colorname_to_hex_map.get(item) != None:
                colorname= " ".join([e.capitalize() for e in item.split(" ")])
                res.add(colorname + " (" + colorname_to_hex_map.get(item) + ")")
            else:
            #Method 2: if we can not find the colors_name locally, we will send query to the website colorsname.org to see if they have the name. Else we will treat it as pattern info
                URL = "https://colornames.org/search/results/?type=exact&query="
                URL += item
                try:
                    page = requests.get(URL)
                    soup = BeautifulSoup(page.content, "html.parser")
                    results = soup.find_all("a", class_="button is-fullwidth freshButton")
                    
                    #the first result which has the highest vote
                    content = results[0].find("span").text.strip()
                    res.add(content)
                except:
                    pattern.add(item)
        #res, pattern = df['colors'].apply(requery_func, axis=1)
        df.loc[row, "color_info"] = ",".join(res)
        df.loc[row, "pattern_info"] = ",".join(pattern)

from colormath.color_objects import sRGBColor, LabColor
from colormath.color_conversions import convert_color
from colormath.color_diff import delta_e_cie2000
from PIL import ImageColor

class Color:
    """
    Class Color: for encapsulate all related color infomation.
    """
    def __init__(self, color_string:str):
        assert color_string != None
        color_info = color_string.split(" (")
        assert len(color_info) == 2
        self.name = color_info[0]
        self.hex_code = color_info[1].removesuffix(")")
        
    def get_rgb(self)->tuple:
        assert self.hex_code != None
        return ImageColor.getcolor(self.hex_code, "RGB")
        
    def get_info(self) ->str:
        return self.name + " "+ self.hex_code
    
def difference(color_1:Color, color_2:Color)->float:
    """
    Input: format("color_name": "color_hex_code"), for example, color_1 = (Color class)Navy (#000080), color_2 = (Color class)Blue (#0000ff)
    Function: calculate delta_e_cie2000 color distance
    Output: Float, the distance 
    """
    assert color_1 != None and color_2 != None, "color_1 or color_2 is Nonetype"
    color1_set = color_1.get_rgb()
    color1_rgb = sRGBColor(color1_set[0], color1_set[1], color1_set[2])
    color2_set = color_2.get_rgb()
    color2_rgb = sRGBColor(color2_set[0], color2_set[1], color2_set[2])
    #convert from RGB to lab color space
    color1_lab = convert_color(color1_rgb, LabColor)
    color2_lab = convert_color(color2_rgb, LabColor)
    
    return delta_e_cie2000(color1=color1_lab, color2=color2_lab)

def get_closest_color(unknown_color:Color)->int:
    """
    Input: (Color class) to_be_determined_color
    Function: By Comparing with colors_distance in the predetermined color list, we extract the closest main_color.
    Output: The cloest color in the list
    """
    assert unknown_color != None
    #sort dict {color_num: int : color_distacne: float}
    temp_distance_map = {}
    main_color = {1: 'Black (#000000)', 2: 'Blue (#0000ff)', 3: 'Brown (#964b00)', 4: 'Green (#00ff00)', 5: 'Grey (#808080)', 6: 'Orange (#ff8000)', 7: 'Pink (#ffc0cb)', 8: 'Purple (#800080)', 9: 'Red (#ff0000)', 10: 'Tan (#d2b48c)', 11: 'White (#ffffff)', 12: 'Yellow (#ffff00)'}
    for k, v in main_color.items():
        dist = difference (unknown_color, Color(v))
        temp_distance_map.update({k:dist})
        
    sorted_dict = dict(sorted(temp_distance_map.items(), key=lambda item: item[1]))
    
    return min(sorted_dict, key=sorted_dict.get)

def from_color_info_to_color_num(color_info:str)->list:
    """
    Input: (str) color_info
    Function: standarized from the color_info column to color_num
    Output: (str)all relative nums (in the relative order)
    """
    assert isinstance(color_info, str) and color_info != ""
    res = list()
    color_info_list = color_info.split(",")
    
    for item in color_info_list:
        curr = Color(item)
        res.append(get_closest_color(curr))
    return res
    
def colour_mapping(df_original: pd.DataFrame):
    """
    Input: pandas.DataFrame
    Function: By using color distance algorithm to standardize the color info, and map the res to our main pre-determined 14 colors.
    Output: None, but you can use the df.to_csv("temp.csv", index=False) to check the mapping result correctness
    """
    for row in range(df_original.shape[0]):
        color_info = df_original.loc[row]["color_info"]
        #if color_info is empty
        if color_info == "":
            continue
        try:
            color_num_str = ",".join(str(n) for n in from_color_info_to_color_num(color_info))
            df_original.loc[row, "color_num"] = color_num_str
        except:
            print("Error: ", row, " color_info ", color_info )

#######################################################################################################
# Product Names Standardization Section
######################################################################################################

def similar(a: str, b: str) -> float:
    '''
    Input: two separate strings
    Function:
        We provide another statistic model (ML) from spacy.similarity to compare two strings similarity firstly.
        if spacy similarities doesn't not exit like 0.0, then we compare two strings similarity by "gestalt pattern matching" 
        not_Statistic model(ML)  It is a character-based matcher. 
    Output: Similarity [0, 1] between those two strings
    '''
    nlp = spacy.load("en_core_web_md")
    doc1 = nlp(a)
    doc2 = nlp(b)
    statistical_method_score = doc1.similarity(doc2)
    non_statistical_method_score = SequenceMatcher(None, a, b).ratio()
    if statistical_method_score < 0.1:
        return non_statistical_method_score
    return statistical_method_score

def lemma_string(original_string:str) -> str:
    '''
    Input: string
    Function: remove any plural format and wired suffix, for example, dresses -> ['dress']
    Output: list 
    '''
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(original_string.lower())
    temp = []
    for token in doc:
        if token.text == '&' or token.text == 'and' or token.text == '/' or token.text == ',':
            continue
        if token.text == "glasses" or token.text == 'booty' or token.text == "sunglasses" or token.text == "earrings": #some of them should be represented in plural format
            temp.append(token.text)
        else:
            temp.append(token.lemma_)
    return " ".join(temp)

def modify_product_type(original:str):
    '''
    input: original string
    function: remove pre_suffix of the original 'product_type' to match more accurate items
    output: modified string
    '''
    
    if len(original) <= 1:
        return original
    removable_words = ["clothing", "sale", "man", "men","mens", "men's", "woman", "women", "womens", "women's",  "unisex",\
        "girl", "girls", "girl's", "lady", "ladies", "snow","ladies'", "active","boy", "boys", "boy's", "graphic", "premium", \
            "cozy", "designer","comfort", "athletic","casual", 'youth', 'adult','formal']
    original = original.replace("+", " ").replace("-", " ").replace("&", " ").replace("/", " ").replace(",", " ")
    original = re.compile(r"\s+").sub(" ", original).strip()
    ori_list = original.split(" ")
    
    acc = ['acc', 'accessory', 'acessories','accesssories','accessories', "jewelry","polarized", "non polar"]
    shoes = ['footwear', "shoes"]
    homeware = ["home", "homeware"]
    tops = ["top", "tops"]
    bottoms = ["bottoms", "bottom","sweetlegs"]
    main_cat = ''
    sub_cat = []
    
    res = []
    
    # Get rid of "bikini top and bikini bottoms" from tops and bottoms, 
    # because they belong to swimwear.
    other_clothing_sensative_words = ["bikini", "swim", "swimwear", "tankini"]
    is_other_clothing = False
    sub = []
    for e in ori_list:
        e = e.strip().lower()
        if e in removable_words:
            continue
        elif not res.__contains__(e):
            res.append(e)
        if e in acc:
            main_cat = "accessories"
        elif e in shoes:
            main_cat = "shoes"
        elif e in tops:
            main_cat = "tops"
        elif e in bottoms:
            main_cat = "bottoms"
        elif e in homeware:
            main_cat = "homeware"
        elif e == "beauty":
            main_cat = "beauty"
        elif e in other_clothing_sensative_words :
            is_other_clothing = True
            if e not in sub_cat:
                sub_cat.append(e)
        else:
            #the rest of string can be added to sub_category
            if e not in sub_cat:
                sub_cat.append(e)
        if is_other_clothing:
            if main_cat != '' and main_cat != 'other_clothing':
                sub_cat.append(main_cat)
            main_cat = "other_clothing"
    #if main_cat doesn't exist but sub_cat exists, we can try to map directly by specific_product_map
    
    sub_cat = " ".join(sub_cat)
    sub_cat = lemma_string(sub_cat)
    return " ".join(res), main_cat, sub_cat

def initiailize_containers() -> None:
    '''
    Input: None
    Function: Read the .json file to initilize the dictionaries and sets
    Output: None
    '''
    with open("json_files/product_to_all.json") as f1:
        global products_to_all 
        products_to_all = json.load(f1)
    with open("json_files/main_categories_to_num.json") as f2: 
        global main_categories_map_to_num
        main_categories_map_to_num = json.load(f2)
    with open("json_files/specific_product_map_to_num.json") as f3:
        global specific_products_map_to_num
        specific_products_map_to_num = json.load(f3)
    for key in specific_products_map_to_num.keys():
        all_cat.add(key)
    with open("json_files/label3_to_label2.json") as f4:
        global label3_to_label2_map
        label3_to_label2_map = json.load(f4)
    with open("json_files/colorsname_to_hex.json") as f5:
        global colorname_to_hex_map
        colorname_to_hex_map = json.load(f5)

def summary_of_the_new_df(df:pd.DataFrame)->None:
    '''
    Input: dataframe
    Function: to calculate some statistics data after pre-processing.
    '''
    unknown = 0
    totalnum = df.shape[0]
    shoes = 0
    other_clothing = 0
    tops = 0
    bottoms = 0
    beauty = 0
    home = 0
    acc = 0
    other = 0
    label2_count = 0
    for row in range(df.shape[0]):
        n = df.loc[row, "label_1st"]
        if n == 0:
            unknown += 1
        elif n == 1:
            shoes += 1
        elif n == 2:
            tops += 1
        elif n == 3:
            bottoms += 1
        elif n == 4:
            other_clothing += 1
        elif n == 5:
            beauty += 1
        elif n == 6:
            acc += 1
        elif n == 7:
            home += 1
        elif n == 8:
            other += 1
        m = df.loc[row]["label_2nd"]
        if m != "" :
            label2_count += 1
        
    print("unknown", unknown, "\t\tratio of all", unknown/totalnum)
    total = totalnum - unknown
    print("lable_2 ", label2_count, "\t\tratio", "{:10.2f}".format(label2_count/total) )
    print("\nshoes", shoes,"\t\tratio", "{:10.2f}".format(shoes/total))
    print("tops", tops, "\t\tratio", "{:10.2f}".format(tops/total))
    print("bottoms", bottoms, "\t\tratio", "{:10.2f}".format(bottoms/total))
    print("other_clothing", other_clothing,"\tratio", "{:10.2f}".format(other_clothing/total))
    print("beauty", beauty, "\t\tratio", "{:10.2f}".format(beauty/total))
    print("accessories", acc, "\tratio", "{:10.2f}".format(acc/total))
    print("homeware", home, "\t\tratio", "{:10.2f}".format(home/total))
    print("other", other, "\t\tratio", "{:10.2f}".format(other/total))

def restruct_dataset(file_path:str) -> pd.DataFrame:
    original_file_path = file_path
    assert original_file_path != None
    columns = ["id", "title", "tags", "images", "gender","product_type",  "colors", "buckets", "url", "body_html"]
    df = pd.DataFrame()
    try:
        df = pd.read_csv(original_file_path, usecols=columns).reset_index()
    except:
        print("The path seems incorrect")
    #insert new columns to this df which are useful and processed information 

    df.insert(df.columns.get_loc("gender"), "product_type(modified)", "", allow_duplicates=True)
    df.insert(df.columns.get_loc("gender"), "main_category", "", allow_duplicates=True)
    df.insert(df.columns.get_loc("gender"), "sub_category", "", allow_duplicates=True)
    df.insert(df.columns.get_loc("gender"), "match_most_similar_>80%_string", "", allow_duplicates=True)
    df.insert(df.columns.get_loc("gender"), "match_most_similar_>60%_string", "", allow_duplicates=True)
    df.insert(df.columns.get_loc("gender"), "label_1st", 0, allow_duplicates=True)
    df.insert(df.columns.get_loc("gender"), "label_2nd", "", allow_duplicates=True)
    df.insert(df.columns.get_loc("gender"), "label_3rd", "", allow_duplicates=True)
    df.insert(df.columns.get_loc("buckets"), "buckets_num", 0, allow_duplicates=True)
    df.insert(df.columns.get_loc("url"), "color_num", 0, allow_duplicates=True)
    df.insert(df.columns.get_loc("colors"), "color_info", "", allow_duplicates=True)
    df.insert(df.columns.get_loc("colors"), "pattern_info", "", allow_duplicates=True)
    df = df[["index","id", "title", "tags", "images", "gender","product_type", "product_type(modified)", \
        "main_category", "sub_category", "match_most_similar_>80%_string", "match_most_similar_>60%_string", \
        "label_1st", "label_2nd","label_3rd", "buckets_num", "buckets", "pattern_info","color_num", \
        "color_info", "colors", "url", "body_html"]]
    df.insert(df.columns.get_loc("body_html"), "raw_text", "", allow_duplicates=True)
    for i in range(df.shape[0]):
        
        ori_word = df.loc[i, 'product_type']
        title = df.loc[i, 'title']
        tags = df.loc[i, 'tags']
        buckets = df.loc[i, 'buckets']
        body_html = df.loc[i, 'body_html']
        
        if not isinstance(ori_word, str):
            df.loc[i,['product_type']] = "unknown"
            df.loc[i, ['product_type(modified)']] = "unknown"
            continue
        #get the modify_product_type (remove)
        try:
            product_type_new, main_cat, sub_cat= modify_product_type(ori_word)
            df.loc[i, ['product_type(modified)']] = product_type_new
            df.loc[i, ["main_category"]] = main_cat
            df.loc[i, ["sub_category"]] = sub_cat
            
            if (main_cat != ""):
                #label the 1st, label if we already know exact main_catgories. 
                df.loc[i,"label_1st"] = main_categories_map_to_num.get(main_cat)
        except:
            print(i, ori_word)
        try:
            #clean body_html as well. 
            if pd.isna(body_html):
                continue
            df.loc[i, 'raw_text'] = tc.cleanHtml(body_html)
        except:
            print("Something wrong with clean html: ", i)
    del(df["body_html"])
    return df
    
def match_process(df:pd.DataFrame):
    
    #build data series from all categories.
    pre_defiened_labels = pd.Series(list(all_cat), name="pre_defined_label")
    #get 80% most_similar_mathes(dataframe) by using package string-matcher
    most_similar_matches = match_most_similar( pre_defiened_labels, df["sub_category"],\
        min_similarity = 0.80, ignore_index=False, replace_na=False)
    most_similar_matches = pd.concat([df['index'],df["sub_category"], most_similar_matches], axis=1)
    #get 60% most_similar_matches(dataframe) 
    less_similar_matches = match_strings(pre_defiened_labels, df["sub_category"],\
        min_similarity = 0.65, ignore_index = False, replace_na = False)
    #fill up 80% most_similar_80% column
    empty_cells = 0
    for row in range(most_similar_matches.shape[0]):
        index = most_similar_matches.loc[row, "index"]
        most_similar_pre_defined_label = most_similar_matches.loc[row, 'most_similar_pre_defined_label']
        most_similar_index = most_similar_matches.loc[row]['most_similar_index']
        
        if not np.isnan(most_similar_index):
            df.loc[df['index'] == index, ['match_most_similar_>80%_string']] = most_similar_pre_defined_label
        else:
            empty_cells += 1
    #fill up 60% less_similar_60% column
    index_similarity_map = {}
    index_to_pre_map = {}
    for row in range(less_similar_matches.shape[0]):
        current_index = less_similar_matches.loc[row, 'right_index']
        label = less_similar_matches.loc[row, 'left_pre_defined_label']
        similarity = less_similar_matches.loc[row, 'similarity']
        
        if index_similarity_map.get(current_index) == None:
            index_similarity_map.update({current_index:similarity})
            index_to_pre_map.update({current_index:label})
        elif index_similarity_map.get(current_index) >= similarity:
            index_similarity_map.update({current_index:similarity})
            index_to_pre_map.update({current_index:label})
        else: # similarity < then current, ignore
            continue
    for key in index_to_pre_map.keys():
        df.loc[df['index'] == key, ['match_most_similar_>60%_string']] = index_to_pre_map.get(key)
    
    
    #Algorithm 2: if both 60% and 80% don't exist, just ignore, 
    #             if the 80% string doesn't exist, compare the 60% string with 80% string similarity by diff() and spacy(), 
    #             let spacy.similarity to decide whether above 60% to fill the 80%. if spacy similarity does not exist, fill 
    #             fill up 80% by similar() algorithm. 
    #     speed : 500 data around 1 mins based on M1 pro.
    double_check_pairs_pt_word60_dic = {}
    #see the accurancy 

    def is_nan_string(string):
        return string == ""
    
    for row in range(df.shape[0]):
        word_80 = df.loc[row]["match_most_similar_>80%_string"]
        word_60 = df.loc[row]["match_most_similar_>60%_string"]
        #print(is_nan_string(word_80), "   ",word_60)
        if is_nan_string(word_80) and is_nan_string(word_60):
            #found nothing
            continue    
        elif is_nan_string(word_80) and not is_nan_string(word_60):
            pt_modified = df.loc[row]["sub_category"]
            pair = (pt_modified, word_60)
            #print(pair)
            if pair not in double_check_pairs_pt_word60_dic.keys():
                
                double_check_pairs_pt_word60_dic.update({pair: similar(word_60, pt_modified)})
            #print("product_type(modified) ", pt_modified, " words(60%): ", word_60, " Similarity: ", similar(word_60, pt_modified))
            if similar(word_60, pt_modified) > 0.14:
                df.loc[row, "match_most_similar_>80%_string"] = word_60
    double_check_pairs_pt_word60_dic = dict(sorted(double_check_pairs_pt_word60_dic.items(), key=lambda item: item[1]))
    print(double_check_pairs_pt_word60_dic)
    # Algorithm 3(Optional): If both 80 60 are empty but the sub cat has the entry
    # We can map mannually the item to our match_most_similar_>80%_string
    for row in range(df.shape[0]):
        #if not pd.isna((df.loc[row]["match_most_similar_>80%_string"])) or not pd.isna((df.loc[row]["match_most_similar_>60%_string"])):
            #continue
        sub_category = df.loc[row]["sub_category"]
        if not isinstance(sub_category, str) :
            continue
        elif sub_category.__contains__("bag"):
            df.loc[row, "match_most_similar_>80%_string"] = "bag"
        elif sub_category.__contains__("glove"):
            df.loc[row, "match_most_similar_>80%_string"] = "glove"
        elif sub_category.__contains__("sunglasses") or sub_category.__contains__("polar"):
            df.loc[row, "match_most_similar_>80%_string"] = "sunglasses"
            
    for row in range(df.shape[0]):
        key = df.loc[row]['match_most_similar_>80%_string']
        if key != None and specific_products_map_to_num.get(key) != None:
            df.loc[row, 'label_1st'] = specific_products_map_to_num.get(key)
        if key != None and label3_to_label2_map.get(key) != None:
            df.loc[row, "label_2nd"] = label3_to_label2_map.get(key)
    
    reset_colors_format(df)
    print("Working on color_name query -- %s seconds " % (time.time() - start_time))
    requery_color_name(df)
    print("Working on color_name match query -- %s seconds " % (time.time() - start_time))
    colour_mapping(df)
    
    summary_of_the_new_df(df)
    return df
    
def assign_label3(str):
    if pd.isna(str):
        return ""
    else:
        str = " ".join([s.capitalize() for s in str.split(" ")])
        return str

def main():
    #iniyilize all maps and sets.
    initiailize_containers()
    
    file_path = "products-June-28th.csv"
    #df = pd.read_csv(file_path)
    print("Working on restruct_dataset -- %s seconds " % (time.time() - start_time))
    df = restruct_dataset(file_path)
    #df = parallelize_dataframe(df, match_process, mp.cpu_count())
    print("Working on match_process -- %s seconds " % (time.time() - start_time))
    new_df = match_process(df)
    new_df['label_3rd'] = new_df['match_most_similar_>80%_string'].parallel_apply(assign_label3)
    
    new_df.to_csv("processed_dataset.csv", index=False)
    
main()
print("%s seconds " % (time.time() - start_time))
    
    