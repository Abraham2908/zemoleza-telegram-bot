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

bot = Bot(token=bot_token)

def auth_telegram_token(x_telegram_bot_api_secret_token: str = Header(None)) -> str:
    if x_telegram_bot_api_secret_token != secret_token:
        raise HTTPException(status_code=403, detail="Not authenticated")
    return x_telegram_bot_api_secret_token

@app.post("/webhook/")
async def handle_webhook(update: TelegramUpdate, token: str = Depends(auth_telegram_token)):
    chat_id = update.message["chat"]["id"]
    text = update.message["text"]

    if text == "/start":
        with open('hello.gif', 'rb') as photo:
            await bot.send_photo(chat_id=chat_id, photo=photo)
        await bot.send_message(chat_id=chat_id, text="Bem vindo ao Zé Moleza, seu facilitador de ferramentas de Pentest!")

    elif text.startswith("/recon"):
        parts = text.split()
        if len(parts) >= 2:
            domain = parts[1]
            await bot.send_message(chat_id=chat_id, text=f"Domínio: {domain}")
            
            # Responder apenas quando necessário
            menu_keyboard = [[KeyboardButton(text="Subfinder")],[KeyboardButton(text="Cancelar")]]  
            markup = ReplyKeyboardMarkup(menu_keyboard)

            await bot.send_message(chat_id=chat_id, 
                                   reply_markup=markup,
                                   text="Escolha uma opção:")
        else:
            await bot.send_message(chat_id=chat_id, text="Por favor informe um domínio depois do comando. Ex: /recon <domínio>")
            return
        
    else:
        # Evite responder a mensagens que não têm uma mensagem original válida para responder
        if "message_id" in update.message:
            await bot.send_message(chat_id=chat_id,
                                   reply_to_message_id=update.message["message_id"],
                                   text="Yo!")

    return {"ok": True}
