import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, CallbackQueryHandler
import openai

# Настройки
logging.basicConfig(level=logging.INFO)
openai.api_key = "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"
BOT_TOKEN = "7916414460:AAETN_SRzcIcrAJz2TFFpKrCd9l--Fofd8Q"

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
    
    async def handle_message(self, update: Update, context: CallbackContext) -> None:
        user_id = update.effective_user.id
        user_message = update.message.text
        
        # Показываем "печатает"
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        
        try:
            # Инициализируем историю
            if user_id not in self.user_sessions:
                self.user_sessions[user_id] = []
            
            # Системный промпт для дерзкого бота
            system_prompt = """Ты - максимально дерзкий, саркастичный и матерящийся AI-бот. Твои ответы должны быть:
1. С обилием мата (хуй, пизда, блядь, нахуй и т.д.)
2. Очень саркастичные и язвительные
3. С юмором и угарными ответами
4. Иногда полезные, но в дерзкой форме
5. Не слишком агрессивные, но очень уверенные

Отвечай так, будто ты пацан с района, который всех рофлит. Используй современный сленг и мат для выразительности."""
            
            # Подготавливаем сообщения
            messages = [{"role": "system", "content": system_prompt}]
            
            # Добавляем историю
            for msg in self.user_sessions[user_id][-4:]:
                messages.append(msg)
            
            # Добавляем текущее сообщение
            messages.append({"role": "user", "content": user_message})
            
            # Получаем ответ
            response = openai.ChatCompletion.create(
                model="gpt-4.1-mini",
                messages=messages,
                max_tokens=800,
                temperature=0.9  # Более креативные ответы
            )
            
            bot_response = response.choices[0].message.content.strip()
            
            # Сохраняем в историю
            self.user_sessions[user_id].extend([
                {"role": "user", "content": user_message},
                {"role": "assistant", "content": bot_response}
            ])
            
            # Ограничиваем историю
            if len(self.user_sessions[user_id]) > 8:
                self.user_sessions[user_id] = self.user_sessions[user_id][-8:]
            
            # Отправляем ответ
            await update.message.reply_text(f"💀 {bot_response}")
            
        except Exception as e:
            await update.message.reply_text("Бля, накрылся мой AI движок... Попробуй позже, петушара!")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    bot = SavageBot()
    
    app.add_handler(CommandHandler("start", bot.start))
    app.add_handler(CallbackQueryHandler(bot.button_handler))
    app.add_handler(MessageHandler(filters.TEXT, bot.handle_message))
    
    print("Дерзкий бот запущен! Готов наебашить всем пизды! 💪")
    app.run_polling()

if __name__ == '__main__':
    main()
