import asyncio
import json
import time

from redis import StrictRedis
import logging
import yaml

from aiogram import Bot, Dispatcher, executor, types

config = None

with open('config.yml', 'r') as f:
    config = yaml.safe_load(f)

API_TOKEN = config.get('telegram_bot_api_token')

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


def event_handler(msg):
    print(msg)
    print('got message')
    try:
        key = msg["data"].decode("utf-8")
        if "notify" in key:
            key = key.replace("notify:", "")
            value = conn.get(key)
            # Process message redis subscriber
            process_message(value)
            # Once we got to know the value we remove it from Redis and do whatever required
            conn.delete(key)
    except Exception as exp:
        pass


async def process_message(value):
    value = value.get('data')
    if isinstance(value, bytes):
        value = value.decode('utf-8')
    with open('users.json', 'r') as file:
        data = json.load(file)
        for user in data.get('users_to_notify'):
            await bot.send_message(user, value)


# Creating Redis and pubsub Connection
redis = StrictRedis(host='localhost', port=6379)
pubsub = redis.pubsub()
pubsub.psubscribe('notify*')
while True:
    message = pubsub.get_message()
    # print('message: ', message)
    if message:
        asyncio.run(process_message(message))
        # print(message)
    else:
        time.sleep(0.01)

