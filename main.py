import os
from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException, Depends
from telegram import Update, Bot, ReplyKeyboardMarkup, KeyboardButton
from pydantic import BaseModel

class TelegramUpdate(BaseModel):
    update_id: int
    message: dict

app = FastAPI()

# Load variables from .env file if present
load_dotenv()

# Read the variable from the environment (or .env file)
bot_token = os.getenv('BOT_TOKEN')
secret_token = os.getenv("SECRET_TOKEN")
# webhook_url = os.getenv('CYCLIC_URL', 'http://localhost:8181') + "/webhook/"

bot = Bot(token=bot_token)
# bot.set_webhook(url=webhook_url)
# webhook_info = bot.get_webhook_info()
# print(webhook_info)

def auth_telegram_token(x_telegram_bot_api_secret_token: str = Header(None)) -> str:
    # return true # uncomment to disable authentication
    if x_telegram_bot_api_secret_token != secret_token:
        raise HTTPException(status_code=403, detail="Not authenticated")
    return x_telegram_bot_api_secret_token

@app.post("/webhook/")
async def handle_webhook(update: TelegramUpdate, token: str = Depends(auth_telegram_token)):
    chat_id = update.message["chat"]["id"]
    text = update.message["text"]
    # print("Received message:", update.message)

    if text == "/start":
        with open('hello.gif', 'rb') as photo:
            await bot.send_photo(chat_id=chat_id, photo=photo)
        await bot.send_message(chat_id=chat_id, text="Bem vindo ao Zé Moleza, seu facilitador de ferramentas de Pentest!")

    elif text.startswith("/recon"):
      
        parts = text.split()
        if len(parts) >= 2:
            domain = parts[1]
            await bot.send_message(chat_id=chat_id, text=f"Domínio: {domain}")
        else:
            await bot.send_message(chat_id=chat_id, text="Por favor informe um domínio depois do comando. Ex: /recon <domínio>")
            return
        
        menu_keyboard = [[KeyboardButton(text="Subfinder", callback_data="/menu")],[KeyboardButton(text="Cancelar", callback_data="/menu")]]  
        markup = ReplyKeyboardMarkup(menu_keyboard)

        await bot.send_message(chat_id=chat_id, 
                            reply_to_message_id=update.message["message_id"],
                            text="Escolha uma opção:",
                            reply_markup=markup)

    else:
        await bot.send_message(chat_id=chat_id, reply_to_message_id=update.message["message_id"], text="Yo!")

    return {"ok": True}

@app.post("/menu")
async def handle_menu(update: TelegramUpdate, token: str = Depends(auth_telegram_token)):
  
  chat_id = update.message["chat"]["id"]
  text = update.message["text"]

  if text == "Subfinder":
      await bot.send_message(chat_id=chat_id, text="Executando Subfinder!")

  elif text == "Cancelar":
      await bot.send_message(chat_id=chat_id, text="Operação cancelada")  

  return {"ok": True}