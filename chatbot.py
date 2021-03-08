import chatterbot
from chatterbot import ChatBot
import discord
import os

# Uncomment the following lines to enable verbose logging
import logging
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
            'default_response': 'わかんない。',
            'maximum_similarity_threshold': 0.80,
            "statement_comparison_function": "chatterbot.comparisons.JaccardSimilarity",
            "response_selection_method": "chatterbot.response_selection.get_most_frequent_response"
        }
    ],
    database_uri='postgres://xcsyacmkjpkkrn:f10c2235b1293dd3f749cb5be3763f32489ec6d419c010337662c2fc562c7c87@ec2-54-198-252-9.compute-1.amazonaws.com:5432/dcgc2cu84f14a1'
)



@client.event
async def on_ready():
    # 起動したらターミナルにログイン通知が表示される
    print('おはよー！')

@client.event
async def on_message(message):
    global up
    if not message.author.bot:
        if message.content == 'AtWakerちゃん！':
            up=1
            global channel
            channel=message.channel
            await channel.send("なーに？")
        elif up==1 and message.content == 'AtWakerちゃん、じゃあね！' and channel==message.channel:
            await channel.send("じゃあね！")
            up=0
        else:
            user_input = message.content
            bot_response = bot.get_response(user_input)
            if up==1 and channel==message.channel:
                await channel.send(bot_response)
    return

# Botの起動とDiscordサーバーへの接続
client.run(TOKEN)