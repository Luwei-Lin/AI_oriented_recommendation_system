from product import Product


def getColors(prediction_color: list):
    print(type(prediction_color))
    o = []
    for i in prediction_color:
        i = i.title()
        o.append(i)
    o = list(dict.fromkeys(o))
    # o = o[0:5]
    # print(o)
    return o


def getjson(product= Product):
    colors = product.get_accurate_colour()
    type = product.get_accurate_type()
    pattern = product.get_pattern()
    size = product.get_size()
    gender = product.get_gender()


    return_json = {
        "colors": colors,
        "type": type,
        "pattern": pattern,
        "size": size,
        "gender": gender
    }

    return return_json