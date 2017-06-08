#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""this module contains classes needed to communicate with Yandex Translation API
	this API is used to detect type of words , return to origin and get further information
   - YandexTranslationAPI : this class takes care of communications steps with Yandex API
   - YandexTrParser : this class parse the response returned from API
   and there's also model classes for different types of words
"""
import sys
import unittest
from datetime import datetime
from config import Config
from helpersmd import ConfigData,GeneralClass,getRequest
from loggermd import Logger,ExceptionLogMessage
import urllib2
import json
from bs4 import BeautifulSoup
import xlwt
class YandexTrParser(GeneralClass):
   """ this class is used to parse response of Yandex Translation API
	and extract specific values
   """
   moduleName='generate.py'
   className='YandexTrParser'
   response=None
   def __init__(self,response):
	self.response=response
   def getOrg(self):
        """returns origin word (unicode) """
        try:
           ret=self.response["ru-en"]["regular"][0]["text"]
	   return ret
        except Exception as ex:
          if self.logger!=None:
              exMessage=ExceptionLogMessage(
                moduleN=self.moduleName,
                dtime=datetime.now(),
                classN=self.className,
                methodN="getOrgText",
                descr=str(ex),
                details={"word":self.word}
              )
              self.logger.log(exMessage) 
          return None
   def getType(self):
	""" returns type of the word 
	    'nn'  : noun
	    'vrb' : verb
	    'adj' : adjective
	    ..
	    None : word not recognized
	"""
        try:
           return self.response["ru-en"]["regular"][0]["pos"]["code"]
        except Exception as ex:
          if self.logger!=None:
              exMessage=ExceptionLogMessage(
                moduleN=self.moduleName,
                dtime=datetime.now(),
                classN=self.className,
                methodN="getType",
                descr=str(ex),
                details={"word":self.word}
              )
              self.logger.log(exMessage) 
          return None
   def getAsp(self):
	""" returns aspective of a verb
	    'pf' : perfective
	    'imp' : imperfective
	    None: not a verb
	"""
        try:
           ret=self.response["ru-en"]["regular"][0]["asp"]["code"]
	   return ret
        except Exception as ex:
          if self.logger!=None:
              exMessage=ExceptionLogMessage(
                moduleN=self.moduleName,
                dtime=datetime.now(),
                classN=self.className,
                methodN="getAsp",
                descr=str(ex),
                details={"word":self.word}
              )
              self.logger.log(exMessage) 
          return None
   def getGen(self):
	""" returns gender of a noun
	    'm':male
	    'f':female
	    'n':neutron
	    None:has no gender
	"""
        try:
           return self.response["ru-en"]["regular"][0]["gen"]["code"]
        except Exception as ex:
          if self.logger!=None:
              exMessage=ExceptionLogMessage(
                moduleN=self.moduleName,
                dtime=datetime.now(),
                classN=self.className,
                methodN="getGen",
                descr=str(ex),
                details={"word":self.word}
              )
              self.logger.log(exMessage)
	  return None


class YandexTranslationAPI(GeneralClass):
   """This class takes care of communication with Yandex Translation API
	and conversion of response to needed forms
   """
   moduleName='generate.py'
   className='YandexTranslationAPI'
   TRANSLATE_URL=None
   def __init__(self,truri):
	self.TRANSLATE_URL=truri
   def getResponse(self,word):
        """ establish conniction and return response """
	try:
	  qword = urllib2.quote(word)
	  url=self.TRANSLATE_URL+qword
	  res=getRequest(url)
	  return res
	except Exception as ex:
	  if self.logger!=None:
              exMessage=ExceptionLogMessage(
                moduleN=self.moduleName,
                dtime=datetime.now(),
                classN=self.className,
                methodN="loadResponse",
                descr=str(ex),
                details={"word":word}
              )
              self.logger.log(exMessage)
	  return None
   def getResponseJSON(self,word):
	""" conver response to json """
	res=self.getResponse(word)
	if res==None:return None
	try:
          res=json.load(res)
          return res
        except Exception as ex:
          if self.logger!=None:
              exMessage=ExceptionLogMessage(
                moduleN=self.moduleName,
                dtime=datetime.now(),
                classN=self.className,
                methodN="loadResponseJSON",
                descr=str(ex),
                details={"word":qword,"mess":"failed to parse to json"}
              )
              self.logger.log(exMessage)
          return None
""" classes that store response ojects
    theres 3 type of Words we take care of in this application
	- Noun
	- Verb
	- Adj
    YandexTrWord is the general class 
    other classes inherits from YandexTrWord
	- YandexTrNoun
	- YandexTrVerb
	- YandexTrAdj
"""
class YandexTrWord(GeneralClass):
    word=None
    type=None
    def __init__(self,word,type):
        self.word=word
        self.type=type
    def getWord(self):
	return self.word
    def getType(self):
	return self.type
    def getAsp(self):
	return '_'
    def getGender(self):
	return '_'
    def display(self):
        print 'Word:',self.word
        print 'Type:',self.type
class YandexTrVerb(YandexTrWord):
    asp=None
    def __init__(self,word,type,asp):
        YandexTrWord.__init__(self,word,type)
        self.asp=asp
    def getAsp(self):
	return self.asp
    def display(self):
	YandexTrWord.display(self)
	print 'Asp:',self.asp
class YandexTrNoun(YandexTrWord):
    gender=None
    def __init__(self,word,type,gen):
        YandexTrWord.__init__(self,word,type)
        self.gender=gen
    def getGender(self):
	return self.gender
    def display(self):
        YandexTrWord.display(self)
        print 'Gender',self.gender
class YandexTrAdj(YandexTrWord):
    def __init__(self,word,type):
        YandexTrWord.__init__(self,word,type)
    def display(self):
        YandexTrWord.display(self)

def getWordFactory(parser):
    """ takes object of type YandexTrParser 
	and returns object of type YandexTrWord 
	
	selection accurate type of subclass according to type
	of the word
    """
    if not isinstance(parser,YandexTrParser):
	return None
    word,type=parser.getOrg(),parser.getType()
    if word==None:
	return None
    if type=='vrb':
	asp=parser.getAsp()
	return YandexTrVerb(word,type,asp)
    elif type=='nn':
	gen=parser.getGen()
	return YandexTrNoun(word,type,gen)
    elif type=='adj':
	return YandexTrAdj(word,type)
    else:
	return YandexTrWord(word,type)

""" unit test for classes in this module """
class testHelpers(unittest.TestCase):
    def test_ConfigDataWithLog(self):
	testWord='красивая'
	testOrg=u'красивый'
	testAsp=None
	testGen=None
	testType='adj'

	cfg=ConfigData('settings.cfg')
	uri=cfg.getValue("YANDEX_TRANSLATE_URL")

        logFile='test.log'
        logger=Logger(logFile)

	yndxApi=YandexTranslationAPI(uri)
	yndxApi.setLogger(logger)

	rjson=yndxApi.getResponseJSON(testWord)
	
	parser=YandexTrParser(rjson)
	word=getWordFactory(parser)

	self.assertEqual(parser.getOrg(),testOrg)
	self.assertEqual(parser.getType(),testType)
	self.assertEqual(parser.getAsp(),testAsp)
	self.assertEqual(parser.getGen(),testGen)
	self.assertEqual(isinstance(word,YandexTrAdj),True)

if __name__ == '__main__':
    unittest.main()
