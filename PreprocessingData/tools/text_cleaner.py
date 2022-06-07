import re
import lxml.html.clean
'''
Input: (String)  title, product_type, tags 
Output: (String) String concating title, product_type and tags. 
'''
def clean_tags_text(raw_title, raw_product_type, raw_tags):
    tags = ''
    title = ''
    product_type = ''
    if isinstance(raw_tags, str) and raw_tags is not None:
        tags = re.sub("-", " ", re.sub("'", " ",re.sub(",", " ", raw_tags)))
        #tags = raw_tags.lower()
    if isinstance(raw_title, str)and raw_title is not None:
        title = re.sub("'", " ", re.sub("-", " ", re.sub(",", "", raw_title)))
        #title = raw_title.lower()
    if isinstance(raw_product_type, str) and raw_product_type is not None :
        product_type = re.sub(",", " ", raw_product_type)
    
    reg_str = '{(.*?)}'
    tags = re.sub('"', "", tags)#remove inside the sentence " signs for cleaning data
    
    contents = title
    #edge case: there is no any words in the title 
    if contents == "": 
        contents = 'NOTITLE'
    #tags string 
    tags_toString = str(re.findall(reg_str, tags)).removeprefix('[').removesuffix(']')
    tags_toString = re.sub("'", "", re.sub('"', ' ', tags_toString))
    
    contents += '; ' + product_type
    
    if product_type != "":
        contents += '; ' + tags_toString
    else:
        contents += tags_toString
        
    return contents

'''
Clean the html with regex.
Input: raw html String
Output: After processing body_html String 

'''
def cleanHtml(html):
    res = lxml.html.clean.clean_html(html)
    res = re.sub(re.compile('<.*?>'), '', html)
    cleantext = re.sub("\n", "", res)
    cleantext = re.sub("¬†", " ", res)
    return cleantext

'''
After cleanHtml() to do one more cleaning for product description. 
'''
def clean_product_description(raw_product_description):
    #remove all ' or " 
    product_description = raw_product_description
    contents = re.sub('"', "", product_description)
    contents = re.sub("'", "", contents)
    contents = re.sub("\n", "", contents)
    contents = re.sub('&amp;', 'and', contents)
    return contents



'''
Directly use the information from csv cells in ['title', 'tags', 'body_html']
return pre-processing raw_text
'''
def raw_content(title, tags, body_html):
    
    text_1 = clean_tags_text(title, None, tags)
    text_2 = clean_product_description(cleanHtml(body_html))

    raw_text = text_1 + '. ' + text_2
    return raw_text

def test():
    title = "Aria High Waist"
    tags = "{d-cup+,meta-size-chart-artesands-size-guide,moderate-coverage,one-piece,plus-size,swim-wear}"
    body_html = '"<meta charset="utf-8"><p><meta charset="utf-8"><span>The Hues Underwire One Piece has a beautifully sculpted feminine wrap-around style. The Hue has a hidden shelf bra with internal support underwire to fit a D cup to DD cup. This swimsuit style allows all of the fit and support required for body sculpting and figure forming confidence for the curvy body. </span></p><p data-mce-fragment="1"><meta charset="utf-8"><em data-mce-fragment="1">Model is wearing an Australian size 18+ </em></p><p class="p1" data-mce-fragment="1"><b data-mce-fragment="1">FEATURES:</b></p><ul class="ul1" data-mce-fragment="1"><li class="li1" data-mce-fragment="1">Supportive Underwire  <br data-mce-fragment="1"></li><li class="li1" data-mce-fragment="1">Removable &amp; Adjustable Straps  </li><li class="li1" data-mce-fragment="1">Front Ruching <br data-mce-fragment="1"></li><li class="li1" data-mce-fragment="1">D/DD Cup Underwire Support <br data-mce-fragment="1"></li><li class="li1" data-mce-fragment="1"> <div data-mce-fragment="1">Nylon / Elastane Blend. </div></li></ul><div class="p2" style="text-align: center;" data-mce-style="text-align: center;" data-mce-fragment="1"><b data-mce-fragment="1"><span data-mce-fragment="1">Artesands Fits Your Curves. Designed in Australia. </span></b></div><h5 style="text-align: left;" data-mce-fragment="1"><strong>Care Notes</strong></h5><p><strong></strong>We recommend hand washing in cold water. Dry flat in a shady spot out of direct sunlight. Do not wring out or hang dry. </p><p>Chlorinated water is not great and can cause colours to fade. Please make sure you always wash your swimsuit well after swimming in chlorinated water. We recommend swimsuit cleaner to keep your swimsuit looking amazing.</p>"'
    print(raw_content(title, tags, body_html))

test()

'''
When you use the test() which used the raw_content() only. You can directly use the  
Output:Aria High Waist; d cup+ meta size chart artesands size guide moderate coverage one piece plus size swim wear. The Hues Underwire One Piece has a beautifully sculpted feminine wrap-around style. The Hue has a hidden shelf bra with internal support underwire to fit a D cup to DD cup. This swimsuit style allows all of the fit and support required for body sculpting and figure forming confidence for the curvy body. Model is wearing an Australian size 18+ FEATURES:Supportive Underwire  Removable and; Adjustable Straps  Front Ruching D/DD Cup Underwire Support  Nylon / Elastane Blend. Artesands Fits Your Curves. Designed in Australia. Care NotesWe recommend hand washing in cold water. Dry flat in a shady spot out of direct sunlight. Do not wring out or hang dry. Chlorinated water is not great and can cause colours to fade. Please make sure you always wash your swimsuit well after swimming in chlorinated water. We recommend swimsuit cleaner to keep your swimsuit looking amazing.


'''