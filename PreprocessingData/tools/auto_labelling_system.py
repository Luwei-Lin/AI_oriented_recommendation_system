import pickle
import spacy

class Product:
    """
    An item with some attributes.
    """
    def __init__(self) -> None:
        pass
    def set_color(self, color_:set)-> None:
        self.color = color_
    def set_pattern(self, pattern_:set) -> None:
        self.pattern = pattern_
    def set_size(self, size_:set) -> None:
        self.size = size_
    def set_gender(self, gender_:str) -> None:
        self.gender = gender_
    def set_types(self, types:set):
        self.types = types
        
    def get_color(self)->str:
        return ",".join(self.color)
    def get_pattern(self)->str:
        return ",".join(self.pattern)
    def get_size(self)->str:
        return ",".join(self.size)
    def get_gender(self)->str:
        return self.gender
    def get_types(self)->str:
        return ",".join(self.types)
    def info(self):
        print("'colour': {color}\n'pattern': {pattern}\n'size': {size}\n'gender': {gender}\n'types':{types}"\
            .format(color=self.get_color(), pattern=self.get_pattern(), size=self.get_size(), gender=self.get_gender(), types=self.get_types()))
        
def auto_detect(text:str) -> Product:
    """ Auto detect the color, pattern, size, and gender of the product based on 
    product_description (text, narrative)
    
    Args:
        text (str): product description

    Returns:
        Product: new Product product with the attributes the model found.
    """
    p = Product()
    colours = set()
    patterns = set()
    sizes = set()
    gender = ""
    types = set()
    id_to_category = {   0: 'women',
        1: 'na',
        2: 'unisex',
        3: 'men',
        4: 'girls',
        5: 'boys',
        6: 'unisex/unknown'}
    #load spacy NER model
    stat_model_NER = spacy.load("./output_model/model-best")
    
    
    #from spacy to detect the certain entities.
    for ent in stat_model_NER(text).ents:
        if ent.label_ == "COLOR":
            colours.add(ent.text)
        elif ent.label_ == "SIZE":
            sizes.add(ent.text)
        elif ent.label_ == "PATTERN":
            patterns.add(ent.text)
        elif ent.label_ == "GENDER":
            continue
        else:
            types.add( ent.text)
    
    tfidf = pickle.load(open("vectorizer.pkl","rb"))
    # For the "gender", we do whole paragrah understanding by a trained text classifier 
    texts = [text]
    text_features = tfidf.transform(texts)
    with open("gender_detector_model.pkl", 'rb') as f:
        gender_detect_model = pickle.load(f)
    
    predictions = gender_detect_model.predict(text_features)
    
    
    for text, predicted in zip(texts, predictions):
        gender = id_to_category[predicted]
        

    p.set_color(colours)
    p.set_pattern(patterns)
    p.set_size(sizes)
    p.set_types(types)
    p.set_gender(gender)
    return p
def initilize_nlp_model(text:str):
    

def test():
    enter = input("Enter the text for detection ('q' for quit): ")
    while  enter != 'q':
        product = auto_detect(enter)
        product.info()
        enter = input("Enter the text for detection ('q' for quit): " )
