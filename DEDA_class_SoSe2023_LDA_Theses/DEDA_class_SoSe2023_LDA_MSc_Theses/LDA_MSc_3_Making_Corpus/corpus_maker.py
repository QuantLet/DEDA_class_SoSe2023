import os
import re
import pandas as pd
import pickle
from gensim import corpora
from nltk.tokenize import word_tokenize
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from sklearn.feature_extraction.text import TfidfVectorizer
from yellowbrick.text import UMAPVisualizer
from umap.umap_ import UMAP
import umap.plot
from sklearn.feature_extraction.text import TfidfVectorizer

class CorpusMaker:
    '''
    A class used for turning the filtered LvB MSc theses into a corpus. Generally, this class can also be used to generate a corpus from any set of .txt files that have already gone through standard NLP preprocessing. 
    
    Outputs are saved as pickle files in automatically generated folder DICT_CORP.
    
    Args:
        input_folder (str): The folder containing the filtered MSc theses. (Should set to the output of the preprocessing function)
        
    Attributes:
        dictionary: A dictionary generated using Gensim.
        dictionary_token2id: A mapping of tokens to IDs.
        corpus: BoW corpus generated from the theses. 
        texts: All tokens (used for coherence later on)
        dates: Returns dates list for theses
        
    Methods:
        make_corpus: Processes the filtered theses texts, drops rare words overall, creates corpus.
        show_top_words: Prints the most frequent words per thesis in the corpus.
        make_wordcloud: Generates a wordcloud image from the corpus.
        make_UMAP: applies UMAP to term frequencies for dimensionality reduction and visualizes as 2d graph.
    '''
    
    
    def __init__(self, input_folder):
        self.input_folder = input_folder
        self.dictionary = None
        self.dictionary_token2id = None
        self.corpus = None
        self.texts = None
        self.dates = None

    def make_corpus(self):
        '''
        Processes the already filtered theses and creates a corpus. Outputs are saved as pickle files for further use. 

        Returns:
            dictionary, dictionary_token2id, corpus

        '''

        print('\nCreating corpus...')

        theses = os.listdir(self.input_folder)
        
        #sorts theses according to their date of publishing
        dates = {}

        for thesis_name in theses:
            date = thesis_name[-18:-8]
            dates[thesis_name] = date.split('-')

        sorted_dates = sorted(dates.items(), key=lambda x: x[1])
        sorted_dates_dict = dict(sorted_dates)

        theses = list(sorted_dates_dict.keys())
        
        # Load and tokenize filtered documents

        # Initialize empty list
        filtered_theses = []

        # Iterate over thesis in theses
        for thesis in theses:

            # Open file in read mode
            with open(os.path.join(self.input_folder, thesis), 'r') as file:

                # Define filtered thesis as the file.read
                filtered_thesis = file.read()

                # Append to the filtered_theses list
                filtered_theses.append(filtered_thesis)

        # Tokenize:

        # Get a list of lists that includes tokens for every thesis 
        theses_tokens = [word_tokenize(filtered_thesis) for filtered_thesis in filtered_theses]

        # Flatten into a list including all tokens
        tokens_overall = [token for thesis_list in theses_tokens for token in thesis_list]

        # Get the token distribution and drop out words mentioned less than three times
        tokens_distribution = pd.Series(tokens_overall).value_counts()
        tokens_distribution_wo_rare_words = tokens_distribution[tokens_distribution > 2]
        theses_tokens_wo_rare_words = [[token for token in thesis if token in tokens_distribution_wo_rare_words] for thesis in theses_tokens]

        print(f'\nAfter removing {sum(tokens_distribution) - sum(tokens_distribution_wo_rare_words)} rare words, total amount of words in the preprocessed texts decreased from {sum(tokens_distribution)} to {sum(tokens_distribution_wo_rare_words)}')    

        # Create texts
        self.texts = theses_tokens_wo_rare_words
        
        # Create dictionary
        self.dictionary = corpora.Dictionary(theses_tokens_wo_rare_words)

        # Create ID mappng
        self.dictionary_token2id = self.dictionary.token2id

        # Create corpus
        self.corpus = [self.dictionary.doc2bow(thesis_tokens) for thesis_tokens in theses_tokens_wo_rare_words]

        # Create dates
        self.dates = list(sorted_dates_dict.values())
        # Pickle the data and save into output folder
        
        # Set up folder
        if not os.path.exists('DICT_CORP'):
            os.makedirs('DICT_CORP')
        
        # Save dictionary
        with open(os.path.join('DICT_CORP', 'dictionary.pkl'), 'wb') as file:
            pickle.dump(self.dictionary, file)
        
        # Save ID mapping
        with open(os.path.join('DICT_CORP', 'dictionary_token2id.pkl'), 'wb') as file:
            pickle.dump(self.dictionary_token2id, file)
        
        # Save corpus
        with open(os.path.join('DICT_CORP', 'corpus.pkl'), 'wb') as file:
            pickle.dump(self.corpus, file)
        
        # Save tokens
        with open(os.path.join('DICT_CORP', 'texts.pkl'), 'wb') as file:
            pickle.dump(self.texts, file)

        # Save dates
        with open(os.path.join('DICT_CORP', 'dates.pkl'), 'wb') as file:
            pickle.dump(self.dates, file)
        
        print('\nCorpus succesfully created.')

        return self.dictionary, self.dictionary_token2id, self.corpus, self.texts, self.dates


    def show_top_words(self, amount):
        '''
        Small function to print most frequent words per document in corpus.

        '''
        for i, thesis in enumerate(self.corpus):
            print(f"\nThesis {i+1}")
            sorted_thesis = sorted(thesis, key=lambda x: x[1], reverse=True)
            for id, freq in sorted_thesis[:amount]:
                print(f"\n{self.dictionary[id]}: {freq}")
            print() 

    def make_wordcloud(self):
        '''
        Small function to generate a wordcloud image for the corpus.
        
        '''

        word_freq = {}
        # Calculate word frequencies for theses in corpus and dictionary
        for thesis in self.corpus:
            for id, frequency in thesis:
                word = self.dictionary[id]

                if word in word_freq:
                    word_freq[word] += frequency
                else:
                    word_freq[word] = frequency

        wordcloud = WordCloud(width = 960, height = 720, background_color ="rgba(255, 255, 255, 0)", mode="RGBA", random_state = 66).generate_from_frequencies(word_freq)

        plt.figure(figsize=(19.2, 14.4))
        plt.imshow(wordcloud)
        plt.axis('off')
        
        if not os.path.exists('Plots'):
            os.makedirs('Plots')
        
        plt.savefig('MSc_Wordcloud.png', transparent = True, dpi = 300)
        plt.show()
        plt.close()
        
    def make_UMAP(self):
        '''
        Small function to generate UMAP visualization of terms distribution
        '''
        
        docs = []
                
        for thesis_list in self.texts:
            docs.extend(thesis_list)

        # Create an instance of TfidfVectorizer
        vectorizer = TfidfVectorizer()

        # Fit and transform the corpus using TF-IDF vectorization
        tfidf_matrix = vectorizer.fit_transform(docs)
        
        # Apply UMAP and plot results
        mapper = UMAP(random_state=66).fit(tfidf_matrix)
        umap.plot.points(mapper)
        plt.savefig('UMAP terms.png', transparent = True, dpi = 300)
        plt.show()
        plt.close()