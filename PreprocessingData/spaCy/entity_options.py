import random 

def get_entity_options(random_colors=False):
    """ generating color options for visualizing the named entities """

    def color_generator(number_of_colors):
        color = ["#"+''.join([random.choice('0123456789ABCDEF') for j in range(6)]) for i in range(number_of_colors)]
        return color

    entities = ["TOPS", "BOTTOMS", "OTHER_CLOTHING", "HOMEWARE", "ACCESSORIES", "SHOES", "BEAUTY"]

    colors = {"ENT":"#E8DAEF"}

    if random_colors:
        color = color_generator(len(entities))
        for i in range(len(entities)):
            colors[entities[i]] = color[i]
    else:
        entities_cat_1 = {"TOPS":"#F9E79F", "BOTTOMS":"#76D7C4", "OTHER_CLOTHING":"#E8DAEF"}
        entities_cat_2 = {"SHOES":"#82E0AA"}#, "CELL_TYPE":"#AED6F1", "CELL_LINE":"#E8DAEF", "RNA":"#82E0AA", "PROTEIN":"#82E0AA"}
        entities_cat_3 = {"HOMEWARE":"#D7BDE2"}#, "CHEMICAL":"#D2B4DE"}
        entities_cat_4 = {"BEAUTY":"#ABEBC6"}#, "ORGAN":"#82E0AA", "TISSUE":"#A9DFBF", "ORGANISM":"#A2D9CE", "CELL":"#76D7C4"}
        

        entities_cats = [entities_cat_1, entities_cat_2, entities_cat_3, entities_cat_4]
        for item in entities_cats:
            colors = {**colors, **item}

    options = {"ents": entities, "colors": colors}
    # print(options)
    return options