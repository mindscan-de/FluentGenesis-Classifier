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

import argparse
import numpy as np
import sys
import traceback

from keras.models import Sequential, Model
from keras import layers
from keras.layers.pooling import MaxPooling2D
from keras.engine.topology import InputLayer
from grpc.framework.foundation.logging_pool import pool
from keras.utils import plot_model

### TODO: load / create_embedding_matrix

embedding_dim = 300

number_of_kernels = {}
number_of_kernels[0] = 150
number_of_kernels[1] = 50
number_of_kernels[2] = 50
number_of_kernels[3] = 50

kernel_sizes =  { }
kernel_sizes[0] = (1, embedding_dim)
kernel_sizes[1] = (2, embedding_dim)
kernel_sizes[2] = (3, embedding_dim)
kernel_sizes[3] = (4, embedding_dim)


# def create_parallel_CNNs( inputLayer ):
#     convs = []
#     for k_no in range(len(kernel_sizes)):
#         conv = layers.Conv2D(number_of_kernels[k_no], kernel_size=kernel_sizes[k_no], strides=(1,1), padding='valid', activation='relu' )(inputLayer)
#         pool = MaxPooling2D()(conv)
#         convs.append(pool)
#     outputLayer = layers.Concatenate()(convs)
#     conv_model = Model(input=inputLayer, output=outputLayer)
#     return conv_model


#def create_inline_CNNs( inputLayer ):
#     input = layers.Input(shape=(64,300,1))
#     local_conv = layers.Conv2D(250, kernel_size=(4,embedding_dim), strides=(1,1), padding='valid', activation='relu' )(input) # , batch_input_shape=(None, embedding_dimension, 64, 1)
#     pool = layers.GlobalMaxPooling2D()(local_conv)    # should return 250 values... one for each kernel.
#     cnn_model = Model(InputLayer, pool)
#     return cnn_model


### TODO: https://realpython.com/python-keras-text-classification/
def createModel(vocab_size, embedding_dimension, embedding_matrix):
    model = Sequential()
    my_input_length= 64
    
    model.add( layers.Embedding(input_dim=vocab_size, output_dim=embedding_dimension, weights=[embedding_matrix], input_length=my_input_length, trainable=False) )
    reshapedInput = layers.Reshape(target_shape=(my_input_length, embedding_dimension, 1))
    model.add( reshapedInput)
    
    # does not working properly
    # model.add( create_inline_CNNs(reshapedInput) )
    
    # TODO:
    # start with a simple and single convolutional layer ... 
    # later on we will do here more different kernelsizes like 150*(1,300), 50*(2,300), 50*(3,300), 50*(4,300) and stack them to a 250 element vector
    # instead of 250 x (4,300) vextor
    model.add( layers.Conv2D(250, kernel_size=(4,embedding_dimension), strides=(1,1), padding='valid', activation='relu' )) # , batch_input_shape=(None, embedding_dimension, 64, 1)
    model.add( layers.GlobalMaxPooling2D() )   # should return 250 values... one for each kernel.
    
    # more robust predictions with dropout
    model.add( layers.Dropout(0.25) )
    
    # fully connected layers
    model.add(layers.Dense(512, activation='relu'))
    model.add(layers.Dense(512, activation='relu'))
    
    model.add( layers.Dropout(0.5) )
    
    # add output Layer - 100 different output classes of intents 
    model.add(layers.Dense(100, activation='sigmoid'))
    
    # compile and prin summary of the model
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    model.summary()
    
    plot_model(model, to_file="current_model.png", show_shapes=True)
    return model
    
    

def runSourceCodeClassifierTraining():
    vocab_size=1000

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