import csv
import os
from unittest.util import sorted_list_difference

import numpy as np
import spacy
import pandas as pd
from flask import jsonify
import sys

from Labels import Labels
from ImageClassifier import ImageClassifier
from convert_color import colordetectionprocess, num2color
from rembg import remove
from TextClassfierWithNER import auto_detect
from product import Product

def return_labels(image_path="", product_desciption="", product_id = '', product_title=""):
    #assert isinstance(image_path, str), "the image_path should be str type"
    IC = ImageClassifier()
    IC.load_ML_model("./TrainedModels/ICModels/SH_model08_21.pkl")

    input_path = image_path
    bg_removed_path = "bg_removed/" + input_path.split('/')[-1] # the path stored background removed images
    # bg_removed_path = "C:\\Users\\97902\\Desktop\\ShopHopper\\1007\\labels_generator_system-main\\labels_generator_system-main\\bg_test\\"+input_path.split('\\')[-1]
    name = input_path.split('\\')[-1] # image name
    try:
        with open(input_path, 'rb') as i:
            with open(bg_removed_path, 'wb') as o:
                input_img = i.read()
                output_img = remove(input_img)
                o.write(output_img)
    except:
        print("load IC_ML_model error.")
        pass
    product = auto_detect(product_description=product_desciption, product_title=product_title)
    try:
        NLP_color = product.get_potential_colour()
        # print("NLP color", NLP_color is None)
    except:
        print("NLP Error")

    #Hardcoding the values for now
    #these values will be later set by labels predicted by models
    color_num = colordetectionprocess(bg_removed_path, name)
    # product.set_accurate_colour(set(num2color(color_num)))

    if NLP_color != '':
        # in Windows OS
        temp = num2color(color_num)
        temp.append(NLP_color)
        product.set_accurate_colour(set(temp))  # num2color returns a list, for example:['Green', 'Green', 'Black', 'Purple', 'Green']

        # in macOS
        # product.set_accurate_colour(set(num2color(color_num).append(NLP_color))) # num2color returns a list, for example:['Green', 'Green', 'Black', 'Purple', 'Green']
    else:
        product.set_accurate_colour(set(num2color(color_num)))
    
    image_product_type, confidence = IC.predict(input_path)

    ##############Combine type by nlp and IC Section##############
    final_product_type = ""
    if float(confidence) > 0.90 :# 1. > 0 (only denpend on image)  type 2. > 60~70 type 3. > 80 4.> 99
        final_product_type = image_product_type
    else: #confidence < 0.8 and nlp has results
        try:
            if product.get_potential_types != "":
                potenial_type = product.get_potential_types().split(',')
                #if there is only result of nlp
                if len(potenial_type) == 1: 
                    final_product_type = potenial_type[0]
                #if there is overlap like bag: 3 times pick highest frequeny item
                else:
                    compare_dict = {}
                    for t in potenial_type:
                        t = t.strip()
                        compare_dict[t] = compare_dict.get(t, 1) + 1
                    #sort the dict from highest to lowest
                    sorted_compare_dict = dict(sorted(compare_dict.items(), key=lambda item: item[1], reverse=True))
                    #check the equality of the frequency
                    is_frequency_equal = True
                    for f in sorted_compare_dict.values():
                        if f > 1:
                            is_frequency_equal = False
                            break
                    if is_frequency_equal:
                        #if all frequency are the same return the first one(which usually is from title)
                        final_product_type = potenial_type[0]
                    else:
                        sorted_compare_list_from_dict = list(sorted_compare_dict)
                        final_product_type = sorted_compare_list_from_dict[0]
            #nlp doesn't have results as well:
            else:
                final_product_type = "unknown"
                try:
                    with open('unknown_and_ambiguous_product.csv', 'a', newline='') as csvfile:
                        w = csv.writer(csvfile, delimiter=',',quotechar=' ', quoting=csv.QUOTE_MINIMAL)
                        w.writerow([product_id, product_title, final_product_type, product_desciption])
                except:
                    #local unknown.csv file missing
                    pass
                
        except:
            final_product_type = "unknown_2"# for the program logic errors 
    product.set_accurate_type(final_product_type)

    # l.type, confidence=IC.predict(input_path)
    # l.size="L"
    product.info()
    import productToJson as pj
    data = jsonify(pj.getjson(product)) # convert Project class to JSON

    return data


sys.stdout.flush()

# label = return_labels()
#
# def test():
#     path =input("Please enter the image path: ")
#     product_title = input("Enter the product title: ")
#     product_desciption = input("Enter the product descption:")
#     # return_labels(path, product_title, product_desciption)

# test()
#
# if __name__ == "__main__":
#     return_labels()
#
# # test_images/4334154678372-4.jpg
# # Stella Dress, Spruce Twigs, Bamboo
# # Description The go-anywhere, fit-and-flare dress! Trim and forgiving in the bust, with an empire waist that sits just where it should. Refresh your winter with this easy to wear, and always flattering piece. It has a smooth fit, which makes layering a breeze. Pair with boots, scarves and our always cozy Wool Coats. (4H3) Features - Scoop neckline - Empire waist - Midi length Blue Sky fit guide - true to size. Fabric - 95% Bamboo, 5% Lycra Length Measurements, Top of Shoulder to Bottom of Hemline (cm) XXS XS S M L XL 1X 2X 3X 4X 112 112 112 114 114 116 116 118 118 118
