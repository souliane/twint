import re
from time import strftime, localtime

from bs4.element import Tag

from twint.config import Config


class tweet:
    image_url = None
    video_url = None

    def __init__(self, tweet_elt: Tag, config: Config):
        if config.Images or config.Media:
            self.setImageUrl(tweet_elt)

        if config.Videos or config.Media:
            self.setVideoUrl(tweet_elt)

    def setImageUrl(self, tweet_elt):
        image_urls = [
            elt["src"]
            for elt in tweet_elt.findAll("img", {"data-aria-label-part": True})
        ]
        try:
            self.image_url = image_urls[0].strip()
        except IndexError:
            self.image_url = None

    def setVideoUrl(self, tweet_elt):
        video_urls = [
            re.match(r".*url\('([^']+)'\)", elt["style"]).group(1)
            for elt in tweet_elt.findAll("div", {"class": "PlayableMedia-player"})
        ]
        try:
            self.video_url = video_urls[0].strip()
        except IndexError:
            self.video_url = None


def getMentions(tw):
    try:
        mentions = tw.find("div", "js-original-tweet")["data-mentions"].split(" ")
    except:
        mentions = ""

    return mentions

def getText(tw):
    text = tw.find("p", "tweet-text").text
    text = text.replace("\n", " ")
    text = text.replace("http", " http")
    text = text.replace("pic.twitter", " pic.twitter")

    return text

def getTweet(tw, mentions):
    
    text = getText(tw)

    return text

def getHashtags(text):
    return re.findall(r'(?i)\#\w+', text, flags=re.UNICODE)

def getStat(tw, _type):
    st = f"ProfileTweet-action--{_type} u-hiddenVisually"
    return tw.find("span", st).find("span")["data-tweet-stat-count"]

def getRetweet(profile, username, user):
    if profile and username.lower() != user:
        return True

def getUser_rt(profile, username, user):
    if getRetweet(profile, username, user):
        user_rt = user
    else:
        user_rt = "None"
    
    return user_rt

def Tweet(tw, location, config):
    t = tweet(tw, config)
    t.id = tw.find("div")["data-item-id"]
    t.datetime = int(tw.find("span", "_timestamp")["data-time"])
    t.datestamp = strftime("%Y-%m-%d", localtime(t.datetime))
    t.timestamp = strftime("%H:%M:%S", localtime(t.datetime))
    t.user_id = tw.find("a", "account-group js-account-group js-action-profile js-user-profile-link js-nav")["data-user-id"]
    t.username = tw.find("span", "username").text.replace("@", "")
    t.timezone = strftime("%Z", localtime())
    for img in tw.findAll("img", "Emoji Emoji--forText"):
        img.replaceWith(img["alt"])
    t.mentions = getMentions(tw)
    t.tweet = getTweet(tw, t.mentions)
    t.location = location
    t.hashtags = getHashtags(t.tweet)
    t.replies = getStat(tw, "reply")
    t.retweets = getStat(tw, "retweet")
    t.likes = getStat(tw, "favorite")
    t.link = f"https://twitter.com/{t.username}/status/{t.id}"
    t.retweet = getRetweet(config.Profile, t.username, config.Username)
    t.user_rt = getUser_rt(config.Profile, t.username, config.Username)
    t.id_conversation = tw.find("div")["data-conversation-id"]
    
    return t
