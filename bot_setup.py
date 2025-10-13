from aiogram import Bot
import os
from dotenv import load_dotenv, find_dotenv


load_dotenv(find_dotenv())
bot = Bot(token=os.getenv("TOKEN"))
