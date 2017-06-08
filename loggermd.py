#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import unittest
from datetime import datetime

"""this module contains classes to handle Exceptions messages 
   and log to text file
"""
class LogMessageInterface:
    def getMessage(self):
        raise NotImplementedError('subclasses must override !')
class ExceptionLogMessage(LogMessageInterface):
    """ Log message for Exceptions
    """
    dtime=None
    moduleN=None
    classN=None
    methodN=None
    descr=None
    details=None
    def __init__(self,dtime,moduleN,classN,methodN,descr,details):
        self.dtime=str(dtime)
        self.moduleN=str(moduleN)
        self.classN=str(classN)
        self.methodN=str(methodN)
        self.descr=str(descr)
        self.details=str(details)
    # overrides(LogMessageInterface)
    def getMessage(self):
        message=self.dtime+" --- "+self.moduleN+"/"+self.classN+"/"+self.methodN+ " --- "+self.descr+" --- "+str(self.details)+'\n'
	return message


class Logger:
    """this class responsible for logging to external text file
    """
    filedir=None
    file=None
    def __init__(self,filedir):
	self.filedir=filedir
	self.file=None
    def openFile(self):
	# is already oppened
	if self.file!=None:
	     return True
	# filedir is not specified
	if (self.filedir==None):
	    return False
	try:
	    self.file=open(self.filedir,'a')
	    return True
	except Exception as ex:
	    print 'Logger/openFile',ex
	    return False
    def log(self,logMessage):
	if isinstance(logMessage,LogMessageInterface):
		logmessage=logMessage.getMessage()
	else:
		logmessage=str(logMessage)
	status=1
	try:
	  if not self.openFile():
	     status=3 #file not openned
	     return status
	  self.file.write(logmessage)
	except Exception as ex:
	  status=0 #failed to log
	  print 'Logger/log',ex
	return status


class testHelpers(unittest.TestCase):
    """ unit test for classes in this module """
    def test_Logger(self):
        logFile='test.log'
        logger=Logger(logFile)
        # all keys existed
        message=ExceptionLogMessage(
            moduleN="helpersmd.py",
            dtime=datetime.now(),
            classN="testHelpers",
            methodN="test_Logger",
            descr="testing with all keys",
            details={"m":"m","n":"n"}
        )
        status=logger.log(message)
        self.assertEqual(status,1)


if __name__ == '__main__':
    unittest.main()

