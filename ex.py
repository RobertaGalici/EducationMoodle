import os
import glob
import pandas as pd
from tqdm import tqdm
import matplotlib.pyplot as plt
from datetime import datetime as dt
from glob import glob

def getNumberOfAccess(path):
    df = pd.read_csv(path, sep='\t', encoding='utf-16')
    df0 = df.drop_duplicates(subset=[' login'])
    df1 = df.dropna() # dropna() method will drop entire row if any value in the row is missing
    df2 = df1[~df1[' session-name'].str.contains(' Cd')] # esclude i campi dove si loggano quelli del personale
    return (len(df2)) # numero di righe, quindi accessi, di persone che si sono loggate

def getAccess(pathGlobal):
    dictAccess = {}
    for root, dirs, files in os.walk(pathGlobal):
        for dirname in sorted(dirs):
            faculty = dirname.split('_')[1]
            if faculty not in dictAccess:
                dictAccess[faculty] = {}

            for file in os.listdir(os.path.join(root, dirname)):
                if file != '.DS_Store':
                    if file.endswith('.csv'):
                        cdl = file.split('.')[0].split('-')[-1]
                        cdlDate = file.split('.')[0].split('-')[0]
                        cdlType = file.split('.')[0].split('-')[1]
                        #student = getStudentName()
                        if cdl not in dictAccess[faculty]:
                            dictAccess[faculty][cdl] = {}
                        if cdlType not in dictAccess[faculty][cdl]:
                            dictAccess[faculty][cdl][cdlType] = []
                        if os.stat(os.path.join(root, dirname, file)).st_size == 0:
                            dictAccess[faculty][cdl][cdlType].append((cdlDate, 0))
                        else:
                            dictAccess[faculty][cdl][cdlType].append((cdlDate, getNumberOfAccess(os.path.join(root, dirname, file))))
    return dictAccess

def createPlot(dataPlots, titlePlot=None, cdlType=None, cdl=None):
    plt.figure(figsize=(20, 10), dpi=300)
    L = {'IA':'Engineering and Architecture', 'SCIENZE': 'Science', 'BiologiaFarmacia': 'Biology and Farmacy', 'SEGP': 'Economic, Law and Political Sciences',
         'SU': 'Humanities', 'MEDICINA': 'Medicine and Surgery'}
    for i, (key, data) in enumerate(dataPlots.items()):
        plt.subplot(2, 3, i+1)
        plt.title(L[key])

        x = [day for day, access in data]
        y = [access for day, access in data]
       # x, y = zip(*sorted(zip(x, y)))
        xdates = [dt.strptime(dstr, '%Y%m%d') for dstr in x]
        plt.plot(xdates, y)
        plt.xticks(rotation=45)
        plt.xlabel("Lessons date")
        plt.ylabel("Avg Students per Degree")
        plt.ylim([0, 800])
        plt.xlim([dt.strptime('20200315', '%Y%m%d'), dt.strptime('20200615', '%Y%m%d')])
        plt.grid()
    plt.tight_layout()
    plt.savefig("/Users/robertagalici/Desktop/avgStudentsPerDegree.png")

def getStudentName(path):
    df = pd.read_csv(path, sep='\t', encoding='utf-16')[' session-name']
    print(df)


# Set your path to the folder containing the .csv files
pathGlobal = '../data/unica-ac/'

# numero di file per tutti i cdl
numberCdl = [y for x in os.walk(pathGlobal) for y in glob(os.path.join(x[0], '*.csv'))]
print("Total of csv: ", len(numberCdl))

# 0. print con il numero di file per ogni cdl
for facultydir in os.listdir('../data/unica-ac/'):
    if facultydir != '.DS_Store':
        path = os.path.join(pathGlobal, facultydir)
        numberCdl = [y for x in os.walk(path, topdown=True) for y in glob(os.path.join(x[0], '*.csv'))]
        print("Number of csv", facultydir, len(numberCdl))

dataAccess = getAccess(pathGlobal)


dataMagistrale = dataAccess #lista con coppie

dataAccessFlatten = {}

for faculty, faculty_data in tqdm(dataAccess.items()):
    dataAccessFlatten[faculty] = {}
    for cdl, cdl_data in faculty_data.items():
        for type, type_data in cdl_data.items():
            for day, n_access in type_data:
                day = day if len(day) <= 8 else day[1:]
                if day not in dataAccessFlatten[faculty]:
                    dataAccessFlatten[faculty][day] = (0, 0)
                dsum, dcount = dataAccessFlatten[faculty][day]
                dsum += n_access
                dcount += 1
                dataAccessFlatten[faculty][day] = (dsum, dcount)

dataAccessFlattenLST = {}

for faculty, faculty_data in tqdm(dataAccess.items()):
    dataAccessFlattenLST[faculty] = []
    for day in sorted(dataAccessFlatten[faculty].keys()):
        dsum, dcount = dataAccessFlatten[faculty][day]
        if dsum//dcount > 20:
            dataAccessFlattenLST[faculty].append((day, dsum//dcount))
# numero di studenti medi che seguono per un corso (per lezione)

#print(dataAccessFlattenLST)
title = "Science"
plotsM = createPlot(dataAccessFlattenLST, title)

# creare un array per ogni corso dove ci dice il numero max di studenti che l'hanno seguito. Dividere ogni valore, il numero di studenti per ogni lezione,
# per il numero max, per tutte le lezioni: tutto in percentuale
