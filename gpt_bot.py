import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, CallbackQueryHandler
import openai

# Настройки
logging.basicConfig(level=logging.INFO)
openai.api_key = "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"
BOT_TOKEN = "7916414460:AAETN_SRzcIcrAJz2TFFpKrCd9l--Fofd8Q"

class SimpleBot:
    def __init__(self):
        self.user_sessions = {}
    
    async def start(self, update: Update, context: CallbackContext) -> None:
        user = update.effective_user
        user_id = user.id
        
        # Очищаем историю
        if user_id in self.user_sessions:
            del self.user_sessions[user_id]
        
        text = f"👋 Привет, {user.first_name}!\n\nЯ AI-бот. Задай мне вопрос!"
        
        keyboard = [
            [InlineKeyboardButton("🧠 Начать диалог", callback_data="start_chat")],
            [InlineKeyboardButton("🗑️ Очистить историю", callback_data="clear")],
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
            await query.edit_message_text("✅ История очищена!")
        
        elif data == "start_chat":
            if user_id not in self.user_sessions:
                self.user_sessions[user_id] = []
            await query.edit_message_text("💬 Диалог начат! Просто напиши сообщение.")
    
    async def handle_message(self, update: Update, context: CallbackContext) -> None:
        user_id = update.effective_user.id
        user_message = update.message.text
        
        # Показываем "печатает"
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        
        try:
            # Инициализируем историю
            if user_id not in self.user_sessions:
                self.user_sessions[user_id] = []
            
            # Подготавливаем сообщения
            messages = [{"role": "system", "content": "Ты полезный ассистент."}]
            
            # Добавляем историю
            for msg in self.user_sessions[user_id][-6:]:
                messages.append(msg)
            
            # Добавляем текущее сообщение
            messages.append({"role": "user", "content": user_message})
            
            # Получаем ответ
            response = openai.ChatCompletion.create(
                model="gpt-4.1-mini",
                messages=messages,
                max_tokens=1000
            )
            
            bot_response = response.choices[0].message.content.strip()
            
            # Сохраняем в историю
            self.user_sessions[user_id].extend([
                {"role": "user", "content": user_message},
                {"role": "assistant", "content": bot_response}
            ])
            
            # Ограничиваем историю
            if len(self.user_sessions[user_id]) > 10:
                self.user_sessions[user_id] = self.user_sessions[user_id][-10:]
            
            # Отправляем ответ
            await update.message.reply_text(f"🤖 {bot_response}")
            
        except Exception as e:
            await update.message.reply_text("❌ Ошибка. Попробуй еще раз.")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    bot = SimpleBot()
    
    app.add_handler(CommandHandler("start", bot.start))
    app.add_handler(CallbackQueryHandler(bot.button_handler))
    app.add_handler(MessageHandler(filters.TEXT, bot.handle_message))
    
    print("Бот запущен!")
    app.run_polling()

if __name__ == '__main__':
    main()