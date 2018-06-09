from difflib import SequenceMatcher

from mrjob.job import MRJob
from mrjob.protocol import JSONValueProtocol
from mrjob.step import MRStep


class ratcliffSimilarity(MRJob):

    OUTPUT_PROTOCOL = JSONValueProtocol
    def mapperSimilarity(self, _, line):
        SIMILARITY_THRESHOLD = -1.0
        words = line.split(' ') 
        sim = SequenceMatcher(a = words[0], b = words[1]).ratio()
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
    


if __name__ == '__main__':
    ratcliffSimilarity.run()
