import nltk

def getWordList(text):
    text=text.decode('utf8')
    words = nltk.word_tokenize(text)
    ret=[w for w in words if len(w)>2]
    return ret


def decodeText(text):
    try:
         return str(text).decode('utf8')
    except:
         return text

def encodeText(text):
    try:
         return text.encode('utf8')
    except:
         return text
