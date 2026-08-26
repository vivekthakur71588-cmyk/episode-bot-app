import logging
import asyncio
import json

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    WebAppInfo
)

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)


# =========================================================
# BOT TOKEN
# =========================================================

# IMPORTANT:
# Yahan BotFather se NAYA token paste karo.
BOT_TOKEN = "8964605908:AAF3QUHbvtDfjuAvc7ZOVjramxXTzItI4ec"


# =========================================================
# EPISODE FILE IDs
# =========================================================

# Quality koi bhi ho, same episode ka same video bheja jayega.

EPISODE_FILES = {
    1: "BAACAgUAAyEFAAMBBjV5rgADBGqNCZPkcoaCjKUt6UWHxxN80emSAAKOLAAC2HpgVEssZTIwgvSGPQQ",
    2: "BAACAgUAAyEFAAMBBWqNCas-x29JIxwmJ9wkTLT7s4THAAKQLAAC2HpgVK36q9CkDMaiPQQ"
}


# =========================================================
# LOGGING
# =========================================================

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

logger = logging.getLogger(__name__)


# =========================================================
# START
# =========================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [
        [
            InlineKeyboardButton(
                "📥 Open Episode Stream Mini App",
                web_app=WebAppInfo(
                    url="https://vivekthakur71588-cmyk.github.io/episode-bot-app/BOT_TOKEN"
                )
            )
        ],
        [
            InlineKeyboardButton(
                "❓ How to Use",
                callback_data="how_to_use"
            )
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "📺 *India's Got Latent - Episodes*\n\n"
        "Click the button below to open the app and select your episode.",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )


# =========================================================
# HOW TO USE
# =========================================================

async def how_to_use_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    guide_text = (
        "📖 *How to Use Episode Stream Bot:*\n\n"
        "1️⃣ Open the Mini App.\n"
        "2️⃣ Select your episode.\n"
        "3️⃣ Select 1080p, 720p or 480p.\n"
        "4️⃣ Watch the short ad completely.\n"
        "5️⃣ Click *Open Bot to Collect*.\n"
        "6️⃣ The selected episode will arrive in this chat."
    )

    await query.message.reply_text(
        guide_text,
        parse_mode="Markdown"
    )


# =========================================================
# MINI APP DATA
# =========================================================

async def handle_web_app_data(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    try:

        # -------------------------------------------------
        # Get Mini App data
        # -------------------------------------------------

        raw_data = update.message.web_app_data.data

        logger.info(
            "WEB APP DATA RECEIVED: %s",
            raw_data
        )

        # -------------------------------------------------
        # Convert JSON
        # -------------------------------------------------

        data = json.loads(raw_data)

        ep_num = int(data.get("episode"))
        quality = data.get("quality", "Unknown")

        logger.info(
            "Episode=%s Quality=%s",
            ep_num,
            quality
        )

        # -------------------------------------------------
        # Check episode
        # -------------------------------------------------

        if ep_num not in EPISODE_FILES:

            await update.message.reply_text(
                "❌ Episode file not found."
            )

            return

        # -------------------------------------------------
        # Get File ID
        # -------------------------------------------------

        file_id = EPISODE_FILES[ep_num]

        # -------------------------------------------------
        # Caption
        # -------------------------------------------------

        caption = (
            f"🎬 *India's Got Latent*\n\n"
            f"📺 Episode: {ep_num}\n"
            f"⚙️ Selected Quality: {quality}\n\n"
            f"✅ Enjoy!"
        )

        # -------------------------------------------------
        # Send video
        # -------------------------------------------------

        sent_message = await update.message.reply_video(
            video=file_id,
            caption=caption,
            parse_mode="Markdown"
        )

        logger.info(
            "Episode %s sent successfully.",
            ep_num
        )

        # -------------------------------------------------
        # Delete after 10 minutes
        # -------------------------------------------------

        await asyncio.sleep(600)

        try:

            await sent_message.delete()

            logger.info(
                "Episode %s deleted after 10 minutes.",
                ep_num
            )

        except Exception as delete_error:

            logger.warning(
                "Could not delete video: %s",
                delete_error
            )

    except json.JSONDecodeError:

        logger.error(
            "Invalid JSON received from Mini App."
        )

        await update.message.reply_text(
            "❌ Invalid request received."
        )

    except Exception as e:

        logger.exception(
            "Error while processing Mini App data"
        )

        try:

            await update.message.reply_text(
                "❌ Something went wrong. Please try again."
            )

        except Exception:
            pass


# =========================================================
# ERROR HANDLER
# =========================================================

async def error_handler(
    update: object,
    context: ContextTypes.DEFAULT_TYPE
):

    logger.exception(
        "Telegram error:",
        exc_info=context.error
    )


# =========================================================
# MAIN
# =========================================================

def main():

    # -----------------------------------------------------
    # Check token
    # -----------------------------------------------------

    if not BOT_TOKEN:

        raise RuntimeError(
            "BOT_TOKEN missing. "
            "Please put your new BotFather token in BOT_TOKEN."
        )

    if BOT_TOKEN == "PASTE_YOUR_NEW_BOT_TOKEN_HERE":

        raise RuntimeError(
            "Please replace BOT_TOKEN with your actual new BotFather token."
        )

    # -----------------------------------------------------
    # Create application
    # -----------------------------------------------------

    app = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .build()
    )

    # -----------------------------------------------------
    # Handlers
    # -----------------------------------------------------

    app.add_handler(
        CommandHandler(
            "start",
            start
        )
    )

    app.add_handler(
        CallbackQueryHandler(
            how_to_use_callback,
            pattern="^how_to_use$"
        )
    )

    app.add_handler(
        MessageHandler(
            filters.StatusUpdate.WEB_APP_DATA,
            handle_web_app_data
        )
    )

    app.add_error_handler(
        error_handler
    )

    # -----------------------------------------------------
    # Start bot
    # -----------------------------------------------------

    print("======================================")
    print("BOT IS RUNNING")
    print("Waiting for Mini App data...")
    print("======================================")

    app.run_polling(
        allowed_updates=Update.ALL_TYPES
    )


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":
    main()
