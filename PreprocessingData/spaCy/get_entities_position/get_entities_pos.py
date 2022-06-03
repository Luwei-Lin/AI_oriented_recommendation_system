import spacy
import spacy

'''
Input: String

Function: get the position of the entities from rule_based_matcher model.

output: all entities with char postion
'''

def get_postion(text):
    nlp_rule = spacy.load("rule_model_7Categories")
    doc = nlp_rule(text)
    res = []
    for ent in doc.ents:
        temp = [(ent.start_char, ent.end_char), ent.label_, ent]
        res.append(temp)
    print(res)

def main():
    text = " the tempo hoodie TOPS tops is the upf 50+ activewear OTHER_CLOTHING youve been looking for! it has thumbholes, a kangaroo pocket, and a hood for when the sun is too hot or you forgot your hat. our fitness hoodie TOPS tops TOPS is made out of our active athlon fabric with the added bonus of our cooltect™ technology. you can be active in this fitted fitness hoodie TOPS tops TOPS without getting uncomfortably hot. so go ahead and enjoy sun-safe biking, walking, running and so much more!highlights:upf 50+raglan long sleeves with thumbholeswelt kangaroo pockethoodedactive athlon™ fabric: lightweight and breathable with moisture wicking for quick dry performancecooltect™ technology accelerates moisture wicking to keep you cooler and more comfortable"
    get_postion(text)

#main()
'''
output: (char position start index, end index), 'label', 'word')
[[(11, 17), 'TOPS', 'hoodie'], [(23, 27), 'TOPS', 'top'], [(43, 53), 'OTHER_CLOTHING', 'activewear'], [(206, 212), 'TOPS', 'hoodie'], [(218, 222), 'TOPS', 'top'], [(359, 365), 'TOPS', 'hoodie'], [(371, 375), 'TOPS', 'top']]
'''

    
    