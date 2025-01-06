import pendulum
from telegram import Update
from telegram.ext import ContextTypes
from queries import init_streak, get_streaks


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.message.from_user.first_name
    await update.message.reply_text(
        f"¡Hola {user_name}!\n"
        "Para ver el contador de rachas, usa el comando /rachas.\n"
        "Para registrar un nuevo inicio, usa el comando /relapse."
    )


async def set_relapse(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.message.from_user.first_name

    init_streak(user_name, pendulum.now())

    await update.message.reply_text(
        f"Racha de {user_name} iniciada correctamente!\n"
    )


async def relapse(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = (
        "🔎 Resultados disponibles:\n\n"
        "Ranking de hoy: /hoy\n"
        "Ranking anual de victorias: /anual\n"
        "Ranking histórico de victorias: /historico\n"
        "Mejores tiempos y promedios: /mejores_tiempos\n"
        "Todo lo anterior: /todo"
    )
    await update.message.reply_text(message)

    
async def streaks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ranking_queens = get_streaks("queens")
    
    return  ranking_queens
