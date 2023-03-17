import json
import os, sys
import tweepy
import logging
logging.basicConfig(format='%(asctime)s | %(levelname)s : %(message)s',
                        level=logging.INFO, stream=sys.stdout)

class _cn:   # Column Names
    id = "id"
    place_id = "place_id"
    geo_place_id = "geo.place_id"
    full_name = "full_name"
    bearer_token = "bearer_token"
    author_id = "author_id"
    username = 'username'
    public_metrics = 'public_metrics'
    description = 'description'
    location = 'location'
    created_at = 'created_at'
    geo = 'geo'
    public_metrics = 'public_metrics'
    text = 'text'

class _on:   # Object Names
    users = "users"
    places = "places"

def get_message(tweet, user, places):
    if tweet.geo == None and user.location == None:
        return f"-- {user.name} tweets '{tweet.text}'"
    
    if tweet.geo != None and places != None:
        place = places[tweet.geo[_cn.place_id]]
        location = place.data[_cn.full_name]
        return f"++ {user.name} from {location} tweets '{tweet.text}'"
    
    return f"++ {user.name} from {user.location} tweets '{tweet.text}'"

def lambda_handler(event, context):
    bearer_token = os.environ[_cn.bearer_token]
    client = tweepy.Client(bearer_token=bearer_token)
    
    #query = '#covid -is:retweet lang:en'
    query = '#covid lang:en'
    _user_fields = [_cn.username, _cn.public_metrics, _cn.description, _cn.location]
    _tweet_fields = [_cn.created_at, _cn.geo, _cn.public_metrics, _cn.text]
    _expansions = [_cn.geo_place_id, _cn.author_id]
    tweets = client.search_recent_tweets(query=query, 
                                         user_fields = _user_fields,
                                         tweet_fields = _tweet_fields,
                                         expansions=_expansions, max_results=100)
    users = tweets.includes[_on.users]
    if users == None:
        sys.exit("No users found for tweets")

    users = {user[_cn.id]: user for user in users}
    try:
        places = tweets.includes[_on.places]
    except:
        places = None

    if places != None:
        places = {place[_cn.id]: place for place in places}
    
    for tweet in tweets.data:
        user = users[tweet.author_id]
        logging.info("-------------")
        message = get_message(tweet, user, places)
        logging.info(message)

if __name__ == "__main__":
    lambda_handler(None, None)