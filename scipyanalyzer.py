#Mineracao de dados
import pickle
import nltk
import string
import operator
import unicodedata
import kmeans

p = nltk.PorterStemmer()

normalize = lambda x:  unicodedata.normalize("NFKD", x).encode('ascii', 'ignore')

inp = open('scipydata.pk1','rb')
data = pickle.load(inp)

#Analyze the authors
authors = {}
for lecture in data:

	if lecture['title'].startswith('PiCloud'):
			lecture['title'] = 'PiCloud - Cloud Computing for Science. Simplified'
			lecture['authors'] = ['Ken Elkabany', 'Aaron Staley', 'Ken Park']
	for author in lecture['authors']:
		authors.setdefault(author,0)
		authors[author]+=1

#print authors

def getWords(text):
	#Parse the statuses and returns the list of words for each text
	
	#Create the stop words list
	stopwords = nltk.corpus.stopwords.words('english')
	stopwords = map(lambda w: unicode(w, 'utf-8'), stopwords)
	
	#Split the words by spaces
	words = text.split(" ")
	
	#Remove all illegal characters and convert to lower case
	RemoveWords = string.punctuation
	for item in RemoveWords:
		words = [word.replace(item,'') for word in words]
	#words = map(normalize,words)
	words = filter(lambda word: not word.isdigit(), words)
	words = filter(lambda word: word != '', words)
	words = [word.lower() for word in words]
	words = filter(lambda word: not word in stopwords, words)
	words = [ p.stem(word) for word in words ]

	return words



lectures = []
keywords = []


'''
f = open('keywords.txt','w')

for lecture in data:
	tags = getWords(lecture['title'])
	tgs = " ".join(tags)
	tgs+= ' '
	f.write(tgs)

f.close()
'''

keywords_class = []

#Let's hack the code!!
for lecture in data:
	tags = getWords(lecture['title'])
	keywords.extend(tags)
	lectures.append(lecture['title'])
	keywords_class.append(tags)

wordList = []

for tag in keywords:
	if tag not in wordList and tag not in [ 'python', 'keynote', 'using','building', 'computing' ]:
		wordList.append(tag)

keywords2 = []
i = 0

for tags in keywords_class:
	keywords2.append([])
	for word in wordList:
		if word in tags:
			keywords2[i].append((word,1))
		else:
			keywords2[i].append((word,0))
	i+=1

	
g = kmeans.open_ubigraph_server()
result,clusters = kmeans.kcluster(g,lectures,keywords2,k=8)

dataClusters = []
i = 0
for cluster in result:
	apCount = {}
	for indice in cluster:
		dados = keywords2[indice]
		for word,count in dados:
			apCount.setdefault(word,0)
			apCount[word]+= count
	words = apCount.items()
	words.sort(key=operator.itemgetter(1))
	words.reverse()
	print words
	print '====' 
	dataClusters.append(words[0:10])


kmeans.showResults(dataClusters)



'''

for dado in dados:
	tags =[]
	#tags = getWords(dado['tags'].decode('utf-8'))
	keys = dado['keys'].split(',')
	tags.extend(keys)
	#nivel = normalize(dado['nivel'].decode('utf-8').lower())
	#tags.append(nivel)
	palestrante =  normalize(dado['palestrante'].decode('utf-8'))
	palestrantes.append(palestrante)
	tags = list(set(tags))
	keywords.append(tags)


wordList = []

for user in keywords:
	for tag in user:
		if tag not in wordList:
			wordList.append(tag)

keywords2 = []
i = 0
for user in keywords:
	keywords2.append([])
	for word in wordList:
		if word in user:
			keywords2[i].append((word,1))
		else:
			keywords2[i].append((word,0))
	i+=1

	
g = kmeans.open_ubigraph_server()
result,clusters = kmeans.kcluster(g,palestrantes,keywords2,k=8)

dataClusters = []
i = 0
for cluster in result:
	apCount = {}
	for indice in cluster:
		dados = keywords2[indice]
		for word,count in dados:
			apCount.setdefault(word,0)
			apCount[word]+= count
	words = apCount.items()
	words.sort(key=operator.itemgetter(1))
	words.reverse()
	print words
	print '====' 
	dataClusters.append(words[0:10])


kmeans.showResults(dataClusters)


'''


"""
f = open('saida2.txt','w')

for dado in dados:
	tags = getWords(dado['tags'].decode('utf-8'))
	keys = dado['keys'].split(',')
	tags.extend(keys)
	tgs = " ".join(tags)
	f.write(tgs)

f.close()
"""

