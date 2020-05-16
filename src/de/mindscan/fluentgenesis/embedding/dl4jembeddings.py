'''
Created on 16.05.2020

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

@author: Maxim Gansert, Mindscan
'''

class DL4jModifiedEmbeddings(object):
    '''
    This class implements a load operation of embeddings created by Deeplearning4j. Because the word2vec algorithm of 
    Deeplearning4j ignores numbers and does not provide embeddings for them, synthetic words for each number had to be 
    generated. The input of the deeplearning4j was only numbers, therefeore the synthetic words do not interfere with 
    natural words.
    
    Another issue is, that some embeddings could not be calculated by the dl4j word2vec algorithm because the encoder 
    did not generate the associated token. The word wasn't uniquely part of the encoding, but only a intermediate word
    which does not occur standalone. This has to be accounted for. The current solution is to replicate the unknown
    word embedding vector for these missing words, in case that these indexes will be used later during training.
    
    Also it is important, that these embeddings can be used by tensorflow + keras. 
    '''


    def __init__(self, params):
        '''
        Constructor
        '''
        