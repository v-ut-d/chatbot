from chatterbot import ChatBot
import discord
import os
from chatterbot.trainers import ListTrainer

# Uncomment the following lines to enable verbose logging
import logging
import spacy
import en_core_web_md
nlp = en_core_web_md.load()
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
        'chatterbot.logic.MathematicalEvaluation',
        'chatterbot.logic.BestMatch',
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
    if message.author.id!=818061060069261332:
        if message.content == 'AtWakerちゃん！':
            up=1
            global channel
            channel=message.channel
            await channel.send("なーに？")
        elif up==1 and message.content == 'AtWakerちゃん、じゃあね！' and channel==client.get_channel(message.channel):
            await channel.send("じゃあね！")
            up=0
        else:
            user_input = message.content
            bot_response = bot.get_response(user_input)
            if up==1:
                await channel.send(bot_response)
    return

# Botの起動とDiscordサーバーへの接続
client.run(TOKEN)