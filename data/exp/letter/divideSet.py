import json
import argparse


def divideSet(inputFileName, output1FileName, output2FileName, filterValue):
    with open(inputFileName, 'r') as dataSet:
        data = json.load(dataSet)
    
    firstSet = list(filter(lambda x : len(x) <= filterValue, data.keys()))
    secondSet = list(filter(lambda x : len(x) > filterValue, data.keys()))

    firstDict = createNewDict(firstSet, data)
    secondDict = createNewDict(secondSet, data)

    saveFile(output1FileName, firstDict)
    saveFile(output2FileName, secondDict)



def createNewDict(oldKeys, oldDict):
    newDict = dict()
    for oldKey in oldKeys:
        newDict.update({oldKey : oldDict[oldKey]})
    return newDict
    
def saveFile(fileName, data):
    with open(fileName, 'w') as filep:
        json.dump(data, filep)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", '--input-set')
    parser.add_argument("-o1", '--output-file1')
    parser.add_argument("-o2", '--output-file2')
    parser.add_argument("-f", '--filter-value')
    args = parser.parse_args()
    divideSet(args.input_set, args.output_file1, args.output_file2, int(args.filter_value))
