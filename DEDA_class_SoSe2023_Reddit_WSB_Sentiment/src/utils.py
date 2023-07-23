import pandas as pd
import numpy as np
from scipy.signal import detrend
import matplotlib.dates as mdates
from statsmodels.tsa.stattools import adfuller
import matplotlib.pyplot as plt


class TopPostsSelector(object):
    def __init__(self, df_posts, df_comments, cutoff_posts=0.9, cutoff_comments=0.8):
        self.posts = df_posts
        self.comments = df_comments

        self.cutoff_posts = cutoff_posts
        self.cutoff_comments = cutoff_comments

    def parser(self):
        posts = self.posts
        comments = self.comments

        posts['timestamp'] = pd.to_datetime(posts['timestamp']).dt.tz_localize('Etc/GMT+8') \
            .dt.tz_convert('America/New_York')
        posts['score'] = pd.to_numeric(posts['score'])
        posts['date'] = pd.to_datetime(posts['timestamp'].dt.strftime('%Y-%m-%d'))
        # posts['minute'] = np.where(posts['timestamp'].dt.minute< 30, '00', '30')
        # posts['date'] = pd.to_datetime(posts['date'].dt.strftime('%Y-%m-%dT%H') + ':' + posts['minute'])
        posts = posts[posts['date'] >= '2021-01-29']

        comments['score'] = pd.to_numeric(comments['score'])

        top_posts = posts.groupby(['date']) \
            .apply(lambda g: g[g['score'] >= np.quantile(g['score'], self.cutoff_posts)]) \
            .reset_index(drop=True)

        top_comments = comments[comments['id_col'].isin(top_posts['id'])] \
            .groupby('id_col') \
            .apply(lambda g: g[g['score'] >= np.quantile(g['score'], self.cutoff_comments)]) \
            .reset_index(drop=True)

        return top_posts, top_comments


class StockPipeLine(object):
    def __init__(self, df, only_last_call):
        self.df = df
        self.only_last_call = only_last_call

    def parser(self):
        df = self.df
        df = df.rename(columns={'Date': 'date'})
        df['date'] = pd.to_datetime(df['date']).dt.tz_localize('Europe/Berlin') \
            .dt.tz_convert('America/New_York')
        if self.only_last_call:
            df['hour'] = df['date'].dt.hour
            df['date'] = df['date'].dt.strftime('%Y-%m-%d')
            df = df.groupby('date') \
                .apply(lambda g: g[g['hour'] == np.max(g['hour'])]) \
                .reset_index(drop=True)
            df = df.drop('hour', axis=1)

        df['Last Price'] = pd.to_numeric(df['Last Price'].str.replace(',', '.'))

        df['close_lag'] = df['Last Price'].shift(1, axis = 0)
        df.loc[0,'close_lag'] = df.loc[1,'close_lag']
        df['first_diff'] = df['close_lag'] - df['Last Price']

        df['close_returns'] = (df['Last Price'] - df['close_lag'])/df['close_lag']
        df.loc[0,'close_returns'] = df['close_returns'].median()
        df = df.drop('close_lag', axis=1)

        return df


def sentiment_counts(df, relative=False):
    sent_date = df.groupby(['date', 'sent_label']).size().to_frame('size').reset_index() \
        .pivot(index='date', columns='sent_label', values='size').reset_index().fillna('0')
    sent_date[['negative', 'positive']] = sent_date[['negative', 'positive']].astype('int32')

    sent_date['date'] = sent_date['date'].dt.tz_localize('America/New_York')
    if relative is True:
        sent_date['tot'] = sent_date['negative'] + sent_date['positive']
        sent_date['negative'] = sent_date['negative'] / sent_date['tot']
        sent_date['positive'] = sent_date['positive'] / sent_date['tot']

    return sent_date


def sentiment_counts_plt(df, ax=None, relative=False, count_data=False):
    if not count_data:
        df = sentiment_counts(df, relative)

    if ax is None:
        ax = plt.gca()

    for col in ['negative', 'positive']:
        ax.plot(df['date'], df[col], label=col)

    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%b'))

    for label in ax.get_xticklabels(which='major'):
        label.set(rotation=30, horizontalalignment='right')

    return ax


def linear_detrend(df):
    p_val = {}
    for count in df.drop(['date', 'tot'], axis=1).columns:
        df[count] = detrend(df[count], type='linear')
        p = adfuller(df[count], autolag='AIC')[1]
        p_val[count] = p

    return df, p_val


def ccf_values(series1, series2):
    p = series1
    q = series2
    p = (p - np.mean(p)) / (np.std(p) * len(p))
    q = (q - np.mean(q)) / (np.std(q))
    c = np.correlate(p, q, 'full')
    return c


def ccf_plot(lags, ccf, stock_name, ax=None, title=False, x_lab=False):
    if ax is None:
        ax = plt.gca()

    ax.plot(lags, ccf)
    ax.axhline(-2/np.sqrt(23), color='red', label='5% confidence interval')
    ax.axhline(2/np.sqrt(23), color='red')
    ax.axvline(x = 0, color = 'black', lw = 1)
    ax.axhline(y = 0, color = 'black', lw = 1)
    ax.axhline(y = np.max(ccf), color='blue', lw=1,
               linestyle='--', label='highest +/- correlation')
    ax.axhline(y = np.min(ccf), color='blue', lw=1,
               linestyle='--')

    ax.set(ylim=[-1, 1], xlim=[-20, 20])
    if title:
        ax.set_title(stock_name, weight='bold', fontsize=15)
    ax.set_ylabel('Correlation Coefficients', weight='bold',
                  fontsize=12)
    if x_lab:
        ax.set_xlabel('Time Lags', weight='bold',
                      fontsize=12)


    return ax
