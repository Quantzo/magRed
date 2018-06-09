from math import sqrt
from difflib import SequenceMatcher
from functools import reduce
from collections import Counter

from mrjob.job import MRJob
from mrjob.protocol import JSONValueProtocol
from mrjob.step import MRStep
from jellyfish import damerau_levenshtein_distance
from jellyfish import jaro_winkler


class combinedSimilarity(MRJob):
    OUTPUT_PROTOCOL = JSONValueProtocol
    def mapperWordSplitter(self, _, line):        
        words = line.split(' ')
        if len(words[0]) > 10:
            yield("dl", [words[0], words[1]])
        else:
            yield("rat", [words[0], words[1]])   

    def mapperSimilarity(self, key, data):
        if key == "dl":
            SIMILARITY_THRESHOLD = 0.8
            distance = damerau_levenshtein_distance(data[0], data[1])
            sim = self.normalizeDistanceIndex(len(data[0]), len(data[1]), distance)
            if(sim > SIMILARITY_THRESHOLD):
                 yield(data[0], [data[1], sim])

        elif key == "rat":
            SIMILARITY_THRESHOLD = 0.8
            sim = SequenceMatcher(a = data[0], b = data[1]).ratio()
            if(sim > SIMILARITY_THRESHOLD):
                 yield(data[0], [data[1], sim])




    def reducerConstructDictionaries(self, key, values):        
        yield(None, {key : list(values)})

    def reducerConstructJSON(self, _, dictionaries):
        yield(None, self.mergeDicts(dictionaries))

    def steps(self):
        return[
        MRStep(mapper= self.mapperWordSplitter),
        MRStep(mapper = self.mapperSimilarity,
        reducer = self.reducerConstructDictionaries),
        MRStep(reducer = self.reducerConstructJSON)
    ]   

    def mergeDicts(self, dict_args):
        result = {}
        for dictionary in dict_args:
            result.update(dictionary)
        return result 
    
    def normalizeDistanceIndex(self, word1Len, word2Len, distanceIndex):
        return 1 - (distanceIndex/(sqrt(max(word1Len, word2Len) * sqrt(word1Len*word2Len))))
    

if __name__ == '__main__':
    combinedSimilarity.run()
