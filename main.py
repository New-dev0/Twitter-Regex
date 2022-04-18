# https://github.com/New-dev0/Twitter-Regex

import asyncio
from decouple import config
from tweepy import Client
from regx import make_regex
from platform import platform
from tweepy.asynchronous import AsyncStream

consumer_key = config("CONSUMER_KEY", default="")
consumer_secret = config("CONSUMER_SECRET", default="")
access_token = config("ACCESS_TOKEN", default="")
access_secret = config("ACCESS_TOKEN_SECRET", default="")

print("> Starting Up!")

client = Client(
    consumer_key=consumer_key,
    consumer_secret=consumer_secret,
    access_token=access_token,
    access_token_secret=access_secret,
)
me = client.get_me()

if platform().startswith("Windows"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


class RegexStream(AsyncStream):
    async def on_status(self, status):
        data = status._json

        if not data["in_reply_to_status_id"]:
            return
        
        if data["retweeted"]:
            return

        if not any(
            user["id"] == me.data.id
            for user in data["entities"].get("user_mentions", [])
        ):
            return

        try:
            pattern = data["text"].split("s/", maxsplit=1)[1]
            pattern = "s/" + pattern
        except IndexError:
            # Consider it as invalid pattern
            return
        try:
            msg = client.get_tweet(
                id=data["in_reply_to_status_id"], user_auth=True
            ).data.text
        except Exception as er:
            print("Error while getting replied tweet", er)
            return

        if not msg:
            return

        try:
            retext = make_regex(pattern, msg)

            client.create_tweet(text=retext, in_reply_to_tweet_id=data["id"])
        except Exception as er:
            raise er
            print(er)

    async def on_connect(self):
        print("> Connected Successfully!")

    async def on_connection_error(self):
        print("> ERROR: Connection Error!")

    async def on_exception(self, exception):
        print(exception)


async def main():
    stream = RegexStream(
        consumer_key=consumer_key,
        consumer_secret=consumer_secret,
        access_token=access_token,
        access_token_secret=access_secret,
    )
    await stream.filter(track=["@" + me.data.username])


try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("> Ending Up!")
