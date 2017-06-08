#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import unittest
from datetime import datetime
from config import Config
from helpersmd import ConfigData,GeneralClass
from loggermd import Logger,ExceptionLogMessage
from yandexapimd import getWordFactory,YandexTrWord,YandexTranslationAPI,YandexTrParser
import nltk
import urllib2
import json
from bs4 import BeautifulSoup
import xlwt
from pandas import DataFrame, read_csv
import pandas as pd
import operator
# class word/origin
class WordOrigin:
    def __init__(self):
	self.wordlist={}
    def setWordList(self,wordlist):
	self.wordlist=wordlist
    def getWordList(self):
	return self.wordlist
    def addWordOrigin(self,term,origin):
	self.wordlist[term]=origin
    def getOrigin(self,term):
        if not self.isInList(term):
	    return None
        return self.wordlist[term]
    def isInList(self,term):
	return term in self.wordlist.keys()

# class word/detailedWord
class Dictionary:
    wordlist=None
    termCount=None
    def __init__(self):
        self.wordlist={}
	self.termCount={}
    def setWordList(self,wordlist):
        self.wordlist=wordlist
    def getWordList(self):
        return self.wordlist
    def addWord(self,term,detailed):
	if isinstance(detailed,YandexTrWord):
            self.wordlist[term]=detailed
	    if term not in self.termCount.keys():
		self.termCount[detailed.getWord()]=0
    def getWord(self,term):
	if not self.isInList(term):
		return None
	return self.wordlist[term]
    def isInList(self,term):
        return term in self.wordlist.keys()
    def getWords(self,type):
	ret=[]
        for value in self.wordlist.values():
            if value!=None and (type==None or value.getType()==type):
		ret.append(value.getWord())
	return ret
    def getTypes(self,type):
	ret=[]
        for value in self.wordlist.values():
            if value!=None and (type==None or value.getType()==type):
                ret.append(value.getType())
        return ret
    def getGenders(self,type):
        ret=[]
	for value in self.wordlist.values():
            if value!=None and (type==None or value.getType()==type):
                ret.append(value.getGender())
        return ret
    def getAsps(self,type):
        ret=[]
        for value in self.wordlist.values():
	    if value!=None and (type==None or value.getType()==type):
                ret.append(value.getAsp())
        return ret
    def getCounts(self,type):
        ret=[]
        for value in set(self.wordlist.values()):
            if value!=None and (type==None or value.getType()==type):
	      if value.getWord() in self.termCount.keys():
                ret.append(self.termCount[value.getWord()])
	      else:
		ret.append('-')
        return ret
    def getData(self,type=None):
	words=self.getWords(type)
	counts=self.getCounts(type)
	types=self.getTypes(type)
	genders=self.getGenders(type)
	asps=self.getAsps(type)
	dicdata=list(zip(words,counts,types,genders,asps))
	df = pd.DataFrame(data = dicdata, columns=['term','count', 'type','gen','asp'])
	return df
    def incTermCount(self,term,c):
	#check int
	if term in self.termCount.keys():
	     self.termCount[term]+=c
	else:
	     self.termCount[term]=c

class DictPOS:
    dictionary={}
    columnsNames=[]
    def getColumn(self,n):
	ret=[]
	for key in self.dictionary.keys():
	     ret.append(self.dictionary[key].getColumn(n))
        return ret
    def getData(self):
	data={}
	n=len(self.columnsNames)
	for i in range(n):
	    colName=self.columnsNames[i]
	    colList=self.getColumn(i)
	    data[colName]=colList
	return pd.DataFrame(data)
    def getColumnsNames(self):
	return self.columnsNames
    def getTermData(self,term):
	if term in self.dictionary.keys():
	    return self.dictionary[term]
	else:
	    return None
class DictVerbsPF(DictPOS):
    def __init__(self):
        self.dictionary={}
        self.columnsNames=['verb',
                           'я','ты','он','мы','вы','они',
                           'он/она/оно про','они про',
                           'ты имп','вы имп']
    def addVerb(self,term,detailed):
        if isinstance(detailed,VerbTerm):
            self.dictionary[term]=detailed

class DictVerbsIMPF(DictPOS):
    def __init__(self):
        self.dictionary={}
	self.columnsNames=['verb',
                           'я','ты','он','мы','вы','они',
                           'он/она/оно про','они про',
                           'ты имп','вы имп']
    def addVerb(self,term,detailed):
        if isinstance(detailed,VerbTerm):
            self.dictionary[term]=detailed

class DictNouns(DictPOS):
    def __init__(self):
        self.dictionary={}
	self.columnsNames=['1s','1p','2s','2p','3s','3p',
			'4s','4p','5s','5p','6s','6p']
    def addNoun(self,term,detailed):
        if isinstance(detailed,NounTerm):
            self.dictionary[term]=detailed

class DictAdjs(DictPOS):
    def __init__(self):
        self.dictionary={}
	self.columnsNames=['1 муж. р.','1ср. р.','1жен. р.','1мн. ч.',
			   '2 муж. р.','2ср. р.','2жен. р.','2мн. ч.',
			   '3 муж. р.','3ср. р.','3жен. р.','3мн. ч.',
			   '4 муж. р.','4ср. р.','4жен. р.','4мн. ч.',
			   '5 муж. р.','5ср. р.','5жен. р.','5мн. ч.',
			   '6 муж. р.','6ср. р.','6жен. р.','6мн. ч.',]
    def addAdj(self,term,detailed):
        if isinstance(detailed,AdjTerm):
            self.dictionary[term]=detailed

class DictItem:
    lst=[]
    numElements=0
    def getColumn(self,n):
	if n>=0 and n<len(self.lst):
	    return self.lst[n]
	else:
	    return None

class VerbTerm(DictItem):
    def __init__(self,*args):
        self.lst=[]
        for i in range(11):
            self.lst.append(args[i])

class AdjTerm(DictItem):
    def __init__(self,*args):
        self.lst=[]
        for i in range(24):
            self.lst.append(args[i])

class NounTerm(DictItem):
    def __init__(self,*args):
        self.lst=[]
        for i in range(12):
            self.lst.append(args[i])

""" unit test for classes in this module """
class testHelpers(unittest.TestCase):
    def test_WordOrigin(self):
	""" tests for WordOrigin Class """
	term="сделаю"
	origin="сделать"
	# add example word/origin
	wordOrigin=WordOrigin()
	wordOrigin.addWordOrigin(term,origin)
	# test 1 / check existance existed term
	inlist=wordOrigin.isInList(term)
	self.assertEqual(inlist,True)
	# test 2 / check retrieval origin term
	origin2=wordOrigin.getOrigin(term)
	self.assertEqual(origin2,origin)

	wordlist=wordOrigin.getWordList() # retrieve word list
	wordOrigin2=WordOrigin() # construct new object
	# test 3 / check existance unexisted term
	inlist2=wordOrigin2.isInList(term)
        self.assertEqual(inlist2,False)
	# test 4 / check retrieval origin unexisted term
	origint4=wordOrigin2.getOrigin(term)
	self.assertEqual(inlist2,False)
	# set previus word list
	wordOrigin2.setWordList(wordlist)
	# test 5 / check existance existed word in the new object list
	inlist3=wordOrigin2.isInList(term)
        self.assertEqual(inlist3,True)
	# test 6 / check retrieval origin term in the new object list
        origin3=wordOrigin2.getOrigin(term)
        self.assertEqual(origin3,origin)

    def test_Dictionary(self):
	"""tests for Dictionary class """
	words=[{"word":"делал","type":"vrb","asp":"im","gen":None}
        	,{"word": "сделал","type":"vrb","asp":"pf","gen":None}
        	,{"word":"сын","type":"nn","asp":None,"gen":"m"},
        	{"word":"новый","type":"adj","asp":None,"gen":None}]
	# construct dictionary and add words
	dictionary=Dictionary()
	for word in words:
	    trword=YandexTrWord(word["word"],word["type"])
	    dictionary.addWord(word["word"],trword)
	# test 1/check retrieval previous added words
	for word in words:
	    trword=dictionary.getWord(word["word"])
	    self.assertEqual(trword.getWord(),word["word"])
	# test 2 / check retrieval unexisted term
	nonexisted="non"
	trword=dictionary.getWord(nonexisted)
	self.assertEqual(trword,None)
	# new dictionary object and add previous object's word list
	wordList=dictionary.getWordList()
	dictionary2=Dictionary()
	dictionary2.setWordList(wordList)
	# test 3/check retrieval previous added words in new object
        for word in words:
            trword=dictionary2.getWord(word["word"])
            self.assertEqual(trword.getWord(),word["word"])
        # test 4 / check retrieval unexisted term in new dictionary object
        nonexisted="non"
        trword=dictionary2.getWord(nonexisted)
        self.assertEqual(trword,None)

if __name__ == '__main__':
    unittest.main()
