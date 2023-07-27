import numpy as np 
import pandas as pd

isFileOpen = dict()

def save(fileName, data, timestamp, channels=None):

    if(len(fileName) > 20):
        fileName = fileName[:20]

    dataDict = {"timestamp":timestamp}

    for chn,chnName in enumerate(channels):
        dataDict[f"{chnName}"] = data[chn]


    if not fileName in isFileOpen:
        isFileOpen[fileName] = 0
        frame = pd.DataFrame(dataDict,index=[isFileOpen[fileName]])
        frame.index.name = "index"
        frame.to_csv(f'{fileName}.csv', mode='w')
    else:
        isFileOpen[fileName] += 1
        frame = pd.DataFrame(dataDict,index=[isFileOpen[fileName]])
        frame.to_csv(f'{fileName}.csv', mode='a', header=False)

def close(fileName):
    if fileName in isFileOpen:
        isFileOpen.pop(fileName)

# if __name__ == "__main__":

#     timestamp = 1.0
#     data = [3,4,2,4,5]

#     save("test",np.array(data),timestamp)