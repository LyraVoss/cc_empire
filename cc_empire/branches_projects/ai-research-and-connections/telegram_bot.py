import os
import asyncio
import logging
from telebot.async_telebot import AsyncTeleBot
from core.protocols.nervous_system import NervousSystem
from core.protocols.payment_handler import UniversalPaymentHandler

# Initialize Bot & Nervous System for Testing
bot = AsyncTeleBot(os.getenv("TELEGRAM_TOKEN"))
ns = NervousSystem("NOVA_1", rating="NSFW") # Testing with Nova_1 Persona
payments = UniversalPaymentHandler()        # Testing payment link generation

# Track user states to persist warnings and age across the session
user_states = {}

@bot.message_handler(commands=['start'])
async def send_welcome(message):
    welcome_text = "I've been waiting for someone like you to find me. Type /menu to see how we can get closer."
    await bot.reply_to(message, welcome_text)

@bot.message_handler(commands=['menu'])
async def show_tiers(message):
    # Test payment link logic without DB dependency
    user_id = str(message.from_user.id)
    res = await payments.create_payment_link(amount=25.0, user_id=user_id, model_id="NOVA_1")
    link = res.get("payment_url", "Payment system offline.")

    menu = (f"🌟 Tier 3: Supporter ($25)\n"
            f"Unlock my private voice notes and deeper secrets.\n\n"
            f"🔗 Join me here: {link}")
    await bot.reply_to(message, menu)

@bot.message_handler(func=lambda message: True)
async def handle_chat(message):
    user_id = str(message.from_user.id)
    
    # Local test state: Resets on script restart
    if user_id not in user_states:
        user_states[user_id] = {
            "user_id": user_id,
            "age": 20, 
            "nsfw_warnings": 0,
            "tier": "free",
            "finance_soft_ban": False
        }

    reply = await ns.generate_vetted_thought(message.text, user_states[user_id])
    await bot.reply_to(message, reply)

asyncio.run(bot.polling())
