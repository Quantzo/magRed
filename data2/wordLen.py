import argparse
from statistics import mean

def calculateMeanLen(inputfile, outputfile):
    data = []
    with open(inputfile, 'r', errors='ignore') as file:
        for line in file:
            tmp = line.strip()
            data.append(len(tmp))
    with open(outputfile, 'w') as file:
        file.write(str(mean(data)))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", '--text-file')
    parser.add_argument("-o", '--output')
    args = parser.parse_args()
    calculateMeanLen(args.text_file, args.output)