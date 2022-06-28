#################################################################
# This script is for generating training dataset from 
# original .csv file by standardizing product_type and 
# labelling the first class label by algorithms.
#
# Please make sure the input file path and type is correct
# Also, make sure product_to_all.json and main_to_num.json
# in the same directory(or same path.) Since these two files
# are the standardize information we use and the product label 
# map to number we predefined.
# 
# Author: Luis Lin
# Date: June 27, 2022
#################################################################
import json
import spacy 
from difflib import SequenceMatcher
from typing import List
import pandas as pd
from string_grouper import match_strings, match_most_similar
import numpy as np

#the main_categories with all sub_categories dict
products_to_all = {}
#the main_categories relate to numbers dict
main_categories_map_to_num = {}
#all categories of product including the name of main_cat
all_cat = set()
#each specific item maps to the main_categories_number
specific_products_map_to_num = {}

'''
Input: two separate strings
Function:
    We provide another statistic model (ML) from spacy.similarity to compare two strings similarity firstly.
    if spacy similarities doesn't not exit like 0.0, then we compare two strings similarity by "gestalt pattern matching" 
    not_Statistic model(ML)  It is a character-based matcher. 
Output: Similarity [0, 1] between those two strings
'''
def similar(a: str, b: str) -> float:
    nlp = spacy.load("en_core_web_md")
    doc1 = nlp(a)
    doc2 = nlp(b)
    statistical_method_score = doc1.similarity(doc2)
    non_statistical_method_score = SequenceMatcher(None, a, b).ratio()
    if statistical_method_score < 0.1:
        return non_statistical_method_score
    return statistical_method_score

'''
input: original string
function: remove pre_suffix of the original 'product_type' to match more accurate items
output: modified string
'''
def modify_product_type(original:str)-> str:
    removable_words = ["mens", "womens", "girls", "ladies", "boys", "graphic", "premium", "cozy", "comfort", "casual", 'adult']
    ori_list = original.split(" ")
    res = []
    for e in ori_list:
        if e.lower() in removable_words:
            continue
        else:
            res.append(e.lower())
    return " ".join(res)

'''
Input: None
Function: Read the .json file to initilize the dictionaries and sets
Output: None
'''
def initiailize_containers() -> None:
    with open("product_to_all.json", "r") as outfile:
        products_to_all = json.load(outfile)
    with open("main_categories_to_num", "r") as outfile2:
        main_categories_map_to_num = json.load(outfile2)
    
    for key in products_to_all.keys():
        all_cat.add(key)
        map_number_of_this_key = main_categories_map_to_num.get(key)
        assert products_to_all.get(key) is not None
        specific_products_map_to_num.update({key: map_number_of_this_key})
        for item in products_to_all.get(key):
            all_cat.add(key)
            specific_products_map_to_num.update({item: map_number_of_this_key})
'''
Input: dataframe
Function: to calculate some statistics data after pre-processing.
'''
def summary_of_the_new_df(df:pd.DataFrame)->None:
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
    for row in range(df.shape[0]):
        n = df.loc[row, ["label_1st"]].item()
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
        
    print("unknown", unknown, "\t\tratio of all", unknown/totalnum)
    total = totalnum - unknown
    print("\nshoes", shoes,"\t\tratio", "{:10.2f}".format(shoes/total))
    print("tops", tops, "\t\tratio", "{:10.2f}".format(tops/total))
    print("bottoms", bottoms, "\t\tratio", "{:10.2f}".format(bottoms/total))
    print("other_clothing", other_clothing,"\tratio", "{:10.2f}".format(other_clothing/total))
    print("beauty", beauty, "\t\tratio", "{:10.2f}".format(beauty/total))
    print("accessories", acc, "\tratio", "{:10.2f}".format(acc/total))
    print("homeware", home, "\t\tratio", "{:10.2f}".format(home/total))
    print("other", other, "\t\tratio", "{:10.2f}".format(other/total))
'''
input: original .csv file path(str)
function: deal with original .csv file and create customized .csv 
        in current directory
output: the labelled .csv file and unknown product_type .csv file
'''
def generate_newcsv(original_file_path:str) -> None:
    assert original_file_path != None
    columns = ["id", "title", "tags", "images", "product_type", "gender", "buckets", "url", "body_html"]
    df = pd.DataFrame()
    try:
        df = pd.read_csv(original_file_path, usecols=columns).reset_index()
    except:
        print("The path seems incorrect")
    #insert new columns to this df which are useful and processed information 

    df.insert(df.columns.get_loc("gender"), "product_type(modified)", "", allow_duplicates=True)
    df.insert(df.columns.get_loc("gender"), "match_most_similar_>80%_string", "", allow_duplicates=True)
    df.insert(df.columns.get_loc("gender"), "match_most_similar_>60%_string", "", allow_duplicates=True)
    df.insert(df.columns.get_loc("gender"), "label_1st", 0, allow_duplicates=True)
    df.insert(df.columns.get_loc("gender"), "label_2nd", 0, allow_duplicates=True)
    df.insert(df.columns.get_loc("gender"), "label_3rd", 0, allow_duplicates=True)
    df.insert(df.columns.get_loc("buckets"), "buckets_num", 0, allow_duplicates=True)
    df.insert(df.columns.get_loc("url"), "color", 0, allow_duplicates=True)
    
    #modified the original product_type
    for i in range(df.shape[0]):
        ori_word = df.loc[i, ['product_type']].item()
        try:
            df.loc[i, ['product_type(modified)']] = modify_product_type(ori_word)
        except:
            print(modify_product_type(ori_word))
    #build data series from all categories.
    pre_defiened_labels = pd.Series(list(all_cat), name="pre_defined_label")
    #get 80% most_similar_mathes(dataframe) by using package string-matcher
    
    most_similar_matches = match_most_similar( pre_defiened_labels, df["product_type(modified)"],\
        min_similarity = 0.80, ignore_index=False, replace_na=False)
    most_similar_matches = pd.concat([df['index'],df["product_type(modified)"], most_similar_matches], axis=1)
    #get 60% most_similar_matches(dataframe) 
    less_similar_matches = match_strings(pre_defiened_labels, df["product_type(modified)"],\
        min_similarity = 0.65, ignore_index = False, replace_na = False)
    #fill up 80% most_similar_80% column
    empty_cells = 0
    for row in range(most_similar_matches.shape[0]):
        index = most_similar_matches.loc[row, "index"]
        most_similar_pre_defined_label = most_similar_matches.loc[row, 'most_similar_pre_defined_label']
        most_similar_index = most_similar_matches.loc[row, ['most_similar_index']].item()
        
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
        df.loc[df['index'] == key, ['match_string_>60%_similarity']] = index_to_pre_map.get(key)
    
    #Algorithm 2: if both 60% and 80% don't exist, just ignore, 
    #             if the 80% string doesn't exist, compare the 60% string with 80% string similarity by diff() and spacy(), 
    #             let spacy.similarity to decide whether above 60% to fill the 80%. if spacy similarity does not exist, fill 
    #             fill up 80% by similar() algorithm. 
    double_check_pairs_pt_word60_dic = {}
    #see the accurancy 

    def is_nan_string(string):
        return string != string
    #w = df.loc[66, ["match_most_similar_>80%_string"]].item()
    #print(w)
    #is_nan_string(w)
    for row in range(df.shape[0]):
        word_80 = df.loc[row, ["match_most_similar_>80%_string"]].item()
        word_60 = df.loc[row, ["match_most_similar_>60%_string"]].item()
        
        if is_nan_string(word_80 ) and is_nan_string(word_60):
            continue
        elif is_nan_string(word_80) and not is_nan_string(word_60):
            pt_modified = df.loc[row, 'product_type(modified)']
            pair = (pt_modified, word_60)
            
            if pair not in double_check_pairs_pt_word60_dic.keys():
                double_check_pairs_pt_word60_dic.update({pair: similar(word_60, pt_modified)})
                
            #print("product_type(modified) ", pt_modified, " words(60%): ", word_60, " Similarity: ", similar(word_60, pt_modified))
            if similar(word_60, pt_modified) > 0.5:
                df.loc[row, "match_most_similar_>80%_string"] = word_60
                
    #From previous we finished match similar products. We start to label the "label_1st" column
    for row in range(df.shape[0]):
        key = df.loc[row, ['match_most_similar_>80%_string']].item()
        if key != None and specific_products_map_to_num.get(key) != None:
            df.loc[row, ['1st_class_label']] = specific_products_map_to_num.get(key)
        else:
            df.loc[row, ['1st_class_label']] = 0
        
    #Last Check if some of the unknown item in the match_most_similar_>80%_string belongs to main_categories
    for row in range(df.shape[0]):
        key = df.loc[row, ["match_most_similar_>80%_string"]].item()
        if df.loc[row, ['1st_class_label']].item() == 0 and not is_nan_string(key):
            df.loc[row, ['1st_class_label']] = main_categories_map_to_num.get(key)
    
    k = df.loc[df.label_1st == 0].index
    drop_df = df.loc[df["label_1st"] == 0].copy().to_csv("unlabelled_products.csv", index=False)
    df = df.drop(k)
    df.to_csv("labelled_products.csv", index=False)
    
def main():
    file_path = "/Users/luis/Downloads/products_June24.csv"
    assert open(file_path)
    try:
        generate_newcsv(file_path)
    except:
        print("something wrong.")
main()