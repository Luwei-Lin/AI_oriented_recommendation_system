import requests
import os, json, re, random
import pandas as pd

from pathlib import Path

workingDir = os.getcwd()

def readJsonFile(filename):
    with open(filename) as dataFile:
        return json.load(dataFile)

def cleanHtml(html):
    return re.sub("\n", "",  re.sub(re.compile('<.*?>'), '', html))

def createDirIfNotExist(dirPath):
    Path(workingDir + "/" + dirPath).mkdir(parents=True, exist_ok=True)

def downloadFile(url, dest):
    f = open(dest, 'wb')
    f.write(requests.get(url, allow_redirects=True).content)
    f.close()

def extractImageExt(url):
    if ".png?v" in url.lower():
        return ".png"
    if ".jpg?v" in url.lower():
        return ".jpg"

if __name__ == "__main__":
    
    # Read JSON data:
    # for product in readJsonFile(workingDir + "/products.json")['products']:
        # retrieveProductImages(product)
    
    filteredData = dict()
    sampleAmount = 250
    columnChosen = ['id', 'title', 'handle', 'images', 'product_type', 'tags', 'options', 
                    'buckets', 'gender', 'body_html']
    
    df = pd.read_csv(workingDir + "/products.csv")
    # columnNames = list(df)
    
    for index in random.sample(range(len(df.index)), sampleAmount):
        row = df.iloc[index]
        
        for columnName in columnChosen:
            if columnName != 'images':
                
                if columnName == 'body_html':
                    row[columnName] = cleanHtml(str(row[columnName]))
                    # print(row[columnName])
                
                if columnName not in filteredData:
                    filteredData[columnName] = [row[columnName]]
                else:
                    filteredData[columnName].append(row[columnName])
                    
            '''//download images.
            else:
                for image in json.loads(row['images']):
                    createDirIfNotExist(str(row["id"]))
                    dest = workingDir + "/" + str(row["id"]) + "/" + str(row["id"]) + "-" 
                    if image["position"] != None:
                        dest += str(image["position"]) + extractImageExt(image["src"])
                    else:
                        dest += extractImageExt(image["src"])
                    downloadFile(image["src"], dest)                    
            '''
        
    pd.DataFrame(filteredData).reset_index().to_csv(workingDir + "/filtered_products.csv")
    
