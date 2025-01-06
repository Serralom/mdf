import os
import logging
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from commands import *
from queries import init_db

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')

# Configurar el logging para tener visibilidad de los errores
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

init_db()

application = Application.builder().token(BOT_TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("relapse", relapse))
application.add_handler(CommandHandler("rachas", streaks))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, set_relapse))

if __name__ == "__main__":
    application.run_polling()
