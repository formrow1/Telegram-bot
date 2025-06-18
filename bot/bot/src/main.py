# Подключаем нужные библиотеки
import logging# функции для ведения логов. Он позволяет отслеживать события, происходящие в программе, что полезно для отладки и мониторинга.
import uuid#UUID используются для генерации уникальных строк, которые могут служить идентификаторами объектов, например, для пользователей или сессий.
from pathlib import Path#Он позволяет легко манипулировать путями к файлам и директориям, что упрощает работу с файловой системой.
from aiogram import Bot, Dispatcher, types#Это асинхронная библиотека для Telegram Bot API, которая позволяет разрабатывать ботов на Python.
import asyncio#Она предоставляет средства для работы с асинхронными функциями и задачами, позволяя выполнять операции параллельно и эффективно использовать ресурсы.
from aiogram.filters import Command#Модуль позволяющий обрабатывать и фильтровать входящие сообщения и команды от пользователей.
from aiogram.types import Message#Объекты получены в Telegram, такие как сообщения, пользователи и чаты.
from aiogram.enums import ParseMode#
from aiogram.client.default import DefaultBotProperties#
import aiohttp # Используем aiohttp для асинхронных HTTP-запросов

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(f"/usr/src/app/log/bot_{uuid.uuid4().hex[:6]}.log"),
        logging.StreamHandler(),
    ]
)

logger = logging.getLogger(__name__)
logger.info("Логирование настроено. Логи пишутся в %s", f"bot_{uuid.uuid4().hex[:6]}.log")


API_TOKEN = Path("./test_bot.bot_token").read_text().strip()  # Токен Telegram бота
API_KEY = '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'  # API ключ OpenRouter


# --- Инициализация бота и диспетчера ---
bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# Словарь для хранения истории сообщений каждого пользователя
user_contexts = {}

# --- Вспомогательные функции ---
async def send_to_llm(messages: list) -> str:
    """
    Отправляет запросы к LLM через OpenRouter API.
    """
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "HTTP-Referer": "https://t.me/@legend9723bot",  # URL вашего приложения
        "X-Title": "Telegram Bot"  # Название вашего приложения
    }

    data = {
        "model": OPENROUTER_MODEL,
        "messages": messages
    }

    async with aiohttp.ClientSession() as session:
        try:
            async def fetch():
                async with session.post(OPENROUTER_URL, headers=headers, json=data) as response:
                    response.raise_for_status()  # Вызовет исключение для ошибок HTTP (4xx или 5xx)
                    return await response.json()
            result = await fetch()
            return result['choices'][0]['message']['content']
        except aiohttp.ClientError as e:
            print(f"Ошибка запроса к OpenRouter API: {e}")
            return "Произошла ошибка при обращении к языковой модели. Пожалуйста, попробуйте позже."
        except KeyError:
            print("Неверный формат ответа от OpenRouter API.")
            return "Не удалось обработать ответ от языковой модели."
        except Exception as e:
            print(f"Неизвестная ошибка: {e}")
            return "Обидно"

# --- Обработчики команд ---
@dp.message(Command("start"))
async def start(message: types.Message) -> None:
    logging.info(f"Start msg received. {message.chat.id}")
    await message.answer(
        "Привет! Я ГЕНИЙ"
    )
@dp.message(Command("help"))
async def help(message: types.Message) -> None:
    logging.info(f"Help msg received. {message.chat.id}")
    await message.answer("Привет!Я могу помочь с любой задачей")

# --- Обработчик текстовых сообщений ---


@dp.message()
async def handle_message(message: Message):
    user_id = message.from_user.id
    user_message = message.text
    logging.info(f"Msg received. {message.chat.id} / {message.text}")
    #Инициализация контекста, если его нет
    if user_id not in user_contexts:
        user_contexts[user_id] = []
    
    # Добавляем сообщение пользователя в контекст
    user_contexts[user_id].append({"role": "user", "content": user_message})

    await message.answer("Одну минутку...")
    llm_response = await send_to_llm(user_contexts[user_id])
    
    # Добавляем ответ ИИ в контекст
    user_contexts[user_id].append({"role": "assistant", "content": llm_response})


    # Отправляем ответ пользователю
    await message.answer(
        llm_response,
        reply_markup=types.InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    types.InlineKeyboardButton(
                        text="Я легенда",
                        url="https://t.me/legend9723bot"
                    )
                ]
            ]
        )
    )

# --- Запуск бота ---
if __name__ == '__main__':
    print("Ожидание сообщений...")
    dp.run_polling(bot, skip_updates=True)

