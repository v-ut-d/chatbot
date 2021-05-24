import chatterbot
from chatterbot import response_selection
from chatterbot.ext.sqlalchemy_app.models import Statement
from chatterbot import ChatBot
import discord
import os
import re
import typing
import functools

# Uncomment the following lines to enable verbose logging
import logging
from chatterbot.trainers import ChatterBotCorpusTrainer
import psycopg2
from urllib.parse import urlparse

result = urlparse(os.environ['DATABASE_URL'])
username = result.username
password = result.password
database = result.path[1:]
hostname = result.hostname
port = result.port
connection = psycopg2.connect(
    database = database,
    user = username,
    password = password,
    host = hostname,
    port = port
)
cur = connection.cursor()
sql=("CREATE TABLE IF NOT EXISTS statement ("
  +"text varchar(65535) NOT NULL, "
  +"search_text varchar(65535), "
  +"conversation varchar(255), "
  +"created_at date, "
  +"tags varchar(255), "
  +"in_response_to varchar(65535), "
  +"search_in_response_to varchar(65535), "
  +"persona varchar(255), "
  +"PRIMARY KEY (text) "
  +");")
cur.execute(sql)
cur.execute("DELETE FROM statement WHERE created_at < (now() - '3 days'::interval);")
cur.close()
connection.close()# import spacy
# nlp = spacy.load("xx_sent_ud_sm")
logging.basicConfig(level=logging.INFO)
up=0
istyping=0
TOKEN = os.environ['TOKEN']

channel=None
intents = discord.Intents.all()
client = discord.Client(intents=intents)
# Create a new instance of a ChatBot
bot = ChatBot(
    'AtWaker',
    storage_adapter='chatterbot.storage.SQLStorageAdapter',
    logic_adapters=[
        {
            "import_path": "chatterbot.logic.BestMatch",
            "statement_comparison_function": "chatterbot.comparisons.SentimentComparison",
            "response_selection_method": response_selection.get_random_response
        }
    ],
    database_uri=os.environ['DATABASE_URL']
    )

async def run_blocking(blocking_func: typing.Callable, *args, **kwargs) -> typing.Any:
    """Runs a blocking function in a non-blocking way"""
    func = functools.partial(blocking_func, *args, **kwargs) # `run_in_executor` doesn't support kwargs, `functools.partial` does
    return await client.loop.run_in_executor(None, func)

async def learn_and_send(channel,user_input):
    global istyping
    istyping+=1
    async with channel.typing():
        z=await run_blocking(bot.get_response,user_input)
        istyping-=1
    if istyping!=0:
        channel.typing()
    mentions=re.findall("<@.+>",z.text)
    for m in mentions:
        mid=int(re.sub("[<@!&>","",m))
        if re.search("&",m):
            if channel.guild.get_role(mid):
                nm=channel.guild.get_role(mid).name
            else:
                nm="deleted_role"
        else:
            if channel.guild.get_member(mid):
                nm=channel.guild.get_member(mid).display_name
            else:
                nm="deleted_member"
        z.text=re.sub(m,"@."+nm,z.text)
    await channel.send(z)
    return
# trainer = ChatterBotCorpusTrainer(bot)

# trainer.train(
#     "chatterbot.corpus.japanese"
# )

@client.event
async def on_ready():
    # 起動したらターミナルにログイン通知が表示される
    print('おはよー！')

@client.event
async def on_message(message):
    global up
    global channel
    if not message.author.bot:
        if message.content == 'AtWakerちゃん！':
            up=1
            channel=message.channel
            await channel.send("なーに？")
        elif (up==1 and 'AtWakerちゃん' in message.content 
             and 'ばいばい' in message.content and channel==message.channel):
            await channel.send("じゃあね！")
            up=0
        elif len(message.content)>0:
            last_input=await run_blocking(bot.get_latest_response,conversation=str(message.channel.id))
            if up==1 and channel==message.channel:
                user_input={
                    "text":message.content,
                    "conversation":str(message.channel.id),
                    "in_response_to":last_input.text if (not last_input is None) else None,
                    "persona":str(message.author.id)
                }
                await learn_and_send(channel,user_input)
            else:
                user_input = Statement(
                    text=message.content,
                    conversation=str(message.channel.id),
                    in_response_to= last_input.text if (not last_input is None) else None,
                    persona= str(message.author.id)
                )
                await run_blocking(bot.learn_response,user_input)
    return

# Botの起動とDiscordサーバーへの接続
client.run(TOKEN)