from math import sqrt
from statistics import mean

from mrjob.job import MRJob
from mrjob.protocol import JSONValueProtocol
from mrjob.step import MRStep
from jellyfish import levenshtein_distance


class levenshteinMeanDistance(MRJob):
    def mapper(self, _, line):
        words = line.split(';')                
        distance = levenshtein_distance(words[0], words[1])
        yield(None, distance)
 

    def reducer(self, key, values):        
        yield(None, mean(values))

if __name__ == '__main__':
    levenshteinMeanDistance.run()
