import argparse
from json import dump
from random import randrange
import itertools

alphabet = "abcdefghijklmnopqrstuvwxyz0123456789"

def skipLetter(s):
    kwds = []
    i = randrange(len(s)+1)
    kwds.append(s[:i-1] + s[i:])
    return kwds

def doubleLetter(s):
    kwds = []
    i = randrange(len(s)+1)
    kwds.append(s[:i] + s[i-1] + s[i:])
    return kwds


def reverseLetter(s):
    kwds = []
    i = randrange(len(s))
    letters = s[i-1:i+1:1]
    if len(letters) == 2:
        reverse_letters = letters[1] + letters[0]
        kwds.append(s[:i-1] + reverse_letters + s[i+1:])       

    return kwds

def wrongKey(s):
    kwds = []

    i = randrange(len(s))
    j = randrange(len(alphabet))
    kwd = s[:i] + alphabet[j] + s[i+1:]
    kwds.append(kwd)
    return kwds

def insertedKey(s):
    kwds = []
    i = randrange(len(s))
    j = randrange(len(alphabet))
    kwds.append(s[:i+1] + alphabet[j] + s[i+1:])
    return kwds





def generateMisspelligns(line):
    misspellings = []
    misspellings.extend(skipLetter(line))
    misspellings.extend(doubleLetter(line))
    misspellings.extend(reverseLetter(line))
    misspellings.extend(wrongKey(line))
    misspellings.extend(insertedKey(line))
    return misspellings


def generateSets(inputFile):
    valDict = {}
    misspellings = []
    correct = []
    with open(inputFile) as file:
        for line in file:
            lineTmp = line.strip()           
            correct.append(lineTmp)
            tmp = generateMisspelligns(lineTmp)
            misspellings.extend(tmp)
            valDict[lineTmp] = tmp
    with open("valiSet.json","w") as jsonfile:
        dump(valDict, jsonfile)
    uniqueMisspellings = set(misspellings)

    with open("missSet.txt", 'w') as file:
        for item in uniqueMisspellings:
            file.write(f"{item}\n")

    prod = itertools.product(correct, misspellings)
    with open("input.txt", 'w') as file:
        for item in prod:
            file.write(f"{item[0]};{item[1]}\n")



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", '--text-file')
    args = parser.parse_args()
    generateSets(args.text_file)