# MAKE SURE TO CORRECTLY SET UP A PYTHON VIRTUAL ENVIRONMENT, INSTALL requirements.txt
# AND DOWNLOAD THE KAGGLE POSTS DATA IN README BEFORE RUNNING ANYTHING!
cd src

# If your internet connection is unstable, make sure to change the last line of the file below
# to reflect the last posts you were able to scrape. The last posts id is the name in the logs when it fails or inside the
# data/comments directory
python 00-get_posts_comments.py

python 01-join-all-comments.py
python 02-sentiment-output.py
python RedditWSBSentiment.py
