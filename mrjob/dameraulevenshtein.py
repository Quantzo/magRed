from math import sqrt

from mrjob.job import MRJob
from mrjob.protocol import JSONValueProtocol
from mrjob.step import MRStep
from jellyfish import damerau_levenshtein_distance


class damerauLevenshteinSimilarity(MRJob):

    OUTPUT_PROTOCOL = JSONValueProtocol
    def mapperSimilarity(self, _, line):
        SIMILARITY_THRESHOLD = -1.0
        words = line.split(' ')        
        distance = damerau_levenshtein_distance(words[0], words[1])
        sim = self.normalizeDistanceIndex(len(words[0]), len(words[1]), distance)
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

    def mergeDicts(self, dict_args):
        result = {}
        for dictionary in dict_args:
            result.update(dictionary)
        return result 
    
    def normalizeDistanceIndex(self, word1Len, word2Len, distanceIndex):
        return 1 - (distanceIndex/(sqrt(max(word1Len, word2Len) * sqrt(word1Len*word2Len))))


if __name__ == '__main__':
    damerauLevenshteinSimilarity.run()
