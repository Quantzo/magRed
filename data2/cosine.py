from functools import reduce
from math import sqrt

from mrjob.job import MRJob
from mrjob.protocol import JSONValueProtocol
from mrjob.step import MRStep


class cosineSimilarity(MRJob):

    OUTPUT_PROTOCOL = JSONValueProtocol
    def mapperSimilarity(self, _, line):
        SIMILARITY_THRESHOLD = 0.8
        words = line.split(';')     
        sim = self.calculateSimilarity(words[0], words[1])
        if(sim > SIMILARITY_THRESHOLD):
            yield(words[0], [words[1], sim])       

    def reducerConstructDictionaries(self, key, values):        
        yield(None, {key : list(values)})

    def reducerConstructJSON(self, _, dictionaries):
        yield(None, self.mergeDicts(dictionaries))

    def steps(self):
        return[
        MRStep(mapper = self.mapperSimilarity,
        reducer = self.reducerConstructDictionaries),
        MRStep(reducer = self.reducerConstructJSON)
    ]

    def getUniqueCharacters(self, word):
        return list(set(word))

    def letterCount(self, letter, word):
        return word.count(letter)
    

    def calculateSimilarity(self, word1, word2):
        characters = self.getUniqueCharacters(word1+word2)
        calculateDotProduct =lambda K, L:reduce(lambda z1, z2: z1+z2, map(lambda x: reduce(lambda x1, x2: x1*x2, x), zip(K, L)))
        calculateMagnitude = lambda V : reduce(lambda x1, x2: x1+x2 ,map(lambda x: x*x, V))
        vec1 = []
        vec2 = []
        for charcter in characters:
            vec1.append(self.letterCount(charcter, word1))
            vec2.append(self.letterCount(charcter, word2))
        
        dotprod = calculateDotProduct(vec1, vec2)
        mag1 = calculateMagnitude(vec1)
        mag2 = calculateMagnitude(vec2)
        return dotprod/sqrt(mag1*mag2)

    def mergeDicts(self, dict_args):
        result = {}
        for dictionary in dict_args:
            result.update(dictionary)
        return result 
    
    


if __name__ == '__main__':
    cosineSimilarity.run()
