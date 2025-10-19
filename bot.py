import os
import logging
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from parser import get_crypto_price, get_top_5_crypto_prices, get_top_5_crypto_list, generate_price_chart

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a welcome message when the /start command is issued."""
    await update.message.reply_text(
        "🚀 *Crypto Tracker Bot* 🚀\n\n"
        "📈 Get real-time cryptocurrency prices and charts including:\n"
        "  • Bitcoin, Ethereum, Binance Coin\n"
        "  • Toncoin and other top cryptos\n\n"
        "💡 *Available commands:*\n"
        "  /price - Check cryptocurrency price\n"
        "  /chart - Get a 24h price chart\n"
        "  /top5 - View top 5 by market cap\n\n"
        "Tap /price to check Toncoin price now!"
    )

async def ask_for_crypto(update: Update, context: ContextTypes.DEFAULT_TYPE, intent: str) -> None:
    """Saves the user's intent and asks them to select a cryptocurrency."""
    context.user_data['intent'] = intent
    logger.info(f"User intent set to: {intent}")
    
    try:
        crypto_list = get_top_5_crypto_list()
        logger.info(f"Received crypto list from API: {crypto_list}")
    except Exception as e:
        logger.error(f"Error getting crypto list: {e}")
        crypto_list = ['bitcoin', 'ethereum', 'binancecoin', 'ripple', 'cardano']
        logger.info(f"Using fallback crypto list: {crypto_list}")
    
    crypto_list.append("Toncoin")
    logger.info(f"Final crypto list with Toncoin: {crypto_list}")
    
    keyboard_rows = [[crypto.title()] for crypto in crypto_list]
    logger.info(f"Keyboard rows: {keyboard_rows}")

    await update.message.reply_text(
        "📈 Please select a cryptocurrency from the list below:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard_rows,
            one_time_keyboard=True,
            resize_keyboard=True,
            input_field_placeholder="Select cryptocurrency",
            selective=True
        ),
    )

async def price_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler for the /price command."""
    await ask_for_crypto(update, context, intent='get_price')

async def chart_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler for the /chart command."""
    await ask_for_crypto(update, context, intent='get_chart')

async def crypto_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles the user's choice of cryptocurrency and sends the price or chart."""
    intent = context.user_data.get('intent')
    if not intent:
        # If intent is not set, do nothing or send a default message.
        return

    crypto_name_raw = update.message.text
    crypto_name = crypto_name_raw.lower()
    
    # Map user-friendly names to API IDs
    crypto_id = 'the-open-network' if crypto_name == 'toncoin' else crypto_name

    if intent == 'get_price':
        await update.message.reply_text(f"🔍 Checking current {crypto_name_raw} price...")
        price_info = get_crypto_price(crypto_id)
        
        if "error" in price_info.lower() or "could not find" in price_info.lower() or "not available" in price_info.lower():
            await update.message.reply_text(f"❌ Sorry, I couldn't retrieve the {crypto_name_raw} price at the moment. Please try again later.")
        else:
            await update.message.reply_text(f"💰 Current {crypto_name_raw} price: {price_info}")

    elif intent == 'get_chart':
        await update.message.reply_text(f"🎨 Generating 24h chart for {crypto_name_raw}...")
        chart_image = generate_price_chart(crypto_id)

        if chart_image:
            await update.message.reply_photo(
                photo=chart_image,
                caption=f"📈 24-hour price chart for {crypto_name_raw}"
            )
        else:
            await update.message.reply_text(f"❌ Sorry, I couldn't generate the chart for {crypto_name_raw} at the moment. Please try again later.")

    # Clear the intent after handling
    if 'intent' in context.user_data:
        del context.user_data['intent']

async def top5(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Fetches and sends the prices of the top 5 cryptocurrencies."""
    await update.message.reply_text("Fetching the prices of the top 5 cryptocurrencies...")
    
    prices_info = get_top_5_crypto_prices()
    
    await update.message.reply_text(f"Top 5 cryptocurrencies:\n{prices_info}")

def main() -> None:
    """Start the bot."""
    if not TOKEN or TOKEN == "YOUR_TELEGRAM_BOT_TOKEN":
        logger.error("Your TELEGRAM_BOT_TOKEN is missing or invalid. Please update the .env file.")
        return

    # Create the Application and pass it your bot's token.
    application = ApplicationBuilder().token(TOKEN).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("price", price_command))
    application.add_handler(CommandHandler("chart", chart_command))

    application.add_handler(CommandHandler("top5", top5))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, crypto_handler))


    # Run the bot until the user presses Ctrl-C
    application.run_polling()

if __name__ == "__main__":
    main()
