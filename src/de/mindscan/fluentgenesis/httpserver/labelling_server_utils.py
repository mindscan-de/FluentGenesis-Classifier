'''
Created on 07.11.2020 

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

@autor: Maxim Gansert, Mindscan
'''
import tensorflow as tf


## BPE ENCODER PART
from de.mindscan.fluentgenesis.bpe.bpe_model import BPEModel
from de.mindscan.fluentgenesis.bpe.bpe_encoder_decoder import SimpleBPEEncoder

SYMBOL_PAD = 0
SYMBOL_START = 16273
SYMBOL_EOS = 16274

bpemodel = BPEModel("16K-full", "../bpe/")
bpemodel.load_hparams()
bpemodel_vocabulary = bpemodel.load_tokens()
bpemodel_bpe_data = bpemodel.load_bpe_pairs()

# padding
bpemodel_vocabulary['<PAD>'] = SYMBOL_PAD
# start symbol
bpemodel_vocabulary['<START>'] = SYMBOL_START
# end of sentence
bpemodel_vocabulary['<EOS>'] = SYMBOL_EOS

bpe_encoder = SimpleBPEEncoder(bpemodel_vocabulary, bpemodel_bpe_data)

MODEL_VOCABULARY_LENGTH = len(bpemodel_vocabulary)

## TOKENIZER PART

from com.github.c2nes.javalang import tokenizer as tokenizer

def tokenize_java_code(theSource: str):
    tokens = list(tokenizer.tokenize(theSource, ignore_errors=True))
    tokenvalues = [x.value for x in tokens]
    
    return tokenvalues

## TRANSFORMER PART


from de.mindscan.fluentgenesis.transformer import TfTransformerV2

MAX_OUTPUTLENGTH = 120

transformer_restored = TfTransformerV2.Transformer(
    num_layers=4, d_model=256, num_heads=8, dff=1024,
    input_vocab_size=16275, target_vocab_size=16275,
    pe_input=512, pe_target=512,
    rate=0.0
    )

transformer_restored.load_weights(filepath='../../../../../data/checkpoints/methodnames_s_emb/v5_1/tf')

def create_padding_mask(seq):
    # this will create a mask from the input, whereever the input is Zero, it is treated as a padding.
    # and a one is written to the result, otherwise a Zero is written to the array (where true -> '1.0': else '0.0')
    seq = tf.cast(tf.math.equal(seq, 0), tf.float32)
  
    # Mask has dimensions (batchsize, 1,1, seq_len)
    return seq[:, tf.newaxis, tf.newaxis, :]

def create_look_ahead_mask(size):
    mask = 1 - tf.linalg.band_part(tf.ones((size, size)), -1, 0)
    return mask  # (seq_len, seq_len)


def create_masks(inp, tar):
    # encoder padding mask
    enc_padding_mask = create_padding_mask(inp)
    
    # wird im second attentionblock im decoder benutzt, um den input zu maskieren
    dec_padding_mask = create_padding_mask(inp)
    
    look_ahead_mask = create_look_ahead_mask(tf.shape(tar)[1])
    dec_target_padding_mask = create_padding_mask(tar)
    combined_mask = tf.maximum(dec_target_padding_mask, look_ahead_mask)
    
    return enc_padding_mask, combined_mask, dec_padding_mask

def append_prediction_column(predicted_matrix, predicted_categories_column, column_mask):
    masked_predicted_categories_column = tf.math.multiply(predicted_categories_column, column_mask )
    return tf.concat([predicted_matrix, masked_predicted_categories_column], axis=1)

# Challenge 5 - rank method names - later
def update_probability_vector( previous_step_vector, current_vector):
    return  tf.transpose(tf.math.multiply(tf.transpose( previous_step_vector),current_vector ))

def isInRange(x):
    return 1 if (x>0 and x<16274) else 0

def update_column_mask(sampled_categories,column_mask):
    updated_sampled_cats = tf.map_fn(isInRange,sampled_categories)
    return tf.transpose(tf.math.multiply(tf.transpose(column_mask),updated_sampled_cats))

def inRangeM(x):
    return 1.0 if (x>0) else 0.0

def outRangeM(x):
    return 0.0 if (x>0) else 1.0

def build_probability_vector( sampled_cat_probabilities, column_mask):
    # 0 for all completed rows, and 1 for all
    inRangeVector = tf.map_fn(inRangeM,column_mask,dtype=tf.float32)
    # the inrange vector must be multiplied with the sampled probabilities
    inRangeProbabilities = tf.transpose(tf.math.multiply(tf.transpose(inRangeVector),sampled_cat_probabilities))
    
    # 1.0 for all completed rows
    outRangeVector = tf.map_fn(outRangeM,column_mask,dtype=tf.float32)
    
    return inRangeProbabilities + outRangeVector

# Multipredictor
def batch_prediction_methodname( transformer, method_body , batch_size = 5):
    bpe_tokenized_input = [16273] + bpe_encoder.encode( tokenize_java_code( method_body ) ) + [ 16274, 0]

    # all sentences are valid
    column_mask = tf.repeat([[1,]], batch_size, axis=0)
    
    # 
    output_probability = tf.repeat([[1.0,]], batch_size, axis=0)
    
    # we need that input vector: transformer (from)
    input_line = tf.constant(([bpe_tokenized_input]))
    input_matrix = tf.repeat(input_line, batch_size, axis=0)

    # output vctor: transformer (to)
    startvector=tf.constant(([[16273,]]))
    start_output_vector = tf.repeat( startvector, batch_size, axis=0)
    sampled_output_matrix = start_output_vector

    for _ in range(16):
        enc_padding_mask, combined_mask, dec_padding_mask = create_masks(input_matrix,sampled_output_matrix)
        predictions, _ = transformer(input_matrix,
                                     sampled_output_matrix, 
                                     False,
                                     enc_padding_mask,
                                     combined_mask,
                                     dec_padding_mask
                                    )
        predictions = predictions[:,-1, :]
        probabilities=tf.nn.softmax(predictions)
        
        # sampled categories ist predict categorical, von einer logits-Matrix
        # output shape is (batchsize,1)
        sampled_categories = tf.random.categorical( logits=predictions, num_samples=1, dtype=tf.int32 )
        sampled_probabilities = tf.gather_nd(probabilities, sampled_categories,batch_dims=1)

        # wir benutzen die predicted_categories und die logits_matrix um den probability vektor zu aktualisieren
        # lookup the probabilities for each category first category first line, ...
        sampled_output_matrix = append_prediction_column( sampled_output_matrix, sampled_categories, column_mask )

        # we use a mask to track, where we already hit end of line
        column_mask = update_column_mask(sampled_categories,column_mask)
        output_probability = update_probability_vector(output_probability, 
                                                       build_probability_vector( sampled_probabilities, column_mask ))
        
        if tf.math.reduce_sum(column_mask) == 0:
            return sampled_output_matrix, input_matrix, output_probability

        
        # todo remove finished vectors / line?
        # print( sampled_output_matrix )
        # if all lines finished -> break; sampled categories contains value between >0 and <16273 -> continue
        pass
        
    return sampled_output_matrix, input_matrix, output_probability


def predictMultipleMethodNames(methodBody : str, max_parallel_requests: int = 100):

    predicted_names, _, probabilities = batch_prediction_methodname(transformer_restored,
                                          methodBody, 
                                          batch_size=max_parallel_requests)
    
    probability_of_names = probabilities.numpy();
    predicted_names = predicted_names.numpy();
    
    #print(predicted_names)
    predicted_names_string = []
    # convert methodnames into strings
    for i in range(0,len(predicted_names)):
        current_predicted_name = predicted_names[i]
        bpe_decoded_name = bpe_encoder.decode([ t for t in current_predicted_name if t>0 and t<16273])
        predicted_names_string.append(''.join(bpe_decoded_name) )

    probability_of_names = [ p[0]*100.0 for p in probability_of_names ]
    
    zipped = zip(predicted_names_string, probability_of_names)
    # filter duplicates and sort by probability
    zipped = list(set(zipped))
    zipped = sorted(zipped, reverse=True, key=lambda x: x[1])
    # convert to dictionary item
    return [ {'methodName': x, 'methodProbability':p} for (x,p) in zipped ]
    

