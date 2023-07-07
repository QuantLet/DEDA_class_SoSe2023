import os 
import re
import pandas as pd
import gc


# Import PDF reading functionality
import pdfplumber 

# Import and set up plotting
import matplotlib.pyplot as plt
plt.rcParams['figure.figsize'] = (12, 6.75)
plt.rcParams['font.size'] = 28
plt.style.use('seaborn-v0_8-white')

# Importing Natural Language Toolkit
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer

def download_nltk_data():
    nltk_data = [("corpora", "stopwords"), ("tokenizers", "punkt"),
                 ("taggers", "averaged_perceptron_tagger"), ("corpora", "wordnet")]
    for package_id, package_name in nltk_data:
        try:
            nltk.data.find(f'{package_id}/{package_name}')
        except LookupError:
            nltk.download(package_name)

download_nltk_data()

# Define lemmatizer separately
# with POS Tag (Parts of Speech tagging)
# (function borrowed from ADAMS course)
def get_wordnet_pos(word):
    """Map POS tag to first character for lemmatization"""
    tag = nltk.pos_tag([word])[0][1][0].upper()
    tag_dict = {"J": wordnet.ADJ,
                "N": wordnet.NOUN,
                "V": wordnet.VERB,
                "R": wordnet.ADV}

    return tag_dict.get(tag, wordnet.NOUN)


def preprocess_text(first_input_folder = None, theses = None, inter_output_folder = None, verbose = False):
    """
    Preprocesses the PDF files by making everything lowercase,
    getting rid of non-alphabetic words, removing stopwords,
    tokenizing, lemmatizing, removing words with less than 3 character.

    Args:
        first_input_folder (str): Path to the folder containing the PDF files.
        
        theses: os.listdir(folder).
                
        inter_output_folder (str): Intermediate output folder to save the filtered theses.
                
        verbose (bool): Returns vizualizations and information about dimensionality reduction. Can be set to False to save computational power, memory and time when working with large corpora of files.

    Returns:
        None. Filthered theses saved in new folder.
    """

    print("Current working directory: {0}".format(os.getcwd()))
    
    # Empty containers needed for vizualization (deactivated if verbose = False)
    if verbose:
        
        # List for all tokens (including single-letter words)
        tokens_w_shortwords = []
                
        # List for all tokens (including stopwords but excluding single-letter words) to vizualize later
        tokens_w_stopwords = []
        
        # List for all tokens (excluding stopwords) to vizualize later
        tokens_wo_stopwords = []
                
        # Empty container for all tokens after processing steps
        tokens_processed = []
        
        # set up viz folder
        viz_folder = os.path.join(os.getcwd(), 'Plots')
        os.makedirs(viz_folder, exist_ok = True)
    
    # Empty container for filtered theses
    filtered_theses = []
    
    # Initialize lemmatizer
    lemmatizer = WordNetLemmatizer()  
    
    # Set up 
    # Set up stop words (i.e. "I", "me", "you", "the", etc.) from English 
    # save as stop_words
    stop_words = set(stopwords.words('english'))
    
    # Update stopwords with common words like figure, table, references, etc all papers share.
    stop_words.update(['cid', 'et', 'al', 'ef', 'ij', 'aj', 'berlin', 'humboldt', 'university', 'l', 'll', 'lll', 'llll', 'lllll', 'llllll', 'lllllll', 'llllllll', 'lllllllll', 'llllllllll', 'lllllllllll', 'llllllllllll', 'lllllllllllll', 'llllllllllllll', 'lllllllllllllll', 'llllllllllllllll', 'lllllllllllllllll', 'llllllllllllllllll', 'lllllllllllllllllll', 'llllllllllllllllllll', 'acknowledgement', 'abstract', 'introduction' 'conclusions', 'references', 'appendix', 'figure', 'table', 'tables', 'figures'])       
    
    # Note, the list was further updated to fit the specific data and address pdf reading issues
    
    for thesis in theses:
        
        with pdfplumber.open(f"{first_input_folder}/{thesis}") as pdf:
            my_list = []
            
            print(f'Currently working on {thesis}.')
            for page in pdf.pages:
                
                # Set up variable to hold text
                my_list.append(page.extract_text())                


            # Classic preprocessing steps
            # Container for filtered pages
            filtered_pages = []
            
            # Iterate
            for page in my_list:
                
                # Step 1)
                # Make everything on the page lower case;
                # save as page_lower_case
                page_lower_case = page.lower()

                # Step 2) 
                # Remove anything that is not (^) an alphabetic letter (a-zA-Z);
                # save as only_alphabetic
                only_alphabetic = re.sub("[^a-zA-Z]+", " ", page_lower_case)                     
                
                # Step 3)
                # Tokenize the alphabetic entries (words)
                # save as word_tokens
                word_tokens = word_tokenize(only_alphabetic)
                
                # Here the if verbose: conditions begin to ensure memory saving 
                # when verbose = False
                
                # If verbose = true, save all word tokens and use them for viz
                if verbose:
                    # Put tokens that include single-letter words in a list
                    tokens_w_shortwords.extend(word_tokens)
                
                # Step 4) 
                # Keep tokens only if 2 <= len(token) <20
                # This makes sure to remove strange words that may end up in our text
                # Due to pdf reading errors                
                
                # If verbose = true, we will save the tokens (excluding strange words) 
                # in a new list and keep them for viz
                if verbose:
                    noshort_tokens = [w.strip() for w in word_tokens if 2 <= len(w.strip()) < 20]
                    # Put word tokens (w/o stopwords) in a list 
                    tokens_w_stopwords.extend(noshort_tokens)
                    
                # If verbose = False, we will simply overwrite the previous variable to save memory
                else:
                    word_tokens = [w.strip() for w in word_tokens if 2 <= len(w.strip()) < 20]

                # Step 5) 
                # Keep word_tokens only if the word is not in stop words
                
                # If verbose = true, we will save the tokens (excluding stopwords)
                # in a new variable and store it for viz
                if verbose:
                    nonstopword_tokens = [w for w in noshort_tokens if not w.lower() in stop_words]
                    tokens_wo_stopwords.extend(nonstopword_tokens)
                    
                # If verbose = False, just overwrite previous variable
                else:
                    word_tokens = [w for w in word_tokens if not w.lower() in stop_words]
                
                # Step 7)
                # Lemmatize words with part of speech tagging
                
                # If verbose = True, save tokens in a new variable
                # and store it for viz
                if verbose:
                    lemmatized_tokens = [lemmatizer.lemmatize(i, get_wordnet_pos(i)) for i in nonstopword_tokens]
                    tokens_processed.extend(lemmatized_tokens)
                
                # Else, overwrite previous variable
                else:
                    word_tokens = [lemmatizer.lemmatize(i, get_wordnet_pos(i)) for i in word_tokens]
                
                # Join words, save as filtered sentence (further fail-safe against short words)
                if verbose:
                    filtered_sentence = " ".join([w for w in lemmatized_tokens if len(w) >= 2])
                    
                else:
                    filtered_sentence = " ".join([w for w in word_tokens if len(w) >= 2])                
                # The verbose condition ends for prepocessing 
    
                # Append filtered sentence into filtered page
                filtered_pages.append(filtered_sentence)

            # Save filtered pages as a filtered thesis
            filtered_thesis = " ".join(filtered_pages)
            
            # Append individual filtered theses
            filtered_theses.append(filtered_thesis)

            
            # Save filtered theses into the output folder
            with open(os.path.join(inter_output_folder, f"filtered {thesis}.txt"), "w") as output:
                output.write(filtered_thesis)
        
        del my_list
        gc.collect()
                
                
            
    # Vizualization section begins (only activated if verbose = True)            
    if verbose:
        
        # Plot the distribution of word lengths before removing single-character words
        # Use list comprehension: 
        # Make Pandas series with length of tokens for tokens in tokens (incl. single character words)
        pd.Series([len(token) for token in tokens_w_shortwords]).value_counts().sort_index().plot(kind='bar')
        plt.title('Distribution of word lengths')
        plt.xlabel('Length')
        plt.xlim(0,30)
        plt.ylabel('Amount of Words')
        plt.savefig(os.path.join(viz_folder, 'lengths_dist_w_shortwords.png'), transparent=True, dpi = 300)
        plt.show()
        plt.close()
        print('\n')
        print(f'Total amount of words before dropping single character words: {len(tokens_w_shortwords)} ')
        print('\n')

        
        # Plot the distribution of word lengths after removing single-character words
        pd.Series([len(token) for token in tokens_w_stopwords]).value_counts().sort_index().plot(kind = 'bar')
        plt.title('Distribution of word lengths')
        plt.xlabel('Length')
        plt.ylabel('Amount of Words')
        plt.savefig(os.path.join(viz_folder, 'lengths_dist_wo_shortwords.png'), transparent=True, dpi = 300)
        plt.show()
        plt.close()
        print('\n')
        print(f'Total amount of words after dropping single character words and other pdf reader mistakes: {len(tokens_w_stopwords)} ')
        print('\n')
        
        
        # Plot five most common words (including stopwords - uses same variable as the previous plot)
        pd.Series(tokens_w_stopwords).value_counts()[:5].plot(kind = 'bar',
                                                                 title = 'Five Most Frequent Words Before Removing Stopwords')
            
        # Save in the output folder 
        plt.savefig(os.path.join(viz_folder, 'word_dist_w_stopwords.png'), transparent=True, dpi = 300)
        # Show plot
        plt.show()
        # Close plot
        plt.close()
        print('\n')
        print(f'Total amount of words before removing stopwords: {len(tokens_w_stopwords)}')
        print('\n')

        # Plot five most common words (excluding stopwords)
        pd.Series(tokens_wo_stopwords).value_counts()[:5].plot(kind = 'bar',
                                                              title = 'Five Most Frequent Words After Removing Stopwords')
        plt.savefig(os.path.join(viz_folder, 'word_dist_wo_stopwords.png'), transparent = True, dpi = 300)
        # Show plot
        plt.show()
        # Close plot
        plt.close()
        print('\n')
        print(f'Total amount of words after removing stopwords: {len(tokens_wo_stopwords)}')
        print('\n')
                
        # Plot distribution of word frequencies
        pd.Series(tokens_processed).value_counts().value_counts().sort_index().plot(kind='line')
        plt.title('Distribution of Word Frequencies')
        plt.xlabel('Frequency')
        plt.ylabel('Words')
        plt.savefig(os.path.join(viz_folder, 'words_frequency_distribution.png'), transparent = True, dpi = 300)
        plt.show()
        plt.close()
        print('\n')
        
        # Plot a histogram to see how many words we have under 10 smalles frequencies
        pd.Series(tokens_processed).value_counts().value_counts().sort_index()[:10].plot(kind='bar')
        plt.title('Distribution of Word Frequencies: 10 Smallest')
        plt.xlabel('Frequency')
        plt.ylabel('Words')
        plt.savefig(os.path.join(viz_folder, 'words_frequency_distribution_smallest.png'), transparent = True, dpi = 300)
        plt.show()
        plt.close()
        print('\n')
        
        
        del tokens_w_shortwords
        del tokens_w_stopwords
        del tokens_wo_stopwords
        del tokens_processed
        gc.collect()
        
        # Viz section ends
    
    print('Preprocessing succesfully completed.')
    print('\n')