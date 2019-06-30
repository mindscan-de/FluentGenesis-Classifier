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
from keras.utils import plot_model

### TODO: load / create_embedding_matrix

embedding_dim = 300


def create_inline_CNNs( embedding_dimension ):
    cnn_input_layer = layers.Input(shape=(64,embedding_dimension,1))
    
    tower_1_c = layers.Conv2D(256, kernel_size=(1,embedding_dimension), strides=(1,1), padding='valid', activation='relu' )(cnn_input_layer)
    tower_1_p = layers.GlobalMaxPooling2D()(tower_1_c)
    
    tower_2_c = layers.Conv2D(128, kernel_size=(2,embedding_dimension), strides=(1,1), padding='valid', activation='relu' )(cnn_input_layer)
    tower_2_p = layers.GlobalMaxPooling2D()(tower_2_c)
    
    tower_3_c = layers.Conv2D(64, kernel_size=(3,embedding_dimension), strides=(1,1), padding='valid', activation='relu' )(cnn_input_layer)
    tower_3_p = layers.GlobalMaxPooling2D()(tower_3_c)
    
    tower_4_c = layers.Conv2D(32, kernel_size=(4,embedding_dimension), strides=(1,1), padding='valid', activation='relu' )(cnn_input_layer)
    tower_4_p = layers.GlobalMaxPooling2D()(tower_4_c)
        
    merged = layers.concatenate([tower_1_p, tower_2_p, tower_3_p, tower_4_p])
    cnn_model = Model(cnn_input_layer, merged)
    cnn_model.summary()
    return cnn_model


### TODO: https://realpython.com/python-keras-text-classification/
def createModel(vocab_size, embedding_dimension, embedding_matrix):
    model = Sequential()
    my_input_length= 64
    
    model.add( layers.Embedding(input_dim=vocab_size, output_dim=embedding_dimension, weights=[embedding_matrix], input_length=my_input_length, trainable=False) )
    model.add( layers.Reshape(target_shape=(my_input_length, embedding_dimension, 1)))
    
    embedded_text_cnn_model = create_inline_CNNs(embedding_dimension)
    model.add( embedded_text_cnn_model )
    
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
    plot_model(embedded_text_cnn_model, to_file="current_cnn_model.png", show_shapes=True)
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