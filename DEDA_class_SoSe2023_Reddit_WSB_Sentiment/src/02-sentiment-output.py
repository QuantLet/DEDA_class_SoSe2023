import pandas as pd
from transformers import AutoModelForSequenceClassification, pipeline
from typing import AnyStr

df_posts = pd.read_csv('../data/wallstreetbets.zip')
df_comments = pd.read_csv('../data/all_comments.zip')
sentiment_model = pipeline(model='mwkby/distilbert-base-uncased-sentiment-reddit-crypto')


class SentimentOutput(object):
    def __init__(self, model):
        self.model = model

        self.df = None
        self.kind = None
        self.col = None
        self.n_col = None

    def text_parser(self) -> None:
        if type(self.col) is not list:
            cols = [self.col]
        else:
            cols = self.col
        for col in cols:
            self.df[col] = self.df[col].fillna('')
            self.df[col] = self.df[col].str.replace(r'[\([{})\]]', '', regex=True)
            self.df[col] = self.df[col].str.replace(r'https?:\/\/.*[\r\n]*', '', regex=True)
            self.df[col] = self.df[col].str.replace(r'\n', '', regex=True)
            self.df[col] = self.df[col].str.replace(r'\\\*', '', regex=True)

        if self.kind == 'posts':
            self.df[self.n_col] = self.df['title'].str.cat(self.df['body'], sep=' ')

    def sentiment_cols(self) -> None:
        text = self.n_col if self.kind == 'posts' else self.col

        sent_ls = self.model(self.df[text].tolist(), truncation=True)
        self.df['sent_label'] = [dct['label'] for dct in sent_ls]
        self.df['sent_score'] = [dct['score'] for dct in sent_ls]

        if self.kind == 'posts':
            self.df = self.df.drop(self.n_col, axis=1)

    def __call__(self, df, kind, col, n_col):
        self.df = df
        self.kind = kind
        self.col = col
        self.n_col = n_col

        self.text_parser()
        self.sentiment_cols()

        return self.df


sentiment = SentimentOutput(model=sentiment_model)
print('Sentiment loaded')

sent_posts = sentiment(df_posts, 'posts', col=['title', 'body'], n_col='title-body')
sent_posts.to_csv('../data/senti_posts.zip', index=False, compression='zip')
print('Posts finished modelling!')

sent_comment = sentiment(df_comments, 'comments', col='comments', n_col=None)
sent_comment = sent_comment.groupby(['id_col', 'comments', 'score']).first().reset_index()
sent_comment.to_csv('../data/senti_comments.zip', index=False, compression='zip')
print('Comments finished modelling!')
