import re
import argparse

def clean(filename):
    with open(filename, mode='r+') as file:        
        data = re.sub(r'\\u\w{4}', '', file.read())
        file.seek(0)
        file.write(data)
        file.truncate()



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", '--filename')
    args = parser.parse_args()

    clean(args.filename)