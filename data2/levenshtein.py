from math import sqrt

from mrjob.job import MRJob
from mrjob.protocol import JSONValueProtocol
from mrjob.step import MRStep


class levenshteinSimilarity(MRJob):

    OUTPUT_PROTOCOL = JSONValueProtocol
    def mapperSimilarity(self, _, line):
        SIMILARITY_THRESHOLD = 0.8
        words = line.split(';')       
        distance = self.calculateLevenshtein(words[0], words[1])
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
    

    def calculateLevenshtein(self, word1, word2):
        if len(word1) < len(word2):
            return self.calculateLevenshtein(word2, word1)
        previous_row = range(len(word2) + 1)
        for i, c1 in enumerate(word1):
            current_row = [i + 1]
            for j, c2 in enumerate(word2):
                insertions = previous_row[j + 1] + 1 
                deletions = current_row[j] + 1      
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        return previous_row[-1]
    
    def normalizeDistanceIndex(self, word1Len, word2Len, distanceIndex):
        return 1 - (distanceIndex/(sqrt(max(word1Len, word2Len) * sqrt(word1Len*word2Len))))
    

    def mergeDicts(self, dict_args):
        result = {}
        for dictionary in dict_args:
            result.update(dictionary)
        return result
    
    


if __name__ == '__main__':
    levenshteinSimilarity.run()
