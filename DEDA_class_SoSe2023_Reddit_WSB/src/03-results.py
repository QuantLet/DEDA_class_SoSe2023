import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from scipy.signal import correlation_lags
from utils import TopPostsSelector, sentiment_counts, sentiment_counts_plt,\
    linear_detrend, StockPipeLine, ccf_plot, ccf_values

df_posts = pd.read_csv('../data/senti_posts.zip').drop(6161)
df_comments = pd.read_csv('../data/senti_comments.zip', lineterminator='\n')

top_posts, top_comments = TopPostsSelector(df_posts, df_comments, cutoff_posts=0.8, cutoff_comments=0.75).parser()

top_comments = top_comments.merge(top_posts[['id', 'date']], left_on='id_col', right_on='id') \
    .drop('id', axis=1)

df_posts['hour_day'] = pd.to_datetime(df_posts['timestamp'].dt.strftime('%Y-%m-%dT%H'))

df_comments = df_comments \
    .merge(df_posts[['id', 'timestamp']], left_on='id_col', right_on='id') \
    .drop('id', axis=1)

df_comments['hour_day'] = pd.to_datetime(df_comments['timestamp'].dt.strftime('%Y-%m-%dT%H'))

df_posts = df_posts[df_posts['timestamp'] >= '2021-01-29']
df_comments = df_comments[df_comments['timestamp'] >= '2021-01-29']
print('Data loading process completed')

col_name = ['hour_day', 'count']

num_posts = df_posts.groupby('hour_day')['id'].nunique().reset_index()
num_posts.columns = col_name

num_comments = df_comments.groupby('hour_day').size().to_frame().reset_index()
num_comments.columns = col_name

day_of_squeeze = num_posts[num_posts['count']==np.max(num_posts['count'])]['hour_day'].to_list()[0]
peak_comments = num_comments[num_comments['count']>=np.max(num_comments['count'])]['hour_day'].to_list()[0]

# Fig 1: Number of posts and comments
plt.rcParams["figure.figsize"] = [10, 5]
fig, ax = plt.subplots(2, 1, sharex = True)

ax[0].plot(num_posts['hour_day'], num_posts['count']/1000)
ax[0].set_ylabel('Number of Posts\n(by Thousands)', fontsize=8)
ax[0].annotate('29th of January', xy=(day_of_squeeze, np.max(num_posts['count']/1000)),
               xytext=(4.5, -5.5), textcoords='offset points', color='crimson')

ax[1].plot(num_comments['hour_day'], num_comments['count']/1000)
ax[1].set_ylabel('Number of Comments\n(by Thousands)', fontsize=8)
ax[1].set_xlabel('Submission Date')

ax[1].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%b'))

for axes in ax:
    axes.spines['top'].set_visible(False)
    axes.spines['right'].set_visible(False)

plt.xticks(fontsize=6)
for label in ax[1].get_xticklabels(which='major'):
    label.set(rotation=30, horizontalalignment='right')

plt.tight_layout()
fig.savefig('../img/n_posts_comments.png', transparent=True)
plt.close(fig)
print('Fig 1: Number of posts and comments finished!')

# Fig 2: Counts of sentiments for top posts and comments

fig, ax = plt.subplots(2, 1)
sentiment_counts_plt(top_posts, ax[0], relative=True)
sentiment_counts_plt(top_comments, ax[1], relative=True)

handles, labels = fig.gca().get_legend_handles_labels()
dict_of_labels = dict(zip(labels, handles))
handles, labels = list(dict_of_labels.values()), list(dict_of_labels.keys())
fig.legend(handles[::-1], labels[::-1], loc='upper right')
# fig.suptitle('Sentiment Proportions for top posts and comments')

for axes in ax:
    axes.spines['top'].set_visible(False)
    axes.spines['right'].set_visible(False)

plt.tight_layout()
fig.savefig('../img/sent_proportions.png', transparent=True)
plt.close(fig)

print('Fig 2: Sentiment proportions finished!')

# Fig 3: Detrended sentiment proportions

posts_count = sentiment_counts(top_posts, relative=True)
comments_count = sentiment_counts(top_comments, relative=True)

posts_count, p_posts = linear_detrend(posts_count)
comments_count, p_comments = linear_detrend(comments_count)

fig, ax = plt.subplots(2, 1)
sentiment_counts_plt(posts_count, ax[0], count_data=True)
sentiment_counts_plt(comments_count, ax[1], count_data=True)

handles, labels = fig.gca().get_legend_handles_labels()
dict_of_labels = dict(zip(labels, handles))
handles, labels = list(dict_of_labels.values()), list(dict_of_labels.keys())
fig.legend(handles[::-1], labels[::-1], loc='upper right')
# fig.suptitle('Sentiment Detrended Proportions for top posts and comments')

for axes in ax:
    axes.spines['top'].set_visible(False)
    axes.spines['right'].set_visible(False)

plt.tight_layout()
fig.savefig('../img/sent_proportions_detrended.png', transparent=True)
plt.close(fig)

print('Fig 3: Detrended Sentiment proportions finished!')

# Fig 4 : Stock and Sentiment correlations

df_amc = pd.read_csv('../stocks/AMC.csv')
df_gme = pd.read_csv('../stocks/GME.csv')
df_amc = StockPipeLine(df_amc, only_last_call=True).parser()
df_gme = StockPipeLine(df_gme, only_last_call=True).parser()

comments_count['date'] = comments_count['date'].dt.strftime('%Y-%m-%d')

df_sent_stock = comments_count.merge(df_amc[['date', 'close_returns']], on='date', how='left')
df_sent_stock = df_sent_stock[df_sent_stock['close_returns'].notnull()]

ccf_amc = ccf_values(df_sent_stock['positive'], df_sent_stock['close_returns'])
lags = correlation_lags(len(df_sent_stock['positive']), len(df_sent_stock['close_returns']))

fig, ax = plt.subplots(2, 1, figsize=[10, 10], sharex=True)
ccf_plot(lags, ccf_amc, 'AMC', ax=ax[0], title=True)

df_sent_stock = comments_count.merge(df_gme[['date', 'close_returns']], on='date', how='left')
df_sent_stock = df_sent_stock[df_sent_stock['close_returns'].notnull()]

ccf_gme = ccf_values(df_sent_stock['positive'], df_sent_stock['close_returns'])
lags = correlation_lags(len(df_sent_stock['positive']), len(df_sent_stock['close_returns']))

ccf_plot(lags, ccf_gme, 'GME', ax=ax[1], title=True, x_lab=True)
# fig.supxlabel('Time Lags', weight='bold', fontsize=12)
plt.tight_layout()
fig.savefig('../img/amc_gme_sent_corr.png', transparent=True)
plt.close(fig)
print('Fig 4`: AMC and GME Sentiment correlations finished!')
