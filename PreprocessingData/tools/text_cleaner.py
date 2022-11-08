import re
from tkinter.messagebox import NO
import unicodedata


#from bs4 import BeautifulSoup
'''
Input: (String)  title, product_type, tags 
Output: (String) String concating title, product_type and tags. 
'''
def clean_tags_text(raw_title, raw_product_type, raw_tags, raw_buckets):
    tags = ''
    title = ''
    product_type = ''
    buckets = ''
    if isinstance(raw_tags, str) and raw_tags is not None:
        tags = re.sub("-", " ", re.sub("'", " ",re.sub(",", " ", raw_tags))).strip()
        #tags = raw_tags.lower()
    if isinstance(raw_title, str)and raw_title is not None:
        title = re.sub("'", " ", re.sub("-", " ", re.sub(",", "", raw_title))).strip()
        
        #title = raw_title.lower()
    if isinstance(raw_product_type, str) and raw_product_type is not None :
        product_type = re.sub(",", " ", raw_product_type)
    if isinstance(raw_buckets, str) and raw_buckets is not None:
        buckets = re.sub("{", "", re.sub("}", "", re.sub(",", ", ", raw_buckets))).strip()
    
    reg_str = r"{(.*?)}"
    tags = re.sub('"', "", tags)#remove inside the sentence " signs for cleaning data
    contents = title
    #edge case: there is no any words in the title 
    if contents == "": 
        contents = ''
    #tags string 
    tags_toString = str(re.findall(reg_str, tags)).removeprefix('[').removesuffix(']')
    tags_toString = re.sub("'", "", re.sub('"', ' ', tags_toString))
    
    if product_type != "":
        contents += '. ' + product_type
        
    if tags_toString != "":
        contents += ". " + tags_toString
        
    if buckets != "":
        contents += ". " + buckets 
    
    return contents

'''
Clean the html with regex.
Input: raw html String
Output: After processing body_html String 

'''
def cleanHtml(html):
    cleantext = ""
    if not isinstance(html, str) or html is None:
        return cleantext
    #res = lxml.html.clean.clean_html(html)
    
    html = re.sub(re.compile(r"{.*?}"), " ", html)
    html = re.sub(re.compile(r"<.*?>"), " ", html)
    
    contents = re.sub("\n", "", html)
    contents = re.sub('&amp;', 'and', contents)
    contents = re.sub("'s", " is", contents)
    contents = re.sub("'ll", " will", contents)
    contents = re.sub("'ve", " have", contents)
    contents = re.sub("'m", " am", contents)
    contents = re.sub('"', "", contents)
    contents = re.sub("'", "", contents)
    contents = re.sub("\'", "'", contents)
    contents = re.sub("¬†", " ", contents)
    
    cleantext = re.compile(r"\s+").sub(" ", contents).strip()
    cleantext = unicodedata.normalize("NFKD", cleantext)
    try:
        #discard the 
        cleantext = cleantext.split("FEATURES")
        return cleantext[0]
    except:
        return cleantext
    #clean_text = BeautifulSoup(text, "lxml").get_text(strip=True)
    

'''
Directly use the information from csv cells in ['title', 'tags', 'body_html']
return pre-processing raw_text without "FEATURE"
'''
def raw_content(title=None, tags=None, body_html=None, buckets=None):
    
    text_1 = clean_tags_text(title, tags, None, buckets)
    text_2 = cleanHtml(body_html)

    raw_text = text_1 + '. ' + text_2
    res = re.compile(r"\s+").sub(" ", raw_text).strip()
    return res
'''
Input: raw_html
Function: extract special tag description from html
Output: list
'''
def get_special_tag_product_description(raw_html):
    tag = 'p' #if we just want to extract the content inside the <p> ..{content}. </p>
    reg_str = '<' + tag + ">(.*?)</" + tag + '>'
    cleanText = re.findall(reg_str, raw_html)
    return cleanText
def test():
    title = "Aria High Waist"
    tags = "{d-cup+,meta-size-chart-artesands-size-guide,moderate-coverage,one-piece,plus-size,swim-wear}"
    example = '''
    <p>Holbrook is a timeless, classic design fused with modern Oakley technology. Inspired by the screen heroes from the 1940s, 50s, and 60s, this design epitomizes the spirit of exploration and adventure. The iconic American frame design is accented by metal rivets and Oakley icons, perfect for those who seek equal parts performance and style.</p>\n<div data-field="productTechnologies" data-level="variant" class="mp-item mp-pdp-item o21_text7 o21_text-color1"><span class="description">Oakley lenses designed and tested under extreme high mass and high velocity circumstances to ensure uncompromising protection across a wide range of demanding conditions.</span></div>\n<div class="technology__lens-options">\n<div class="lens-options__heading">\n<img alt="Prizm Sapphire Polarized" class="lens-options__icon" src="https://assets.oakley.com/extra/image/Oakley/OakleyDRAG/910000000063_puck.png?impolicy=OO_thumb"><span>\xa0</span><span data-field="secondaryColor" data-level="Lens" class="lens-options__name mp-item mp-pdp-item o21_text8 o21_text-medium text-uppercase o21_text-color1">PRIZM SAPPHIRE POLARIZED</span><span class="sports"></span>\n</div>\n<div class="lens-options__details">\n<ul>\n<li class="o21_text8">\n<span class="detail-title o21_text-color2">Light Transmission:</span><span>\xa0</span><span data-field="lightTransmission percentage" data-level="lens" class="detail-value mp-item mp-pdp-item o21_text-color1">12%</span>\n</li>\n<li class="o21_text8">\n<span class="detail-title o21_text-color2">Light Conditions:</span><span>\xa0</span><span data-field="lightTransmission lightingCondition" data-level="lens" class="detail-value  mp-item mp-pdp-item">Bright Light</span>\n</li>\n<li class="o21_text8">\n<span class="detail-title o21_text-color2">Contrast:</span><span>\xa0</span><span data-field="lightTransmission contrast" data-level="lens" class="detail-value mp-item mp-pdp-item o21_text-color1">Increased</span>\n</li>\n<li class="o21_text8">\n<span class="detail-title o21_text-color2">Base Lens Color:</span><span>\xa0</span><span data-field="lightTransmission lensBaseColor" data-level="lens" class="detail-value mp-item mp-pdp-item o21_text-color1">GRAY</span>\n</li>\n<li class="o21_text8">\n<span class="detail-title o21_text-color2">Information notice:</span><span>\xa0</span><span data-field="lensInfoNote" data-level="lens" class="detail-value mp-item mp-pdp-item o21_text-color1">3</span>\n</li>\n</ul>\n</div>\n</div>\n<ul></ul>
    '''

    body_html = '"<meta charset="utf-8"><p><meta charset="utf-8"><span>The Hues Underwire One Piece has a beautifully sculpted feminine wrap-around style. The Hue has a hidden shelf bra with internal support underwire to fit a D cup to DD cup. This swimsuit style allows all of the fit and support required for body sculpting and figure forming confidence for the curvy body. </span></p><p data-mce-fragment="1"><meta charset="utf-8"><em data-mce-fragment="1">Model is wearing an Australian size 18+ </em></p><p class="p1" data-mce-fragment="1"><b data-mce-fragment="1">FEATURES:</b></p><ul class="ul1" data-mce-fragment="1"><li class="li1" data-mce-fragment="1">Supportive Underwire  <br data-mce-fragment="1"></li><li class="li1" data-mce-fragment="1">Removable &amp; Adjustable Straps  </li><li class="li1" data-mce-fragment="1">Front Ruching <br data-mce-fragment="1"></li><li class="li1" data-mce-fragment="1">D/DD Cup Underwire Support <br data-mce-fragment="1"></li><li class="li1" data-mce-fragment="1"> <div data-mce-fragment="1">Nylon / Elastane Blend. </div></li></ul><div class="p2" style="text-align: center;" data-mce-style="text-align: center;" data-mce-fragment="1"><b data-mce-fragment="1"><span data-mce-fragment="1">Artesands Fits Your Curves. Designed in Australia. </span></b></div><h5 style="text-align: left;" data-mce-fragment="1"><strong>Care Notes</strong></h5><p><strong></strong>We recommend hand washing in cold water. Dry flat in a shady spot out of direct sunlight. Do not wring out or hang dry. </p><p>Chlorinated water is not great and can cause colours to fade. Please make sure you always wash your swimsuit well after swimming in chlorinated water. We recommend swimsuit cleaner to keep your swimsuit looking amazing.</p>"'
    buckets = "{Casual,ActiveWear,Streetwear}"
    #print(raw_content(title, None, body_html, None))
    print(cleanHtml(example))
'''
When you use the test() which used the raw_content() only. You can directly use the  
Output:Aria High Waist; d cup+ meta size chart artesands size guide moderate coverage one piece plus size swim wear. The Hues Underwire One Piece has a beautifully sculpted feminine wrap-around style. The Hue has a hidden shelf bra with internal support underwire to fit a D cup to DD cup. This swimsuit style allows all of the fit and support required for body sculpting and figure forming confidence for the curvy body. Model is wearing an Australian size 18+ FEATURES:Supportive Underwire  Removable and; Adjustable Straps  Front Ruching D/DD Cup Underwire Support  Nylon / Elastane Blend. Artesands Fits Your Curves. Designed in Australia. Care NotesWe recommend hand washing in cold water. Dry flat in a shady spot out of direct sunlight. Do not wring out or hang dry. Chlorinated water is not great and can cause colours to fade. Please make sure you always wash your swimsuit well after swimming in chlorinated water. We recommend swimsuit cleaner to keep your swimsuit looking amazing.


'''
#test()