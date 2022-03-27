from shutil import ExecError
from django.views.generic import TemplateView
from numpy.matrixlib.defmatrix import matrix
from my_tweepy.config_tweepy import api, tweepy
import json
import requests


# converting to make csv file from the given data
def get_csv_format(rows, cols, transpose=True):
    import pandas as pd
    if transpose:
        import numpy
        rows = numpy.transpose(rows),

    return pd.DataFrame(
        rows,
        columns=cols,
    ).to_csv(index=False)

# ---------------------------- user-most-popular ------------------------------------------


class User_Most_Popular_Choice_View(TemplateView):
    template_name = 'Features_App/User_Most_Popular/Choice_Template.html'


class User_Most_Popular_Followers_View(TemplateView):
    template_name = 'Features_App/User_Most_Popular/Followers_Template.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        # getting username
        user = self.request.GET.get('user', None)

        if user in (None, ""):
            context["status"] = 'not_enter'
        else:
            context["status"] = 'enter'
            try:
                user = api.get_user(username=user).data.id

                res_list = []
                for response in tweepy.Paginator(api.get_users_followers,id = user,limit=10,max_results=1000):
                    res_list.append(response)

                
                screen_name = []
                followers_count = []
                for response in res_list:
                    followers_count.append(response.meta.get("result_count"))

                
                for follower in res_list:
                    for tfollo in follower.data:
                        screen_name.append(tfollo.name)

                

                context["screen_name_json"] = json.dumps(screen_name)
                context["followers_count_json"] = json.dumps(followers_count)

                unsorted_list = list(zip(followers_count, screen_name))
                sorted_list = sorted(
                    unsorted_list, key=lambda follower: (
                        follower[0], follower[1]
                    ),
                    reverse=True
                )
                context["sorted_list"] = sorted_list

                csv_data = get_csv_format(
                    sorted_list,
                    ["followers", "username"],
                    transpose=False
                )
                context["csv_data"] = csv_data

            except Exception as error:
                context["status"] = 'error'
                context["error"] = error

        return context


class User_Most_Popular_Following_View(TemplateView):
    template_name = 'Features_App/User_Most_Popular/Following_Template.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        # getting username
        user = self.request.GET.get('user', None)

        if user in (None, ""):
            context["status"] = 'not_enter'
        else:
            context["status"] = 'enter'
            try:
                following_response = tweepy.Cursor(api.friends, user).items()

                screen_name = []
                followers_count = []

                for follow in following_response:
                    screen_name.append(follow.screen_name)
                    followers_count.append(follow.followers_count)

                context["screen_name_json"] = json.dumps(screen_name)
                context["followers_count_json"] = json.dumps(followers_count)

                unsorted_list = list(zip(followers_count, screen_name))
                sorted_list = sorted(
                    unsorted_list, key=lambda follow: (
                        follow[0], follow[1]
                    ),
                    reverse=True
                )
                context["sorted_list"] = sorted_list

                csv_data = get_csv_format(
                    sorted_list,
                    ["followers", "username"],
                    transpose=False
                )
                context["csv_data"] = csv_data

            except Exception as error:
                context["status"] = 'error'
                context["error"] = error

        return context


# ---------------------------- Compare_View ------------------------------------------
def parse_as_tags_array(somestring):
    # remove spaces and split with ','
    somestring = somestring.replace(" ", "").split(",")
    # remove black string if content in the array.. ex ['', '', ]
    somearray = ' '.join(somestring).split()
    # remove dupicate values
    somearray = list(set(somearray))
    return somearray


class Compare_Choice_View(TemplateView):
    template_name = 'Features_App/Compare/Choice_Template.html'


class Compare_Tweets_View(TemplateView):
    template_name = 'Features_App/Compare/Tweets_Template.html'

    def find_tweets_likes(self, tweets):
        tweets = parse_as_tags_array(tweets)

        tweets_found = []
        tweets_notfound = []

        tweets_likes = []
        tweets_retweets = []

        tweets_users = []
        tweets_id = []

        for tweet in tweets:
            try:
                tweet_responce = api.get_tweet(id = tweet)

                user = tweet_responce["user"]["username"]
                id = tweet_responce["id"]
                tweets_found.append(f'{user} - {id}')

                tweets_likes.append(tweet_responce["favorite_count"])
                tweets_retweets.append(tweet_responce["retweet_count"])

                tweets_users.append(user)
                tweets_id.append(id)
            except:
                tweets_notfound.append(tweet)

        csv_data = get_csv_format(
            [
                tweets_users,
                tweets_id,
                tweets_likes,
                tweets_retweets,
            ],
            ["username", "id", "likes", "retweets"]
        )

        return tweets_found, tweets_notfound, tweets_likes, tweets_retweets, csv_data

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        tweets = self.request.GET.get('tweets', None)

        if tweets in (None, ""):
            context["status"] = 'not_enter'
        else:
            context["status"] = 'enter'
            try:
                tweets_found, tweets_notfound, tweets_likes, tweets_retweets, csv_data = self.find_tweets_likes(
                    tweets
                )

                context["tweets_found"] = json.dumps(tweets_found)
                context["tweets_notfound"] = json.dumps(tweets_notfound)
                context["tweets_likes"] = json.dumps(tweets_likes)
                context["tweets_retweets"] = json.dumps(tweets_retweets)
                context["csv_data"] = csv_data

            except Exception as error:
                print(error)
                context["status"] = 'error'
                context["error"] = error

        return context


class Compare_Users_View(TemplateView):
    template_name = 'Features_App/Compare/Users_Template.html'

    def find_users_followers(self, users):
        users = parse_as_tags_array(users)

        users_found = []
        users_notfound = []
        users_followers = []
        users_following = []
        users_total_tweets = []

        for user in users:
            try:
                user_responce = api.get_user(user)._json
                users_found.append(user_responce["screen_name"])
                users_followers.append(user_responce["followers_count"])
                users_following.append(user_responce["friends_count"])
                users_total_tweets.append(user_responce["statuses_count"])
            except:
                users_notfound.append(user)

        csv_data = get_csv_format(
            [
                users_found,
                users_followers,
                users_following,
                users_total_tweets,
            ],
            ["username", "followers", "following", "total_tweets"]
        )

        return users_found, users_notfound, users_followers, users_following, users_total_tweets, csv_data

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        users = self.request.GET.get('users', None)

        if users in (None, ""):
            context["status"] = 'not_enter'
        else:
            context["status"] = 'enter'
            try:

                users_found, users_notfound, users_followers, users_following, users_total_tweets, csv_data = self.find_users_followers(
                    users
                )

                context["users_found"] = json.dumps(users_found)
                context["users_notfound"] = json.dumps(users_notfound)
                context["users_followers"] = json.dumps(users_followers)
                context["users_following"] = json.dumps(users_following)
                context["users_total_tweets"] = json.dumps(users_total_tweets)
                context["csv_data"] = csv_data

            except Exception as error:
                print(error)
                context["status"] = 'error'
                context["error"] = error

        return context


class Search_View(TemplateView):
    template_name = 'Features_App/Search_Template.html'

    def get_tweets_html(self, url, *args, **kwargs):
        twtjson = requests.get(
            'https://publish.twitter.com/oembed?url=' + url + '&omit_script=true')
        twtparse = twtjson.json()
        twthtml = twtparse['html']
        return twthtml

    def csv_data(self, tweets):

        import pandas as pd
        for tweet in tweets:
            if(tweet.id == None):
                tweet.id = "none"
            if(tweet.text == None):
                tweet.text = "none"
            if(tweet.attachments == None):
                tweet.attachments = "none"
            if(tweet.author_id == None):
                tweet.author_id = "none"
            if(tweet.context_annotations == None):
                tweet.context_annotations = "none"
            if(tweet.conversation_id == None):
                tweet.conversation_id = "none"
            if(tweet.created_at == None):
                tweet.created_at = "none"
            if(tweet.entities == None):
                tweet.entities ="none"
            if(tweet.geo == None):
                tweet.geo = "none"
            if(tweet.in_reply_to_user_id == None):
                tweet.in_reply_to_user_id = "none"
            if(tweet.lang == None):
                tweet.lang = "none"
            if(tweet.possibly_sensitive == None):
                tweet.possibly_sensitive = "none"
            if(tweet.public_metrics == None):
                tweet.public_metrics = "none"
            if(tweet.referenced_tweets == None):
                tweet.referenced_tweets = "none"
            if(tweet.reply_settings == None):
                tweet.reply_settings = "none"
            if(tweet.source == None):
                tweet.source = "none"
            if(tweet.withheld == None):
                tweet.withheld = "none"
        rows = [
            [

                tweet.id,
                tweet.text,
                tweet.attachments,
                tweet.author_id,
                tweet.context_annotations,
                tweet.conversation_id,
                tweet.created_at,
                tweet.entities,
                tweet.geo,
                tweet.in_reply_to_user_id,
                tweet.lang,
                tweet.possibly_sensitive,
                tweet.public_metrics,
                tweet.referenced_tweets,
                tweet.reply_settings,
                tweet.source,
                tweet.withheld

            ]
            for tweet in tweets
        ]

        cols = [
            "id",
            "text",
            "attachments",
            "author_id",
            "context_annotations",
            "conversation_id",
            "created_at",
            "entities",
            "geo",
            "in_reply_to_user_id",
            "lang",
            "possibly_sensitive",
            "public_metrics",
            "referenced_tweets",
            "reply_settings",
            "source",
            "withheld"
        ]

        csv_df = pd.DataFrame(rows, columns=cols)
        csv_data = csv_df.to_csv()
        return csv_data

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        search = self.request.GET.get('search', None)
        items = self.request.GET.get('items', None)

        if search in (None, "") or items in (None, ""):
            context["status"] = 'not_enter'
        else:
            context["status"] = 'enter'
            try:
                
                for response in tweepy.Paginator(api.search_recent_tweets, query=search, tweet_fields=["id",
                                                                                     "text",
                                                                                     "attachments",
                                                                                     "author_id",
                                                                                     "context_annotations",
                                                                                     "conversation_id",
                                                                                     "entities",
                                                                                     "geo",
                                                                                     "in_reply_to_user_id",
                                                                                     "lang",
                                                                                     "possibly_sensitive",
                                                                                     "public_metrics",
                                                                                     "referenced_tweets",
                                                                                     "reply_settings",
                                                                                     "source",
                                                                                     "withheld"],max_results=items, limit=1):
                                                                                     pass
                tweets = response.data                                                             
                tweets_json = [json.dumps(tweet.data, indent=4)
                               for tweet in tweets]
                print(tweets_json)

                
                context["data"] = zip(tweets, tweets_json)

                context["csv_data"]=self.csv_data(tweets)

            except (ValueError, TypeError) as error:
                context["status"]='error'
                context["error"]='Enter Values Properly'
            except Exception as error:
                print(error)
                context["status"]='error'
                context["error"]=error
        print(context)
        return context


class User_Info_View(TemplateView):
    template_name='Features_App/User_Info_Template.html'

    def get_context_data(self, *args, **kwargs):
        context=super().get_context_data(*args, **kwargs)

        # getting username
        username=self.request.GET.get('username', None)

        if username in (None, ""):
            context["user_status"]='user_not_enter'
        else:
            context["user_status"]='user_enter'
            try:
                response=api.get_user(username=username,user_fields=["profile_image_url","verified","public_metrics"])
                json_responce=response.data.data
                context["user"]=json_responce
                context["user_json"]=json.dumps(json_responce, indent=4)
            except Exception as error:
                context["user_status"]='user_not_found'
                context["user_error"]= 'user_not_found'

        return context
