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
                yield("ap", [data[0], data[1], sim])
                yield("cos", [data[0], data[1], sim])
                yield("jw", [data[0], data[1], sim])
        elif key == "rat":
            SIMILARITY_THRESHOLD = 0.8
            sim = SequenceMatcher(a = data[0], b = data[1]).ratio()
            if(sim > SIMILARITY_THRESHOLD):
                yield("ap", [data[0], data[1], sim])
                yield("cos", [data[0], data[1], sim])
                yield("jw", [data[0], data[1], sim])

    def mapperVote(self, key, data):
        ADJACENT_THRESHOLD = 0.8
        COSINE_THRESHOLD = 0.9
        JARO_THRESHOLD = 0.9
        sim = 0
        vote = False
        if key == "ap":
            sim = self.calculateAdjacentSimilarity(data[0], data[1])
            if sim > ADJACENT_THRESHOLD:
                vote = True            
        elif key == "cos":
            sim = self.calculateCosSimilarity(data[0], data[1])
            if sim > COSINE_THRESHOLD:
                vote = True  
        elif key == "jw":
            sim = jaro_winkler(data[0], data[1])
            if sim > JARO_THRESHOLD:
                vote = True  
        yield(data[0]+data[1], [data[0], data[1], vote, sim])

    def reducerVote(self, key, values):
        BO_3 = True
        data = list(values)
        wordKey = data[0][0]
        wordMiss = data[0][1]
        sim = data[0][3]
        voteResults = []
        for itemList in data:
            voteResults.append(itemList[2])
        if BO_3:
            c = Counter(voteResults)
            if c[True] > 1:
                yield(wordKey, [wordMiss, sim])
        else:
            if True in voteResults:
                yield(wordKey, [wordMiss, sim])

    def reducerConstructDictionaries(self, key, values):        
        yield(None, {key : list(values)})

    def reducerConstructJSON(self, _, dictionaries):
        yield(None, self.mergeDicts(dictionaries))

    def steps(self):
        return[
        MRStep(mapper= self.mapperWordSplitter),
        MRStep(mapper = self.mapperSimilarity),
        MRStep(mapper = self.mapperVote,
        reducer = self.reducerVote),
        MRStep(reducer = self.reducerConstructDictionaries),
        MRStep(reducer = self.reducerConstructJSON)
    ]   

    def mergeDicts(self, dict_args):
        result = {}
        for dictionary in dict_args:
            result.update(dictionary)
        return result 
    
    def normalizeDistanceIndex(self, word1Len, word2Len, distanceIndex):
        return 1 - (distanceIndex/(sqrt(max(word1Len, word2Len) * sqrt(word1Len*word2Len))))

    def calculateAdjacentSimilarity(self, word1, word2):
        pairs1 = self.letterPairs(word1)
        pairs2 = self.letterPairs(word2)
        intersection = 0
        union = len(pairs1) + len(pairs2)
        for pair1 in pairs1:
            for i in range(len(pairs2)):
                if(pair1 == pairs2[i]):
                    intersection += 1
                    del pairs2[i]
                    break
        return (2.0*intersection)/union

    def letterPairs(self, word):
        pairs = []
        for i in range(len(word)-1):
            pairs.append(word[i:i+2])
        return pairs


    def getUniqueCharacters(self, word):
        return list(set(word))

    def letterCount(self, letter, word):
        return word.count(letter)
    

    def calculateCosSimilarity(self, word1, word2):
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

if __name__ == '__main__':
    combinedSimilarity.run()
