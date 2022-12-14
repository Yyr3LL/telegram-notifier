import json
import redis
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


def process_message(value):
    with open('users.json', 'r') as file:
        data = json.load(file)
        for user in data.get('users_to_notify'):
            bot.send_message(user, value)




@dp.message_handler(commands=['add'])
async def handle_users(message: types.Message):
    with open('users.json', 'r') as file:
        data = json.load(file)
    if message.from_user.id not in data['administrators']:
        await message.reply("sayonara loshara")

    user = message.text[5:]
    if user not in data['users_to_notify']:
        data['users_to_notify'].append(user)

    with open('users.json', 'w') as file:
        json.dump(data, file)

    await bot.send_message(message.from_user.id, "test message")  # like this
    await message.reply("Hi!\nI'm EchoBot!\nPowered by aiogram.")
    
    
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
