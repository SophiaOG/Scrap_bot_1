from aiogram import Bot, Dispatcher, F
import os
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from dotenv import load_dotenv
import asyncio
import json
from parser import threads

load_dotenv()
bot = Bot(token=os.getenv('TOKEN'))
dp = Dispatcher()
parsing_state = False


class Form(StatesGroup):
    count = State()


class Computers:
    def __init__(self):
        with open("computers.json", 'r', encoding='utf-8') as file:
            self.laptops = json.load(file)

    def get_list(self, count):
        title = self.laptops[count].get("title")
        desc = self.laptops[count].get("desc")
        price = self.laptops[count].get("price")
        return f"{title} \n {price} \n {desc}"

    def get_link(self, count):
        link = self.laptops[count].get("link")
        return str(link)

    def get_url(self, count):
        url = self.laptops[count].get("pict")
        return str(url)

    def get_len(self):
        return len(self.laptops)


def inline(url):

    kb = [[InlineKeyboardButton(text="подробнее", url=url)]]
    keyboard = InlineKeyboardMarkup(inline_keyboard=kb, resize_keyboard=True)
    return keyboard


@dp.message(Command("start"))
async def start(message: Message, state: FSMContext):

    await state.update_data(count=0)

    kb = [[
          KeyboardButton(text="next")]]
    keyboard = ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True
    )

    await message.answer("привет!\nиспользуй кнопку для просмотра :)", reply_markup=keyboard)


@dp.message(F.text.lower() == "next")
async def send_computer(message: Message, state: FSMContext):

    computers = Computers()
    data = await state.get_data()
    count = data.get('count', 0)

    if computers.get_len() - count <= 10:
        global parsing_state
        if not parsing_state:
            parsing_state = True
            await message.answer("подгружаем данные... возможно замедление работы бота")
            start_page = computers.get_len()//24 + 1
            asyncio.create_task(check_func(start_page, start_page+3))
        else:
            url = computers.get_url(count)
            title = computers.get_list(count)
            link = computers.get_link(count)

            await message.answer_photo(photo=url, caption=f"{title} \n {count}", reply_markup=inline(link))
    else:
        url = computers.get_url(count)
        title = computers.get_list(count)
        link = computers.get_link(count)

        await message.answer_photo(photo=url, caption=f"{title} \n {count}", reply_markup=inline(link))

    count += 1
    await state.update_data(count=count)


async def check_func(x, y):
    global parsing_state
    await asyncio.create_task(threads(x, y))
    parsing_state = False


async def main():
    await asyncio.create_task(threads(1, 4))
    await dp.start_polling(bot)

try:
    if __name__ == "__main__":
        asyncio.run(main())

except:
    with open("computers.json", 'w', encoding="utf-8") as f:
        pass
    print("power off :(")
