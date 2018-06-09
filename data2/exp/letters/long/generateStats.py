import json
import argparse
from functools import reduce
from statistics import mean, median_grouped, stdev
import matplotlib.pyplot as plt
import pylab
from astropy.visualization import hist
 
class experimentStatistic:
    def __init__(self, matchNumber, correctMatches, excessMatches, maxCorrectMatches, coverage, correctRatio, wrongRatio, totalMisspellings ):
        self.matchNumber = matchNumber
        self.correctMatches = correctMatches
        self.excessMatches = excessMatches
        self.maxCorrectMatches = maxCorrectMatches
        self.coverage = coverage
        self.correctRatio = correctRatio
        self.wrongRatio = wrongRatio
        self.truePositive = self.correctMatches
        self.falsePositive = self.excessMatches
        self.falseNegative = self.maxCorrectMatches - correctMatches
        self.trueNegative = totalMisspellings-(self.excessMatches + self.falseNegative + self.correctMatches)
        #truePositiveRate, sensitivty
        self.recall = self.truePositive/(self.truePositive + self.falseNegative)
        #trueNegativeRate
        self.specifity = self.trueNegative/(self.trueNegative + self.falsePositive)
        #falsePositiveRate
        self.falsePositiveRate = self.falsePositive/(self.falsePositive + self.trueNegative)
        #positive predictive value
        self.precision = 0
        self.f_score = 0            
        self.calculatePrecision()
        self.calculateFScore()
        self.accurancy = (self.truePositive + self.trueNegative)/totalMisspellings
    def calculateFScore(self):
        if(self.recall + self.precision == 0):
            self.f_score = 0            
        else:
            self.f_score =  (2 *self.precision * self.recall)/(self.precision + self.recall)

    def calculatePrecision(self):
        if(self.truePositive + self.falsePositive == 0):
            self.precision = 0
        else:
            self.precision = self.truePositive/(self.truePositive + self.falsePositive)

class vectorStatistic:
    def __init__(self, meanv, medianv, meanDev, stDev):
        self.mean = meanv
        self.median = medianv
        self.mean_deviation = meanDev
        self.standard_deviation = stDev

def loadJSONFile(fileName):
    with open(fileName, 'r') as file:
        data = json.load(file)
    return data
    
def calculateStatistics(valRecord, expRecord, totalMisspellings):
    maxCorrectMatches = len(valRecord)
    matchNumber = len(expRecord)
    correctMatches = 0
    excessMatches = 0
    for elem in expRecord:
        if elem[0] in valRecord:
            correctMatches += 1
        else:
            excessMatches += 1
    coverage = correctMatches/maxCorrectMatches
    correctRatio = correctMatches/matchNumber
    wrongRatio = excessMatches/matchNumber    
    return experimentStatistic(matchNumber,correctMatches, excessMatches, maxCorrectMatches, coverage, correctRatio, wrongRatio, totalMisspellings).__dict__


def prepareStatistics(experimentFilename, validationFileName, resultsFolder, totalMisspellings):
    valData = loadJSONFile(validationFileName)
    expData = loadJSONFile(experimentFilename)
    statData = dict()
    for record in valData.items():
        if(record[0] in expData):
            expRecord = expData[record[0]]
            statData.update({record[0] : calculateStatistics(record[1], expRecord, totalMisspellings) })
        else:
            statData.update({record[0] : experimentStatistic(0,0,0,len(record[1]),0,0,0, totalMisspellings).__dict__ })

    with open(resultsFolder+"/experientStats.json", 'w') as jsonFile:
        json.dump(statData, jsonFile)

    coverageVec = []
    correctRatioVec = []
    wrongRatioVec = []


    for record in statData.items():
        coverageVec.append(record[1]['coverage'])
        correctRatioVec.append(record[1]['correctRatio'])
        wrongRatioVec.append(record[1]['wrongRatio'])


    
    coverageStats ={ 'coverage' : prepareVecStatistics(coverageVec) }
    correctRatioStats ={ 'correctRatio' : prepareVecStatistics(correctRatioVec) }
    wrongRatioStats = { 'wrongRatio' : prepareVecStatistics(wrongRatioVec) }

    globalStats = {}
    globalStats.update(coverageStats)
    globalStats.update(correctRatioStats)
    globalStats.update(wrongRatioStats)

    with open(resultsFolder+"/globalStats.json", 'w') as jsonFile:
        json.dump(globalStats, jsonFile)

    plt.ioff()
    saveHistogram(coverageVec, resultsFolder+"/covHist.png", "Histogram pokrycia", "Pokrycie", "Liczebność" )
    saveHistogram(correctRatioVec, resultsFolder+"/corHist.png", "Histogram wspołczynnika oryginalnych elementów do całości", "Współczynnik", "Liczebność")
    saveHistogram(wrongRatioVec, resultsFolder+"/wrongHist.png", "Histogram wspołczynnika innych elementów do całości", "Współczynnik", "Liczebność")

    




def calculateMean(vector):
    return mean(vector)
def calculateMedian(vector):
    return median_grouped(vector, interval = 0.1)
def calculateStdev(vector):
    return stdev(vector)
def calculateMeanDev(vector, meanv):
    sum = 0
    for val in vector:
        sum += abs(val - meanv)
    return sum/len(vector)


def prepareVecStatistics(vector):
    meanv = calculateMean(vector)
    medianv = calculateMedian(vector)
    stdevv = calculateStdev(vector)
    meandevv = calculateMeanDev(vector, meanv)
    return vectorStatistic(meanv, medianv, meandevv, stdevv).__dict__


def saveHistogram(vector, name, title, xlabel, ylabel):
    plt.figure()
    hist(vector, bins="blocks", histtype = "step")
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.savefig(name)



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-iv", '--validation-set-filename')
    parser.add_argument("-ie", '--experiment-set-filename')
    parser.add_argument("-tm", '--total-misspellings')
    parser.add_argument("-o", '--result-folder')
    args = parser.parse_args()

    prepareStatistics(args.experiment_set_filename, args.validation_set_filename, args.result_folder, int(args.total_misspellings))
