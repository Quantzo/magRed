import matplotlib
matplotlib.use('Agg')
import json
import argparse
import numpy as np
import matplotlib.pyplot as plt

from sklearn.metrics import roc_curve, auc
from scipy import interp





def plotRoc(fprMicro, tprMicro, roc_aucMicro, fprMacro, tprMacro, roc_aucMacro, name):
    plt.ioff()
    plt.figure()
    plt.plot(fprMicro, tprMicro, lw=2, color='darkorange', label='micro-average ROC curve (area = %0.8f)' % roc_aucMicro)
    plt.plot(fprMacro, tprMacro, lw=2, color='red', label='macro-average ROC curve (area = %0.8f)' % roc_aucMacro)
    plt.plot([0, 1], [0, 1], color='navy', lw = 2)
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title("Ratcliff/Obershelp")
    plt.legend(loc="lower right")
    plt.savefig(name)





def loadJSONFile(fileName):
    with open(fileName, 'r') as file:
        data = json.load(file)
    return data


def createVectors(expRecord, valRecord):
    label = []
    score = []
    for elem in expRecord:
        if elem[0] in valRecord:
            label.append(1)
        else:
            label.append(0)
        score.append(elem[1])
    return (score, label)


def prepareRoc(experimentFilename, validationFileName, outputName):
    valData = loadJSONFile(validationFileName)
    expData = loadJSONFile(experimentFilename)
    data = dict()
    for record in expData.items():
        valRecord = valData[record[0]]
        vectors = createVectors(record[1], valRecord)
        data.update({record[0] : vectors})
    fpr = dict()
    tpr = dict()
    roc_auc = dict()
    yscores = []
    ylabels = []
    i = 0
    for item in data.items():
        fpr[i], tpr[i], _ = roc_curve(item[1][1], item[1][0])
        roc_auc[item[0]] = auc(fpr[i], tpr[i])
        yscores.append(item[1][0])
        ylabels.append(item[1][1])
        i+=1 

    flatten = lambda l: [item for sublist in l for item in sublist]
    fpr['micro'], tpr['micro'], _ = roc_curve(flatten(ylabels), flatten(yscores))
    roc_auc["micro"] = auc(fpr["micro"], tpr["micro"])

    all_fpr = np.unique(np.concatenate([fpr[j] for j in range(i)]))

    mean_tpr = np.zeros_like(all_fpr)
    for i in range(i):
        mean_tpr += interp(all_fpr, fpr[i], tpr[i])

    mean_tpr /= i

    fpr["macro"] = all_fpr
    tpr["macro"] = mean_tpr
    roc_auc["macro"] = auc(fpr["macro"], tpr["macro"])

    plotRoc(fpr['micro'],tpr['micro'], roc_auc["micro"], fpr['macro'],tpr['macro'], roc_auc["macro"], outputName)

    





if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-iv", '--validation-set-filename')
    parser.add_argument("-ie", '--experiment-set-filename')
    parser.add_argument("-o", '--roc-file')
    args = parser.parse_args()

    prepareRoc(args.experiment_set_filename, args.validation_set_filename, args.roc_file)