import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
import ccxt

# 1. BOT TOKENINI SHU YERGA YOZING
TOKEN = "8964767123:AAFwMp2JjQVwxAjf5amqdje3Ex51HIavaXk"

bot = Bot(token=TOKEN)
dp = Dispatcher()
exchange = ccxt.binance()

# Kuzatiladigan aktivlar ro'yxati
crypto_list = [
    'BTC/USDT',   # Bitcoin
    'ETH/USDT',   # Ethereum
    'SOL/USDT',   # Solana
    'PAXG/USDT',  # Oltin (PAX Gold)
    'TON/USDT'    # Toncoin
]

# Narxlarni va 24 soatlik foiz o'zgarishini oluvchi funksiya
async def get_prices_text():
    try:
        text = "📊 **JORIY BOZOR VA 24h O'ZGARISHLAR** 📊\n"
        text += "-----------------------------------------\n"
        
        for symbol in crypto_list:
            ticker = exchange.fetch_ticker(symbol)
            current_price = ticker['last']
            
            # 24 soatlik o'zgarish foizini olamiz
            change_percentage = ticker['percentage']
            
            coin_name = symbol.split('/')[0]
            
            # O'sish yoki tushishiga qarab emoji tanlaymiz
            if change_percentage >= 0:
                emoji = f"🟢 +{change_percentage:.2f}%"
            else:
                emoji = f"🔴 {change_percentage:.2f}%"
            
            # Matn formatini chiroyli qilamiz
            if coin_name == 'PAXG':
                text += f"✨ **GOLD (Oltin)**: `{current_price}` USDT ({emoji})\n"
            else:
                text += f"🔹 **{coin_name}**: `{current_price}` USDT ({emoji})\n"
                
        text += "-----------------------------------------\n"
        text += "🔄 *Ma'lumotlar Binance birjasidan olindi.*"
        return text
    except Exception as e:
        return f"❌ Narxlarni olishda xatolik: {e}"

# Yangilash tugmasini yaratuvchi funksiya
def get_refresh_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(
        text="🔄 Narxlarni yangilash", 
        callback_data="refresh_prices"
    ))
    return builder.as_markup()

# /start komandasi uchun handler
@dp.message(Command("start"))
async def start_command(message: types.Message):
    await message.answer(
        "Salom! Men Kriptovalyuta va Oltin narxlarini hamda sutkalik o'zgarishlarini kuzatuvchi botman.\n\n"
        "📈 Narxlarni bilish uchun pastdagi tugmani bosing yoki /narxlar buyrug'ini yuboring.\n\n"
        "🧮 **Kalkulyator**: Istalgan miqdordagi narxni hisoblash uchun menga masalan `0.5 btc` yoki `15 sol` deb xabar yuboring!",
        reply_markup=get_refresh_keyboard()
    )

# /narxlar komandasi uchun handler
@dp.message(Command("narxlar"))
async def send_prices(message: types.Message):
    await bot.send_chat_action(chat_id=message.chat.id, action="typing")
    prices_text = await get_prices_text()
    await message.answer(prices_text, parse_mode="Markdown", reply_markup=get_refresh_keyboard())

# Tugma bosilganda narxlarni xabar ichida yangilovchi handler
@dp.callback_query(lambda c: c.data == "refresh_prices")
async def refresh_prices_callback(callback_query: types.CallbackQuery):
    await callback_query.answer("Narxlar va foizlar yangilanmoqda...")
    new_text = await get_prices_text()
    
    if callback_query.message.text != new_text:
        await callback_query.message.edit_text(
            text=new_text,
            parse_mode="Markdown",
            reply_markup=get_refresh_keyboard()
        )

# 🧮 MATNLI XABARLARNI O'QIB HISOBLAYDIGAN KALKULYATOR FUNKSIYASI
@dp.message()
async def crypto_calculator(message: types.Message):
    try:
        parts = message.text.strip().split()
        
        if len(parts) == 2:
            amount = float(parts[0])  # Miqdori (masalan: 0.5)
            coin = parts[1].upper()   # Tanganing nomi (masalan: BTC)
            
            if coin == "GOLD" or coin == "OLTIN":
                coin = "PAXG"
                
            symbol = f"{coin}/USDT"
            
            if symbol in crypto_list:
                await bot.send_chat_action(chat_id=message.chat.id, action="typing")
                ticker = exchange.fetch_ticker(symbol)
                price = ticker['last']
                
                total_usdt = amount * price
                display_name = "GOLD (Oltin)" if coin == "PAXG" else coin
                
                await message.reply(
                    f"🧮 **Kalkulyator natijasi:**\n\n"
                    f"💰 {amount} {display_name} = `{total_usdt:,.2f}` USDT\n\n"
                    f"ℹ️ *1 {display_name} = {price} USDT*",
                    parse_mode="Markdown"
                )
    except ValueError:
        pass
    except Exception as e:
        await message.reply(f"❌ Hisoblashda xatolik: {e}")

# Botni ishga tushirish
async def main():
    print("Telegram Crypto Bot (Foiz + Kalkulyator) bilan ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
