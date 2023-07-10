import pandas as pd
import logging
from config import parse_args
import gc
from typing import Tuple
import praw
import yaml
from prawcore.exceptions import PrawcoreException
from praw.models import MoreComments
from yaml.loader import SafeLoader

with open('../config-personal.yml') as f:
    config = yaml.load(f, Loader=SafeLoader)

logging.basicConfig(level=logging.DEBUG, filename='logs/00-get_post_comments.log', filemode='w')


class RedditCommentLoader(object):
    def __init__(self, from_id: str = None) -> None:  #
        self.reddit = praw.Reddit(
            client_id=config['reddit']['client_id'],
            client_secret=config['reddit']['secret'],
            user_agent=f"testscript by u/{config['reddit']['user_name']}",
        )
        self.post_ids = pd.read_csv('../data/wallstreetbets.zip').loc[:, 'id'].tolist()
        self.comment_dict = {'id_col': [], 'comments': [], 'score': []}
        self.post_c = 0
        self.last_post_id = None
        self.from_id = from_id

    def draw_comments(self, post_id: str) -> Tuple:
        comment_ls = []
        score_ls = []
        post = self.reddit.submission(post_id)
        for top_level_comment in post.comments:
            if isinstance(top_level_comment, MoreComments):
                continue
            comment_ls.append(top_level_comment.body)
            score_ls.append(top_level_comment.score)

        return comment_ls, score_ls

    def run(self) -> None:
        if self.from_id:
            ind = self.post_ids.index(self.from_id)
            self.post_ids = self.post_ids[ind+1:]

        logging.info('Comment process starting now')
        print('Comment process starting now')

        for post_id in self.post_ids:
            self.post_c += 1
            for i in range(3):
                try:
                    comment_ls, score_ls = self.draw_comments(post_id)

                    self.comment_dict['id_col'].extend([post_id]*len(comment_ls))
                    self.comment_dict['comments'].extend(comment_ls)
                    self.comment_dict['score'].extend(score_ls)

                    break
                except PrawcoreException:
                    logging.exception(f'Got into a thing ...\n{PrawcoreException.__str__}')
                    logging.info(f'Retrying ...')

                    if i >= 2:
                        logging.info(f'Last item was {post_id}. Only part of the comments are saved')
                        self.last_post_id = post_id
                        self.push_data(which='momentary')
                        raise

            gc.collect()

            if self.post_c % 500 == 0:
                print(f'{self.post_c} post with comments have been processed')

        self.push_data(which='complete')

    def push_data(self, which: str) -> None:
        if which == 'momentary':
            df = pd.DataFrame(self.comment_dict)
            path = f'../data/comments/comments-until-{self.last_post_id}.zip'
            df.to_csv(path, index=False, compression='zip')
        else:
            logging.info('All the comments went through')
            df = pd.DataFrame(self.comment_dict)
            df.to_csv('../data/comments/comment-full.zip', index=False, compression='zip')
            logging.info('All comments were saved successfully')


# args = parse_args()
redd = RedditCommentLoader(from_id=None)  # Change to the preferred post id
redd.run()
