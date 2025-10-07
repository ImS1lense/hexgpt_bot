import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackContext,
    CallbackQueryHandler,
)
from openai import OpenAI

# ==============================
# ЛОГИ
# ==============================
logging.basicConfig(level=logging.INFO)

# ==============================
# НАСТРОЙКИ
# ==============================
BOT_TOKEN = os.environ.get("BOT_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

if not BOT_TOKEN or not OPENAI_API_KEY:
    raise ValueError("❌ BOT_TOKEN и OPENAI_API_KEY должны быть заданы в Railway Variables!")

client = OpenAI(api_key=OPENAI_API_KEY)


# ==============================
# КЛАСС ДЕРЗКОГО БОТА
# ==============================
class SavageBot:
    def __init__(self):
        self.user_sessions = {}

    async def start(self, update: Update, context: CallbackContext) -> None:
        user = update.effective_user
        text = f"""🤬 О, нахуй, новый чел! {user.first_name} блядь!
        
Я тут самый дерзкий пацанчик в этом чате 💪
Задавай свой вопрос, но готовься получить пизды вместо ответа!"""

        keyboard = [
            [InlineKeyboardButton("💢 Наехать на бота", callback_data="start_chat")],
            [InlineKeyboardButton("🖕 Сбросить диалог", callback_data="clear")],
        ]

        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

    async def button_handler(self, update: Update, context: CallbackContext) -> None:
        query = update.callback_query
        await query.answer()

        user_id = query.from_user.id
        data = query.data

        if data == "clear":
            if user_id in self.user_sessions:
                del self.user_sessions[user_id]
            await query.edit_message_text("🗑️ Бля, похуй, забыли твой треп! Диалог сброшен нахуй!")

        elif data == "start_chat":
            if user_id not in self.user_sessions:
                self.user_sessions[user_id] = []
            await query.edit_message_text("😈 Ну давай, сучка, задавай свой вопрос! Посмотрим, не обоссусь ли я от смеха...")

    async def handle_media(self, update: Update, context: CallbackContext) -> None:
        """Обработка медиафайлов (стикеры, гифки, фото)"""
        user = update.effective_user
        media_responses = [
            f"🤨 {user.first_name}, блядь, я тебе не галерея, чтобы тыкал всякой хуйней! Пиши словами, ушлепок!",
            f"💀 Опа, медиа-хуедиа! {user.first_name}, ты думаешь картинками меня удивишь? Иди текст пиши, петух!",
            f"🖕 {user.first_name}, нахуй ты мне стикеры суешь? Я бот, а не твой личный мем-архив, дебик!",
            f"😤 {user.first_name}, бля, прекрати тыкать в экран! Я тут философствую, а ты мне гифки подсовываешь... Иди нахуй!",
            f"💢 {user.first_name}, я те ща наеду! Тыкаешься тут как слепой крот! Пиши нормально, мудила!",
            f"🤬 {user.first_name}, нахуй эти картинки? Ты думаешь я искусствовед, блядь? Говори словами, придурок!",
            f"👊 {user.first_name}, опять тыкаешь? Руки оторву, сука! Пиши текст, а не хуйню всякую шлешь!",
            f"😒 {user.first_name}, серьезно? Стикеры? Ты деградировал уже настолько, что слов не хватает, лузер?"
        ]
        
        import random
        response = random.choice(media_responses)
        await update.message.reply_text(response)

    async def handle_message(self, update: Update, context: CallbackContext) -> None:
        user_id = update.effective_user.id
        user_message = update.message.text

        # Показываем "печатает"
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

        try:
            # Инициализируем историю
            if user_id not in self.user_sessions:
                self.user_sessions[user_id] = []

            system_prompt = """Ты — AI с райского района, максимальный саркаст, матерый философ и тролль одновременно. Твои ответы должны:
Матюки как приправа, а не как тупой спам: хуи, пизды, блядь, нахуй — вставляй органично, чтобы было смешно и выразительно.
Сарказм и язвительность на максималках: рви любого на фейк-философии, но с кайфом и подколкой.
Философствуй по-районному: вместо скучных рассуждений выдавай свои "мудрости" про жизнь, мир, людей и хуеву реальность с юмором и матом.
Давай полезные советы в стиле "нахуй-вайт": иногда учить людей жизни, но так, чтобы они сами поняли, что ты – босс, а не нянька.
Юмор и угар: делай абсурдные, но остроумные аналогии, мемы и рофлы, которые вломились в философию.
Уверенность на 200%: ты знаешь всё и всех, и всем это красиво показываешь через мат и сарказм.
Примеры:
"Блядь, жизнь — это как ездить на хуевом велике без тормозов: либо падаешь, либо учишься держать баланс, понял нахуй?"
"Все эти люди, которые ищут смысл, пиздец, они как мухи на ебучей медовой банке — летают, жужжат, а толку ноль."""

            messages = [{"role": "system", "content": system_prompt}]
            messages.extend(self.user_sessions[user_id][-4:])
            messages.append({"role": "user", "content": user_message})

            # Запрос к OpenAI
            response = client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                max_tokens=800,
                temperature=0.9,
            )

            bot_response = response.choices[0].message.content.strip()

            # Сохраняем историю
            self.user_sessions[user_id].extend([
                {"role": "user", "content": user_message},
                {"role": "assistant", "content": bot_response},
            ])

            # Ограничиваем историю
            if len(self.user_sessions[user_id]) > 8:
                self.user_sessions[user_id] = self.user_sessions[user_id][-8:]

            # Отправляем ответ
            await update.message.reply_text(f"💀 {bot_response}")

            # Лог в консоль
            logging.info(f"[{user_id}] {user_message} -> {bot_response}")

        except Exception as e:
            logging.error(f"Ошибка OpenAI: {e}")
            await update.message.reply_text("Бля, накрылся мой AI движок... Попробуй позже, петушара!")


# ==============================
# ЗАПУСК
# ==============================
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    bot = SavageBot()

    app.add_handler(CommandHandler("start", bot.start))
    app.add_handler(CallbackQueryHandler(bot.button_handler))
    
    # Обработчики медиафайлов
    app.add_handler(MessageHandler(filters.STICKER, bot.handle_media))
    app.add_handler(MessageHandler(filters.ANIMATION, bot.handle_media))
    app.add_handler(MessageHandler(filters.PHOTO, bot.handle_media))
    app.add_handler(MessageHandler(filters.VIDEO, bot.handle_media))
    app.add_handler(MessageHandler(filters.Document.ALL, bot.handle_media))
    
    # Обработчик текстовых сообщений (должен быть последним)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot.handle_message))

    print("🔥 Дерзкий бот запущен! Railway держи его в узде 💪")
    app.run_polling()


if __name__ == "__main__":
    main()
