import gensim
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from nltk.tokenize import RegexpTokenizer

from NLP.InputPreprocessor import InputPreprocessor


class LatentDirichletAllocation:
    def __init__(self, doc_set):
        self.__doc_set = doc_set
        self.__preprocessor = InputPreprocessor(doc_set)

    def get_corpus_and_dictionary(self):
        texts = []

        tokenizer = RegexpTokenizer(r'\w+')

        # create English stop words list
        en_stop = stopwords.words('english')

        # Create p_stemmer of class PorterStemmer
        p_stemmer = PorterStemmer()

        for i in self.__doc_set:
            # clean and tokenize document string
            raw = i.lower()
            tokens = tokenizer.tokenize(raw)

            # remove stop words from tokens
            stopped_tokens = [i for i in tokens if not i in en_stop]

            # stem tokens
            stemmed_tokens = [p_stemmer.stem(i) for i in stopped_tokens]

            # add tokens to list
            texts.append(stemmed_tokens)

        # turn our tokenized documents into a id <-> term dictionary
        dictionary = gensim.corpora.Dictionary(texts)

        corpus = [dictionary.doc2bow(text) for text in texts]

        return corpus, dictionary

    def compute(self, topics, passes, save_filename):

        corpus, dictionary = self.get_corpus_and_dictionary()
        # generate LDA model
        ldamodel = gensim.models.LdaMulticore(corpus, num_topics=topics, id2word=dictionary, passes=passes, workers=3)

        save_filename += "_{}_{}".format(topics, passes)

        dictionary.save(save_filename + ".dict")
        gensim.corpora.MmCorpus.save_corpus(save_filename + ".mm", corpus, id2word=dictionary)
        ldamodel.save(save_filename + ".model")

        return ldamodel, corpus, dictionary
