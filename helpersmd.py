#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import unittest
from datetime import datetime
from config import Config
from loggermd import Logger,ExceptionLogMessage
import urllib2
"""this module contains helper classes"""

class GeneralClass:
    """General Class:
      contains common methods and attributes between classes
    """
    logger=None
    def setLogger(self,logger):
	"""this is setter method 
	   logger is instanse of Logger class
	   It will be used to log exeptions and other messages
	"""
	if isinstance(logger,Logger):
		self.logger=logger
	else:
		self.logger=None


class ConfigData(GeneralClass):
     """ ConfigData class
       this class is used to get key/values from configuration text
       file
     """
     moduleName='helpersmd.py'
     className='ConfigData'
     filedir=None
     cfg=None
     def __init__(self,filedir):
        self.filedir=filedir
     def loadCfg(self):
        try:
           f=file(self.filedir)
           self.cfg=Config(f)
	   return True
        except Exception as ex:
           print ex
           self.cfg=None
	   if self.logger!=None:
	     exMessage=ExceptionLogMessage(
                  moduleN=self.moduleName,
                  dtime=datetime.now(),
                  classN=self.className,
                  methodN="loadCfg",
                  descr=str(ex),
                  details=None
             )
             self.logger.log(exMessage)
	   return False

     def getValue(self,key):
        if (self.cfg==None):
            if not self.loadCfg():
	      	if self.logger!=None:
		    exMessage=ExceptionLogMessage(moduleN=self.moduleName,
                   	dtime=datetime.now(),classN=self.className,
                   	methodN="getValue/1",descr="",
                   	details="configuration file not loaded"
                    )
		    self.logger.log(exMessage)
		return None
        try:
            return self.cfg[key]
        except Exception as ex:
            if self.logger!=None:
              exMessage=ExceptionLogMessage(
                moduleN=self.moduleName,
                dtime=datetime.now(),
                classN=self.className,
                methodN="getValue/2",
                descr=str(ex),
                details=None
              )
              self.logger.log(exMessage)
            print str(ex)
            return None

def getRequest(url):
        req = urllib2.Request(url)
        response=urllib2.urlopen(req)
        return response

""" unit test for classes in this module """
class testHelpers(unittest.TestCase):
    def test_ConfigDataWithLog(self):
        logFile='test.log'
        logger=Logger(logFile)

        testFile='settings.cfg'
        testKey='testKey'
	wrongKey='wrong'
        # check retrieval of config value
        cfg=ConfigData(testFile)
        cfg.setLogger(logger)
        testValue=cfg.getValue(testKey)
        self.assertEqual(testValue,'testValue')
	# check retrieval with wrong key
        cfg=ConfigData(testFile)
        cfg.setLogger(logger)
        testValue=cfg.getValue(wrongKey)
        self.assertEqual(testValue,None)
        # wrong config new object
        cfg2=ConfigData(testFile)
        cfg2.setLogger(logger)
        testValue=cfg2.getValue(wrongKey)
        self.assertEqual(testValue,None)

if __name__ == '__main__':
    unittest.main()

