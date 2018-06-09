import argparse
import re

def cleanData(inputFile, outputFile):
    data = []
    with open(inputFile, 'r') as file:
        for line in file:
            items = line.split(" see ")
            for item in items:
                tmp = re.sub('\(.*?\)','', item)
                newItem = tmp.replace('/',"").replace(',', "").lower().strip()
                data.append(newItem)

    clean = set(data)

    with open(outputFile, 'w') as file:
        for item in clean:
            file.write(f"{item}\n")        




if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", '--text-file')
    parser.add_argument("-o", '--output-file')

    args = parser.parse_args()
    cleanData(args.text_file, args.output_file)