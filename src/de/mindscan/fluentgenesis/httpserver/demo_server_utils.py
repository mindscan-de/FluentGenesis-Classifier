'''
Created on 18.08.2020

MIT License

Copyright (c) 2020 Maxim Gansert

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

@author: Maxim Gansert, Mindscan
'''

import numpy as np
import tensorflow as tf

from com.github.c2nes.javalang import tokenizer as tokenizer

from de.mindscan.fluentgenesis.bpe.bpe_model import BPEModel
from de.mindscan.fluentgenesis.bpe.bpe_encoder_decoder import SimpleBPEEncoder

PAD = 0
UNK = 0

bpemodel = BPEModel("16K-full", "../bpe/")
bpemodel.load_hparams()

dataset_directory = bpemodel.get_data_source_path()

bpemodel_vocabulary = bpemodel.load_tokens()
bpemodel_bpe_data = bpemodel.load_bpe_pairs()

bpemodel_vocabulary['<PAD>'] = 0

encoder = SimpleBPEEncoder(bpemodel_vocabulary, bpemodel_bpe_data)

MODEL_VOCABULARY_LENGTH = len(bpemodel_vocabulary)


checkpoint = '../../../../../data/checkpoints/20200516_1750/predict_m'

m_model = tf.keras.models.load_model(checkpoint)
m_model.summary()


def top_k(p,k):
    probabilities=p.copy()
    result = []
    for _ in range(0,k):
        first_class = np.argmax(probabilities, axis=-1)
        probabilities[first_class]=0.0
        result.append(first_class)
    return result


def predictTheMethodName(theSource : str , K:int):
    # tokenize the code into java tokens...
    tokens = list(tokenizer.tokenize(theSource, ignore_errors=True))
    tokenvalues = [x.value for x in tokens]
    
    # encode the tokens
    encodedtokens = encoder.encode(tokenvalues) + [0]*24
    lengthconstrainedtokens = encodedtokens[:24]

    # predict labels
    to_predict=[lengthconstrainedtokens]
    thedata = np.stack(np.array(to_predict))
    probs = m_model.predict([thedata])
    mytopK = top_k(probs[0],K)
    return encoder.decode(mytopK)

