from flask import Flask, request, jsonify
# from GetOutputFromMLModels import return_labels
from product import Product

# Initializing flask app
app = Flask(__name__)


# Route for seeing a data
@app.route("/getLables", methods=['POST'])
def getLables():

    path = request.form.get("path") # Path of image
    title = request.form.get("title") # title
    text = request.form.get("text") # text


    if (path != None and text != None):
        # print(path)
        import GetOutputFromMLModels as gofmm
        product = gofmm.return_labels(path, text, title)
        # print(product)

    import productToJson as pj
    data = jsonify(pj.getjson(product))
    # data = pj.getjson(product)

    return data



if __name__ == '__main__':
    app.run()