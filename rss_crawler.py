# -*- coding: utf-8 -*-

import feedparser
import pprint
import re, time, html
import pickle
import os.path

import spacy

from nltk.corpus import stopwords
stop_words = stopwords.words('english')

from gensim import corpora
from gensim import similarities
from gensim.models import CoherenceModel
import gensim

def createCorpus(urls):
	val = []
	title = []
	rawData = []
	for url in urls:
		feed = feedparser.parse(url)
		for entry in feed['entries']:
			try:
				res = entry['content'][0]['value']
			except KeyError:
				res = entry['summary_detail']['value']
			while res[0] == ' ':
				res = res[1:]
			title.append(''.join(entry['title']))
			val.append(res)
			rawData.append(entry)
	return title, val, rawData

def clean(txt):
	tag_remover 	= re.compile(r'<[^>]+>|(@[A-Za-z0-9]+)|\.\.\.|Continue reading|(https?:\S*)|\?|\!')
	url_remover 	= re.compile(r'((?:[\w-]+\.)+[a-z]{3,6}/([A-Za-z0-9]+))|\S*@\S*')
	script_remover 	= re.compile(r'<script(.*)/script>')
	space_remover 	= re.compile(r'^\s+|\s+$|\s+(?=\s)')
	char_replacer 	= re.compile(r'\uFFFF')

	rm_space 	= lambda txt: space_remover.sub('', txt)
	rm_url 		= lambda txt: url_remover.sub('', txt)
	rm_tag 		= lambda txt: tag_remover.sub('',txt)
	rm_script 	= lambda txt: script_remover.sub('', txt)
	replace_n 	= lambda txt: char_replacer.sub(' ', txt.replace('\n',u'\uFFFF'))
	return rm_space(
		rm_url(
			rm_tag(
				rm_script(
					replace_n(txt)
				)
			)
		)
	).lower()

def tokenize(sentences):
	for sentence in sentences:
		yield(gensim.utils.simple_preprocess(str(sentence), deacc=True))

def remove_stopwords(texts):
	return [[word for word in gensim.utils.simple_preprocess(str(doc)) if word not in stop_words] for doc in texts]


pp = pprint.PrettyPrinter(indent=4)

with open('newslist.txt') as file:
	urls = list(map(lambda t: t.replace('\n',''), file.readlines()))

def crawl(topic, limit):
	def make_bigrams(texts):
		return [bigram_mod[doc] for doc in texts]

	def make_trigrams(texts):
		return [trigram_mod[bigram_mod[doc]] for doc in texts]

	def lemmatization(texts, allowed_postags=['NOUN', 'ADJ', 'VERB', 'ADV']):
		texts_out = []
		for sent in texts:
			doc = nlp(" ".join(sent)) 
			texts_out.append([token.lemma_ for token in doc if token.pos_ in allowed_postags])
		return texts_out

	textData = []
	textTitle, textList, rawData = createCorpus(urls)
	for text in textList:
		text = clean(text)
		textData.append(text)
	tokens = list(tokenize(textData))

	bigram = gensim.models.phrases.Phrases(tokens, min_count=2, threshold=100)
	trigram = gensim.models.phrases.Phrases(bigram[tokens], threshold=100)

	bigram_mod = gensim.models.phrases.Phraser(bigram)
	trigram_mod = gensim.models.phrases.Phraser(trigram)

	nlp = spacy.load('en_core_web_sm', disable=['parser', 'ner'])

	tokens_nostops = remove_stopwords(tokens)
	tokens_bigrams = make_bigrams(tokens_nostops)

	data_lemmatized = lemmatization(tokens_bigrams, allowed_postags=['NOUN', 'ADJ', 'VERB', 'ADV'])
	textData = data_lemmatized
	dictionary = corpora.Dictionary(data_lemmatized)
	corpus = [dictionary.doc2bow(text) for text in textData]

	pickle.dump(corpus, open('corpus.pkl', 'wb'))
	dictionary.save('dictionary.gensim')
	pickle.dump(rawData, open('rawData.pkl', 'wb'))
	pickle.dump(textTitle, open('textTitle.pkl', 'wb'))
	pickle.dump(textList, open('textList.pkl', 'wb'))

	num_topics = len(urls)*10
	print('Num topics = {}'.format(num_topics))

	model = gensim.models.LdaModel(corpus, num_topics = num_topics, id2word=dictionary)
	model.save('model.gensim')

	with open('last.txt','w') as f:
		f.write('{}'.format(time.time()))
		f.close()

	# model = gensim.models.LsiModel(corpus, num_topics = num_topics, id2word=dictionary)
	# path = 'mallet/bin/mallet'
	# model = gensim.models.wrappers.LdaMallet(path, corpus=corpus, num_topics=num_topics, id2word=dictionary)

	# coherence_model = CoherenceModel(model=model, texts=textData, dictionary=dictionary, coherence='c_v')
	# coherence = coherence_model.get_coherence()
	# print('Coherence Score: ', coherence)

	topicTokens = list(tokenize([topic]))[0]
	bowTopic = dictionary.doc2bow(topicTokens)
	vecTopic = model[bowTopic]

	lda_idx = similarities.MatrixSimilarity(model[corpus])
	similarity = lda_idx[vecTopic]
	similarity = sorted(enumerate(similarity), key=lambda item: -item[1])

	# index = np.sqrt(matutils.corpus2dense((model[doc] for docno, doc in enumerate(corpus)), model.num_topics).T)
	# q = np.sqrt(matutils.sparse2full(vecTopic, model.num_topics))
	# similarity = np.sqrt(0.5 * np.sum((q - index)**2, axis=1))
	# similarity = sorted(enumerate(similarity), key=lambda x: -x[1])
	# print similarity[:10]

	res = []
	for doc_id, sim in similarity[:limit]:
		if(sim > 0.5):
			res.append({
				'title': html.unescape(textTitle[doc_id]),
				'content': html.unescape(clean(textList[doc_id])),
				'link' : rawData[doc_id]['link'],
				'similarity': sim,
				'doc_id': doc_id
			})
	pp.pprint(res)

	return res

def query(topic, limit):

	dictionary = gensim.corpora.Dictionary.load('dictionary.gensim')
	corpus = pickle.load(open('corpus.pkl', 'rb'))
	model = gensim.models.LdaModel.load('model.gensim')

	rawData = pickle.load(open('rawData.pkl', 'rb'))
	textList = pickle.load(open('textList.pkl', 'rb'))
	textTitle = pickle.load(open('textTitle.pkl', 'rb'))

	topicTokens = list(tokenize([topic]))[0]
	bowTopic = dictionary.doc2bow(topicTokens)
	vecTopic = model[bowTopic]

	lda_idx = similarities.MatrixSimilarity(model[corpus])
	similarity = lda_idx[vecTopic]
	similarity = sorted(enumerate(similarity), key=lambda item: -item[1])

	res = []
	for doc_id, sim in similarity[:limit]:
		if(sim > 0.5):
			res.append({
				'title': html.unescape(textTitle[doc_id]),
				'content': html.unescape(clean(textList[doc_id])),
				'link' : rawData[doc_id]['link'],
				'similarity': sim,
				'doc_id': doc_id
			})
	pp.pprint(res)
	return res

if __name__ == '__main__':
	crawl('trump', 5)