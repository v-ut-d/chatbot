import chatterbot
from chatterbot import response_selection
from chatterbot import ChatBot
import discord
import os

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
cur.execute("DELETE FROM statement WHERE created_at < (now() - '10 days'::interval);")
# import spacy
# nlp = spacy.load("xx_sent_ud_sm")
logging.basicConfig(level=logging.INFO)
up=0
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
            "response_selection_method": response_selection.get_most_frequent_response,
        }
    ],
    database_uri='postgres://xcsyacmkjpkkrn:f10c2235b1293dd3f749cb5be3763f32489ec6d419c010337662c2fc562c7c87@ec2-54-198-252-9.compute-1.amazonaws.com:5432/dcgc2cu84f14a1'
)

async def run_blocking(blocking_func: typing.Callable, *args, **kwargs) -> typing.Any:
    """Runs a blocking function in a non-blocking way"""
    func = functools.partial(blocking_func, *args, **kwargs) # `run_in_executor` doesn't support kwargs, `functools.partial` does
    return await client.loop.run_in_executor(None, func)

async def learn_and_send(channel,input):
    z=bot.get_response(user_input)
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
        elif up==1 and message.content == 'AtWakerちゃん、じゃあね！' and channel==message.channel:
            await channel.send("じゃあね！")
            up=0
        else:
            user_input = message.content
            if up==1 and channel==message.channel:
                await run_blocking(learn_and_send,channel,user_input)
            else:
                await run_blocking(bot.get_response,user_input)
    return

# Botの起動とDiscordサーバーへの接続
client.run(TOKEN)