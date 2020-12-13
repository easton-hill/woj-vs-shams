import csv
import os
import requests
import sys

# Twitter username to get tweets from
username = "wojespn"
# CSV file to store tweets
csvfile = "tweets.csv"

def get_tweets(tweets_returned):
    """ 
    Tweets array will hold a tweet object for every tweet returned
    Details stored: ID, created time, text, RTs, favorites
    Exclude tweets with URLs/media
    """
    tweets = []
    for tweet in tweets_returned:
        if len(tweet["entities"]["urls"]) or "https" in tweet["full_text"]:
            continue
        tweet_details = {}
        tweet_details["ID"] = tweet["id_str"]
        tweet_details["time"] = tweet["created_at"]
        tweet_details["text"] = tweet["full_text"]
        tweet_details["retweets"] = tweet["retweet_count"]
        tweet_details["favorites"] = tweet["favorite_count"]
        tweets.append(tweet_details)

    if len(tweets) == 0:
        print("No more tweets returned")
        sys.exit()

    return tweets

def write_tweets(csvfile, tweets):
    with open(csvfile, "a", encoding="utf-8", newline="") as f:
        csvwriter = csv.writer(f)
        for tweet in tweets:
            csvwriter.writerow([tweet["ID"], tweet["time"], tweet["text"], tweet["retweets"], tweet["favorites"]])


def main(username, csvfile):
    # Twitter bearer token stored in environment variable
    bearer = os.environ.get("TWITTER_KEY")
    headers = {"Authorization": f"Bearer {bearer}"}

    # Using optional parmas: trim_user, exclude_replies, include_rts, tweet_mode
    url = "https://api.twitter.com/1.1/statuses/user_timeline.json?"
    url += f"screen_name={username}&trim_user=true&exclude_replies=true&include_rts=false&tweet_mode=extended&count=200"

    # Get tweets first time, then loop until no tweets returned (max 3200)
    response = requests.get(url, headers=headers)
    tweets = get_tweets(response.json())
    max_id = int(tweets[-1]["ID"])
    print(f"Adding {len(tweets)} tweets...")
    write_tweets(csvfile, tweets)

    while True:
        url = "https://api.twitter.com/1.1/statuses/user_timeline.json?"
        url += f"screen_name={username}&trim_user=true&exclude_replies=true&include_rts=false&tweet_mode=extended&count=200"
        url += f"&max_id={max_id - 1}"

        response = requests.get(url, headers=headers)
        tweets = get_tweets(response.json())
        max_id = int(tweets[-1]["ID"])
        print(f"Adding {len(tweets)} tweets...")
        write_tweets(csvfile, tweets)

if __name__ == "__main__":
    main(username, csvfile)