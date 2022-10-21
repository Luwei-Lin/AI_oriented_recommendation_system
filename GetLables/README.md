# Auto Labelling System

This system will take product description along with product image to generate corresponding labels


## Environment settings:
<ol>
<li /> Python version: 3.9
<li/> Install spacy, sklearn, bs4, rembg, colormath and fastai latest versions. Delete spacy after installing all these packages and install the latest version again.
<li> Add <br><br> temp = pathlib.PosixPath<br>
pathlib.PosixPath = pathlib.WindowsPath<br><br>
after import part in ImageClassifier.py if the OS is Windows.
</ol>
