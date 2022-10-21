from unittest.util import sorted_list_difference
from Labels import Labels
from ImageClassifier import ImageClassifier
from convert_color import colordetectionprocess, num2color
from rembg import remove
from TextClassfierWithNER import auto_detect
from product import Product
import json 
import spacy

def return_labels(image_path="", product_desciption="", product_title="") -> Product:
    #assert isinstance(image_path, str), "the image_path should be str type"
    IC = ImageClassifier()
    IC.load_ML_model("./TrainedModels/ICModels/SH_model08_21.pkl")

    input_path = image_path
    bg_removed_path = "bg_removed/"+input_path.split('/')[-1]
    name = input_path.split('/')[-1] # image name
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
        product.set_accurate_colour(set(num2color(color_num).append(NLP_color))) # num2color returns a list, for example:['Green', 'Green', 'Black', 'Purple', 'Green']
    else:
        product.set_accurate_colour(set(num2color(color_num)))
    
    image_product_type, confidence = IC.predict(input_path)

    ##############Combine type by nlp and IC Section##############
    final_product_type = ""
    try:
        if product.get_potential_types != "":
            ##################Get Only One Product Type From NLP#################################
            nlp_result = ""
            potenial_type = product.get_potential_types().split(',')
            #if there is only result of nlp
            if len(potenial_type) == 1: 
                nlp_result = potenial_type[0]
            #if there is overlap like bag: 3 times pick highest frequeny item
            else:
                nlp_result = ""
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
                    nlp_result = potenial_type[0]
                else:
                    sorted_compare_list_from_dict = list(sorted_compare_dict)
                    nlp_result = sorted_compare_list_from_dict[0]
            ################## After One Product Type From NLP#################################
            f = open("./json_files/label3_to_label2.json")
            label3_to_label2 = json.load(f)
            label3_to_label2:dict
            nlp = spacy.load("en_core_web_lg")
            temp_nlp_label2 = nlp_result
            nlp_label2 = ""
            if temp_nlp_label2 in label3_to_label2.keys():# if nlp_result is third layer label
                nlp_label2 =label3_to_label2.get(nlp_result)
            else:
                nlp_label2 = temp_nlp_label2 #if nlp_result is neither 2nd or 3rd label
            ################ Compare With the image product type##############################
            if nlp_label2 == image_product_type:
                final_product_type = image_product_type
            elif nlp(nlp_label2).simlarity(nlp(image_product_type)) > 0.85 and float(confidence) > 0.80: 
                final_product_type = image_product_type
            else:
                final_product_type = "unknown_1"
            #############################################################################################
        elif float(confidence) > 0.9:
            final_product_type = image_product_type 
        else: # nlp doesn't have results as well:
            final_product_type = "unknown_2"
    except:
        final_product_type = "unknown_3"# for the program logic errors

    product.set_accurate_type(final_product_type)

    # l.type, confidence=IC.predict(input_path)
    # l.size="L"
    product.info()

    return product

label = return_labels()

def test():
    path =input("Please enter the image path: ")
    product_title = input("Enter the product title: ")
    product_desciption = input("Enter the product descption:")
    return_labels(path, product_title, product_desciption)

test()

