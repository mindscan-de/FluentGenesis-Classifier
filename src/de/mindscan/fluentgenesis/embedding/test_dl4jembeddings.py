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
import unittest
from fluentcheck import Check

from de.mindscan.fluentgenesis.embedding import dl4jembeddings

def assertThat(x):
    return Check(x)

class Test(unittest.TestCase):


    def testDecodeSyntheticWord_Empty_expectEmpty(self):
        # arrange
        embedding = dl4jembeddings.DL4jModifiedEmbeddings()
        
        #act
        result = embedding.decode_synthetic_word('')
        
        #assert
        assertThat( result ).is_empty()
        
    def testDecodeSyntheticWord_WordSmallA_expectTranslation_0(self):
        # arrange
        embedding = dl4jembeddings.DL4jModifiedEmbeddings()
        
        #act
        result = embedding.decode_synthetic_word('a')

        #assert
        assertThat( result ).matches('0')
        
    def testDecodeSyntheticWord_WordSmallB_expectTranslation_1(self):
        # arrange
        embedding = dl4jembeddings.DL4jModifiedEmbeddings()
        
        #act
        result = embedding.decode_synthetic_word('b')

        #assert
        assertThat( result ).matches('1')

    def testDecodeSyntheticWord_WordSmallBA_expectTranslation_10(self):
        # arrange
        embedding = dl4jembeddings.DL4jModifiedEmbeddings()
        
        #act
        result = embedding.decode_synthetic_word('ba')

        #assert
        assertThat( result ).matches('10')
        
    def testDecodeSyntheticWord_WordSmallJJ_expectTranslation_99(self):
        # arrange
        embedding = dl4jembeddings.DL4jModifiedEmbeddings()
        
        #act
        result = embedding.decode_synthetic_word('jj')

        #assert
        assertThat( result ).matches('99')

    def testDecodeSyntheticWord_WordSmallBCDEFGHIJA_expectTranslation_1234567890(self):
        # arrange
        embedding = dl4jembeddings.DL4jModifiedEmbeddings()
        
        #act
        result = embedding.decode_synthetic_word('bcdefghija')

        #assert
        assertThat( result ).matches('1234567890')
    

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testDecodeSyntheticWord_Empty_expectEmpty']
    unittest.main()