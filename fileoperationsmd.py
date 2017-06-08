import pickle

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
