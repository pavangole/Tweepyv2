"""
this py code
reply to the tweet which added #withrvr ( can change ) and mention you ( in my case @withrvr ) in the tweet
"""

from config_tweepy import api  # , tweepy

try:

    # taking out the tweets who have mention you ( in my case @withrvr )
    mentions = api.mentions_timeline()
    # hashtag_should_content = '#withrvr'

    # looping over tweets how have mention
    # then checking if it content hashtag
    for mention in reversed(mentions):
        print(mention.text)
        print()
        # if hashtag_should_content in mention.text.lower():
        #     user_name = mention.user.screen_name

        #     print(f"({mention.id}) - mention.text")

        #     # replying (commenting) with the msg (who have mentioned )
        #     # uncomment to reply to them
        #     # msg = "..@" + user_name + " thanks to mention me and using hashtag #withrvr"
        #     # api.update_status(msg, mention.id)
        # else:
        #     print(
        #         f'Not content {hashtag_should_content}'
        #     )


except Exception as e:
    print(e)
