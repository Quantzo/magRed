from mrjob.job import MRJob
from mrjob.protocol import JSONValueProtocol
from mrjob.step import MRStep


class adjacentPairingSimilarity(MRJob):

    OUTPUT_PROTOCOL = JSONValueProtocol
    def mapperSimilarity(self, _, line):
        SIMILARITY_THRESHOLD = -1.0
        words = line.split(' ') 
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

    def mergeDicts(self, dict_args):
        result = {}
        for dictionary in dict_args:
            result.update(dictionary)
        return result

    def letterPairs(self, word):
        pairs = []
        for i in range(len(word)-1):
            pairs.append(word[i:i+2])
        return pairs



    def calculateSimilarity(self, word1, word2):
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


if __name__ == '__main__':
    adjacentPairingSimilarity.run()



