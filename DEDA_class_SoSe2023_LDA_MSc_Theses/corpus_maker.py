import os
import re
import pandas as pd
import pickle
from gensim import corpora
from nltk.tokenize import word_tokenize



def corpusmaker(input_folder = None, last_output_folder = None):
    '''
    Function processes the already filtered theses and creates a corpus. Outputs are saved as pickle files for further use. 
    
    Args:
        input_folder (str): The folder containing the filtered theses. Set to the output path of the preprocess_text function.
        last_output_folder (str): The folder to save the pickled data.
        
    Returns:
        dictionary, dictionary_token2id, corpus
    
    '''
    
    print('Creating corpus...')
    
    theses = os.listdir(input_folder)
    
    # Load and tokenize filtered documents
    
    # Initialize empty list
    filtered_theses = []
    
    # Iterate over thesis in theses
    for thesis in theses:
        
        # Open file in read mode
        with open(os.path.join(input_folder, thesis), 'r') as file:
            
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
    
    print(f'After removing {sum(tokens_distribution) - sum(tokens_distribution_wo_rare_words)} rare words, total amount of words in the preprocessed texts decreased from {sum(tokens_distribution)} to {sum(tokens_distribution_wo_rare_words)}')    
    
    # Create dictionary
    dictionary = corpora.Dictionary(theses_tokens_wo_rare_words)

    # Create ID mappng
    dictionary_token2id = dictionary.token2id
    
    # Create corpus
    corpus = [dictionary.doc2bow(thesis_tokens) for thesis_tokens in theses_tokens_wo_rare_words]
    
    # Pickle the data and save into output folder
    with open(os.path.join(last_output_folder, 'dictionary.pkl'), 'wb') as file:
        pickle.dump(dictionary, file)
    with open(os.path.join(last_output_folder, 'dictionary_token2id.pkl'), 'wb') as file:
        pickle.dump(dictionary_token2id, file)
    with open(os.path.join(last_output_folder, 'corpus.pkl'), 'wb') as file:
        pickle.dump(corpus, file)
    
    
    print('Corpus succesfully created.')

    return dictionary, dictionary_token2id, corpus


def topwords(corpus, dictionary, amount):
    '''
    Small function to print most frequent words per document in corpus.
        
    '''
    for i, thesis in enumerate(corpus):
        print(f"Thesis {i+1}")
        sorted_thesis = sorted(thesis, key=lambda x: x[1], reverse=True)
        for id, freq in sorted_thesis[:amount]:
            print(f"{dictionary[id]}: {freq}")
        print()  