from collections import defaultdict
from json import dump
import itertools
import argparse

def mergeDicts(dict_args):
    result = {}
    for dictionary in dict_args:
        result.update(dictionary)
    return result

def parseLine(fileLine):
    data = fileLine.split("->")
    data[1] = list(map(lambda x: x.strip(), data[1].split(',')))
    return data

def saveList(fileName, dataSet):
    with open(fileName+".txt", 'w') as file:
        for item in dataSet:
            file.write(item + '\n')            

def saveCartesianProduct(fileName, product):
    with open(fileName+".txt", 'w') as file:
        for item in product:
            file.write(f"{item[0]} {item[1]}\n")
def filterSet(minNumber,mergedDict):
    return dict(filter(lambda i : len(i[1]) > minNumber , mergedDict.items()))

def saveSets(validation, minNumber):
    validationSet = defaultdict(set)
    for dictionary in validation:
        for k, v in dictionary.items():
            validationSet[k].add(v)    
    validationList = list(map(lambda x : {x : list(validationSet[x])}, validationSet))
    mergedDict = mergeDicts(validationList)
    reducedDict = filterSet(minNumber, mergedDict)
    correct = list(reducedDict.keys())
    misspells = set(itertools.chain(*reducedDict.values()))

    prod = itertools.product(correct, misspells)
    saveList("corrSet" + str(minNumber), correct)
    saveList("missSet" + str(minNumber), misspells)
    saveCartesianProduct(f"input{minNumber}", prod)
    with open("valiSet" + str(minNumber)+".json", 'w') as jsonfile:
        dump(reducedDict, jsonfile)


def extractSets(fileName, minNumber):
    misspelings = []
    correct = []
    validation = []
    with open(fileName, 'r') as file:
        for line in file:
            data = parseLine(line)
            validation.extend(list(map(lambda x: {x: data[0]}, data[1])))  
    saveSets(validation, minNumber)




if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", '--text-file')
    parser.add_argument("-m", '--min-number')
    args = parser.parse_args()
    extractSets(args.text_file, int(args.min_number))