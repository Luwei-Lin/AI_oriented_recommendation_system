import random 

def get_entity_options(random_colors=False):
    """ generating color options for visualizing the named entities """

    def color_generator(number_of_colors):
        color = ["#"+''.join([random.choice('0123456789ABCDEF') for j in range(6)]) for i in range(number_of_colors)]
        return color

    entities = ["TOPS", "BOTTOMS", "OTHER_CLOTHING", "HOMEWARE", "ACCESSORIES", "SHOES", "BEAUTY",\
        "GENDER", "SIZE","COLOR","PATTERN"]

    colors = {"ENT":"#E8DAEF"}

    if random_colors:
        color = color_generator(len(entities))
        for i in range(len(entities)):
            colors[entities[i]] = color[i]
    else:
        entities_cat_1 = {"TOPS":"#F9E79F"}#, "BOTTOMS":"# "OTHER_CLOTHING":"#E8DAEF"}
        entities_cat_2 = {"SHOES":"#82E0AA"}#, "CELL_TYPE":"", "CELL_LINE":"#E8DAEF", "RNA":, "PROTEIN":}
        entities_cat_3 = {"HOMEWARE":"#D7BDE2"}#, "CHEMICAL":""}
        entities_cat_4 = {"BEAUTY":"#ABEBC6"}#, "ORGAN":"", "TISSUE":"", "ORGANISM":"", "CELL":}
        entities_cat_5 = {"OTHER_CLOTHING":"#DAF7A6"}
        entities_cat_6 = {"OTHER":"#A9DFBF"}
        entities_cat_7 = {"BOTTOMS":"#A2D9CE"}
        entities_cat_8 = {"ACCESSORIES": "#D2B4DE"}
        
        entities_cat_9 = {"GENDER": "#76D7C4"}
        entities_cat_10 = {"SIZE": "#581845"}
        entities_cat_11 = {"COLOR": "#AED6F1"}
        entities_cat_12 = {"PATTERN":"#C70039"}
        

        entities_cats = [entities_cat_1, entities_cat_2, entities_cat_3, entities_cat_4,\
            entities_cat_5, entities_cat_6, entities_cat_7, entities_cat_8, entities_cat_9,\
            entities_cat_10, entities_cat_11, entities_cat_12]
        for item in entities_cats:
            colors = {**colors, **item}

    options = {"ents": entities, "colors": colors}
    # print(options)
    return options
