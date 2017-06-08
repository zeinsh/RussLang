#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import unittest
import string
from fileoperationsmd import loadPKLData,savePKLData,readTxtFile
from textprocessingmd import getWordList
from datetime import datetime
from config import Config
from helpersmd import ConfigData,GeneralClass,getRequest
from loggermd import Logger,ExceptionLogMessage
from yandexapimd import getWordFactory,YandexTrWord,YandexTranslationAPI,YandexTrParser
from dictionarymd import Dictionary,WordOrigin,AdjTerm,VerbTerm,NounTerm
from dictionarymd import DictVerbsPF,DictVerbsIMPF,DictNouns,DictAdjs
import nltk
import urllib2
import json
from bs4 import BeautifulSoup
import xlwt
import collections

'''import collections
print collections.Counter(['a', 'b', 'c', 'a', 'b', 'b'])
print collections.Counter({'a':2, 'b':3, 'c':1})
print collections.Counter(a=2, b=3, c=1)
'''
# read text from file
# analyze and count terms
# remove terms with len<3
# get translation words
# get details of each type
# output to excel all
# output to excel for each type

#load configurations
cfg=ConfigData('settings.cfg')
uri=cfg.getValue("YANDEX_TRANSLATE_URL")
wiktionary=cfg.getValue("WIKTIONARY")
dctdata_dir=cfg.getValue("DICTIONARY_DATA")
worgdata_dir=cfg.getValue("WORDORIGIN_DATA")
dctvpf_dir=cfg.getValue("DICTVERBPF_DATA")
dctvimpf_dir=cfg.getValue("DICTVERBIMPF_DATA")
dctnouns_dir=cfg.getValue("DICTNOUNS_DATA")
dctadjs_dir=cfg.getValue("DICTADJS_DATA")

yndx=YandexTranslationAPI(uri)
logger=Logger('yndxapi.log')
yndx.setLogger(logger)

# Load pickle data
dictionary=loadPKLData(dctdata_dir)
if dictionary==None:
    dictionary=Dictionary()
wordOrigin=loadPKLData(worgdata_dir)
if wordOrigin==None:
    wordOrigin=WordOrigin()
dictVerbsPF=loadPKLData(dctvpf_dir)
if dictVerbsPF==None:
    dictVerbsPF=DictVerbsPF()
dicVerbsIMPF=loadPKLData(dctvimpf_dir)
if dicVerbsIMPF==None:
    dicVerbsIMPF=DictVerbsIMPF()
dictNouns=loadPKLData(dctnouns_dir)
if dictNouns==None:
    dictNouns=DictNouns()
dictAdjs=loadPKLData(dctadjs_dir)
if dictAdjs==None:
    dictAdjs=DictAdjs()

def getTrWords(wordList):
    ret=[]
    words=[]
    for w in wordList:
	term=w.encode('utf8').strip()
	org=wordOrigin.getOrigin(term)
    	if org!=None:
            term=str(org)
    	word=dictionary.getWord(term)
    	if word==None:
            res=yndx.getResponseJSON(term)
            pars=YandexTrParser(res)
            word=getWordFactory(pars)
	    if word==None:
		continue
            wordOrigin.addWordOrigin(word,org)
            dictionary.addWord(term,word)
	ret.append(word.getWord())
        words.append(word)
    return ret,words

def getTableVerb(term,asp,table):
   if asp=='pf':
        ret=dictVerbsPF.getTermData(term)
   elif asp=='im':
        ret=dicVerbsIMPF.getTermData(term)
   if ret!=None:
	return ret

   present=[]
   past=[]
   imp=[]
   try:
     soup =BeautifulSoup(str(table), "html.parser")
     trs=soup.findAll("tr")
     for i in range(1,7):
        soup=BeautifulSoup(str(trs[i]), "html.parser")

        tds=soup.findAll("td")
        ss=tds[1].text
        pp=tds[2].text
        mm=tds[3].text
        ss=ss.strip().replace('\n','\\')
        pp=pp.strip().replace('\n','\\')
        mm=mm.strip().replace('\n','\\')
        present.append(ss)
        if (i==4 or i==3):
           past.append(pp)
        if i==2 or i==5:
            imp.append(mm)
   except Exception as ex:
      print str(ex) 
      return None
   if len(present)==6:
       	ret=[term]+present+past+imp
	vt=VerbTerm(*ret)
	if asp=='pf':
	    dictVerbsPF.addVerb(term,vt)
	elif asp=='im':
	    dicVerbsIMPF.addVerb(term,vt)
	return vt
   else:
      return None

def getTableAdj(term,table):
   #print 'table',table
   m=[]
   try:
     soup =BeautifulSoup(str(table), "html.parser")
     trs=soup.findAll("tr")
     for i in range(2,10):
        soup=BeautifulSoup(str(trs[i]), "html.parser")
        tds=soup.findAll("td")
        if i in [5,6]:
            if i==5:
                p1=tds[2].text
                p2=tds[3].text
                p3=tds[4].text
                p4=tds[5].text
            if i==6:
                p1=tds[1].text
                p4=tds[2].text
        else:
            p1=tds[1].text
            p2=tds[2].text
            p3=tds[3].text
            p4=tds[4].text#       if i==2:
#          mm=soup.findall("td")[3].text
        p1=p1.strip().replace('\n','\\')
        p2=p2.strip().replace('\n','\\')
        p3=p3.strip().replace('\n','\\')
        p4=p4.strip().replace('\n','\\')
        m.append(p1)
        m.append(p2)
        m.append(p3)
        m.append(p4)
        #present.append(ss)
        #past.append(pp)
        #imp.append(mm)
   except Exception as ex:
      print 'ex',str(ex)
      return None
#   m=tuple(m)
   at=AdjTerm(*m)
   dictAdjs.addAdj(term,at)
   return at

def getTableNoun(term,table):
   sing=[]
   plur=[]
   try:
     soup =BeautifulSoup(str(table), "html.parser")
     trs=soup.findAll("tr")
     for i in range(1,len(trs)):
        soup=BeautifulSoup(str(trs[i]))
        ss=soup.findAll("td")[1].text
        pp=soup.findAll("td")[2].text
        ss=ss.strip().replace('\n','\\')
        pp=pp.strip().replace('\n','\\')
        sing.append(ss)
        sing.append(pp)
   except:
      return None
   if len(sing)>=6:
      nt=NounTerm(*sing)
      dictNouns.addNoun(term,nt)
      return nt
   else:
      return None

def processWord(word,type,asp):
   ret=None
   if type=='vrb':
      if asp=='pf':
          ret=dictVerbsPF.getTermData(word)
      elif asp=='im':
          ret=dicVerbsIMPF.getTermData(word)
   elif type=='adj':
	  ret=dictAdjs.getTermData(word)
   elif type=='nn':
          ret=dictNouns.getTermData(word)
   if ret!=None:
        return ret

   url=wiktionary+word
   try:
    html=getRequest(url)
    soup = BeautifulSoup(html, "html.parser")
    retAll=soup.findAll('table')

    for l in retAll:
       	if type=='vrb':
           ret=getTableVerb(word,asp,l)
	elif type=='nn':
	   ret=getTableNoun(word,l)
	elif type=='adj':
	   ret=getTableAdj(word,l)
       	if ret!=None:
	   return ret
           break
    s=ret[0]
    ret=[word.strip().decode('utf8')]+ret
    asp=getAspect(word)
    if asp=='pf':
      Data2.append(ret)
    else:Data1.append(ret)
   except Exception as ex:
    print word,ex


#adj=getTable('новый','adj',None)
#data=dictAdjs.getData()
#print data[dictAdjs.getColumnsNames()]
text=readTxtFile('input.txt')
wlist=getWordList(text)
trList,words=getTrWords(wlist)
counts=collections.Counter(trList)
for a in counts:
   dictionary.incTermCount(a,counts[a])
for w in words:
   processWord(w.getWord().encode('utf8'),w.getType(),w.getAsp())
print dictionary.getData()
#print dictVerbsPF.getData()
print dicVerbsIMPF.getData()
#verbsData=dictionary.getData()
#verbsData=verbsData.sort(['count'],ascending=[1])
#print verbsData

# save Dictionary


# save Data binary
savePKLData(dctdata_dir,dictionary)
savePKLData(worgdata_dir,wordOrigin)
savePKLData(dctvpf_dir,dictVerbsPF)
savePKLData(dctvimpf_dir,dicVerbsIMPF)
savePKLData(dctnouns_dir,dictNouns)
savePKLData(dctadjs_dir,dictAdjs)

