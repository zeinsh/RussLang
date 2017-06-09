Welcome to the RussLang wiki!

I am collecting in this project scripts I used before while learning Russian Language . 
I wrote some scripts to automate my learning process , and get needed tables ,

P.S. Samples and Explanations will be added after finishing .

tokenize texts , return every word to origin
determine details about each word (type,aspect,gender...)
get conjugations of each word
classify and organize in tables
extract tables to external sheets
In this project , I used :

Yandex dictionary API
Data from ru.wiktionary.org
To minimize dependency on the Internet , The data are saved locally , and the connection will not 
be established unless they are not available locally .

Statistics are used to determine the most significant words to memorize , by sorting terms in dictionaries
by frequency descendingly .

The following tables will be provided :

dictionary : term/type/aspect/gender
im/perfective verbs and their conjugations
adjectives and their cases
nouns singular/plural and cases
