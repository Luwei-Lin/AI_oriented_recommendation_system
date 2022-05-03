from pickletools import optimize
from numpy import loadtxt
from keras.models import Sequential
from keras.layers import Dense
from keras.models import model_from_json
import numpy
import os

from sklearn import metrics

def load_data():
    dataset = loadtxt('pima-indians-diabetes.csv', delimiter=',')
    
    X = dataset[:, 0:8]
    y = dataset[:, 8]
    # define the keras model
    model = Sequential()
    model.add(Dense(12, input_dim=8, activation='relu'))
    model.add(Dense(8, activation='relu'))
    model.add(Dense(1, activation='sigmoid'))
    
    # compile the keras model
    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
    model.fit(X, y, epochs=150, batch_size=10)
    #evaluate the model
    _, accuracy = model.evaluate(X, y)
    print('Accuracy: %.2f' % (accuracy*100))
    
    #predictions = (model.predict(X) > 0.5).astype(int)
    #for i in range(5):
    #    print('%s => %d (expected %d)' %  (X[i].tolist(), predictions[i], y[i]))
    
    #serialize model to JSON
    model_json = model.to_json()
    with open("model.json", "w") as json_file:
        json_file.write(model_json)
    #serialize weights to HDF5
    model.save_weights("model.h5")
    print("Saved model to disk")
    
    #later to load 
    json_file = open('model.json', 'r')
    loaded_model_json = json_file.read()
    json_file.close()
    loaded_model = model_from_json(loaded_model_json)
    #load weights into new model
    loaded_model.load_weights("model.h5")
    print("Loaded model from disk")
    
    #evaluate loaded model on test data
    loaded_model.compile(loss = 'binary_crossentropy', optimizer='rmsprop', metrics= ['accuracy'])
    score = loaded_model.evaluate(X, y, verbose = 0)
    print("%s: %.2f%%" % (loaded_model.metrics_names[1], score[1]*100))
    
    
def main():
    load_data()
main()