import nltk

def getWordList(text):
    text=text.decode('utf8')
    words = nltk.word_tokenize(text)
    ret=[w for w in words if len(w)>2]
    return ret
