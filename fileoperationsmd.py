import pickle
import xlwt
from textprocessingmd import decodeText
def loadPKLData(file_dir):
   try:
      with open(file_dir, 'rb') as input:
        pklFile=pickle.load(input)
	return pklFile
   except:
      return None

def savePKLData(file_dir,object):
   try:
      with open(file_dir, 'wb') as output:
         pickle.dump(object, output, pickle.HIGHEST_PROTOCOL)
      return True
   except:
      return False

def readTxtFile(filedir):
   try:
       f=open(filedir,'r')
       return f.read()
   except:
	return None

def writeDataframeXLS(*args):
   outputXlsFile=args[0]
   wb = xlwt.Workbook(encoding='utf8')
   for i in range(1,len(args)):
        dtclass=args[i]
        sheet=dtclass.getName()
        columns=dtclass.getColumnsNames()
        Data=dtclass.getData()[columns]
        ws = wb.add_sheet(sheet)
        for i,row in enumerate(Data):
            mxx=len(str(row))
            ws.write(0,i,decodeText(row))
            for j, col in enumerate(Data[row]):
              dcol=decodeText(col)
              ws.write(j+1, i, dcol)
              mxx=max(len(dcol),mxx)
            ws.col(i).width = 256 * (mxx+3)
   wb.save(outputXlsFile)
