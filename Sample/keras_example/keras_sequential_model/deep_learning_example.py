from numpy import loadtxt
from keras.models import Sequential
from keras.layers import Dense


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
    
    #_, accuracy = model.evaluate(X, y)
    
    #print('Accuracy: %.2f' % (accuracy*100))
    
    predictions = (model.predict(X) > 0.5).astype(int)
    for i in range(5):
        print('%s => %d (expected %d)' %  (X[i].tolist(), predictions[i], y[i]))
    
    
def main():
    load_data()
main()