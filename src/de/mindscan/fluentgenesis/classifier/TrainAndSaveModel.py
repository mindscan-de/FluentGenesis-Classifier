'''
MIT License

Copyright (c) 2019 Maxim Gansert

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

@author: Maxim Gansert
'''

import sys
import argparse

import numpy as np

from keras.models import Sequential
from keras import layers
import traceback

### TODO: load / create_embedding_matrix

### TODO: https://realpython.com/python-keras-text-classification/
def createModel(vocab_size, embedding_dim, embedding_matrix):
    model = Sequential()
    # TODO: do the - embedding layer - non trainable pretrainied with glove.
    #
    # model.add( layers.Embedding(input_dim=vocab_size, output_dim=embedding_dim, weights=[embedding_matrix], input_length=64, trainable=False) )
    # 
    # TODO:
    # start with a simple and single convolutional layer ... 
    # later on we will do here more different kernelsizes 150*(300,1), 50*(300,2), 50*(300,3), 50*(300,4) and stack them to a 250 element vector
    # instead of 250 x (300x4) vextor
    model.add( layers.Conv2D(250, kernel_size=(embedding_dim,4), strides=(1,1), padding='valid', activation='relu', batch_input_shape=(None, embedding_dim, 64, 1)))
    model.add( layers.GlobalMaxPooling2D() )   # should return 250 values... one for each kernel.
    
    # fully connected layers
    model.add(layers.Dense(512, activation='relu'))
    model.add(layers.Dense(512, activation='relu'))
    
    # add output Layer - 100 different output classes of intents 
    model.add(layers.Dense(100, activation='sigmoid'))
    
    # compile and prin summary of the model
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    model.summary()
    return model
    
    

def runSourceCodeClassifierTraining():
    vocab_size=1000
    embedding_dim = 300
    embedding_matrix=np.zeros((vocab_size, embedding_dim), dtype=np.float32)
    # embedding_matrix = create_embedding_matrix('D:\Projects\SinglePageApplication\Angular\FluentGenesis-Classifier\data\glove\glove.6B.50d.txt')
    _ = createModel(vocab_size, embedding_dim, embedding_matrix)
    pass

def main(argv = None):
    argv = argv or sys.argv[1:]
    parser = argparse.ArgumentParser(description="Training of the FluentGenesis-Classifier-Model.")
    
    try:
        _ = parser.parse_args(argv)
        # args.
        runSourceCodeClassifierTraining()
        
    except:
        trace = traceback.format_exc()
        print (trace)
        print ("Exception occured, which one you ask? i don't know")
        return 1
    finally:
        return 0

if __name__ == '__main__':
    sys.exit(main())