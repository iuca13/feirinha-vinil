# bot_simples.py - IGNORA CANAL + Grupo Feirinha
import re
import base64
import os
from telegram.ext import Application, MessageHandler, filters, CommandHandler
from telegram import Update
import urllib.parse
import logging
import requests

logging.basicConfig(level=logging.INFO)

PPLX_API_KEY = os.getenv("PPLX_API_KEY") or "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"
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN") or "8371091084:AAGo8Hm5scZJ-2P1P0PSwaQqlD4wzFSDey0"
AFF_TAG = "diegosfm-20"

VINIL_NODE = "7791937011"
AMAZON_BR = "A2EB9PYM83FCP9"
VINIL_BINDING = "19416266011"

def perplexity_analyze(image_bytes):
    b64 = base64.b64encode(image_bytes).decode()
    payload = {
        "model": "sonar-pro",
        "messages": [{"role": "user", "content": [
            {"type": "text", "text": "Identifique CAPA VINIL:\nTÍTULO: [exato]\nARTISTA: [exato]"},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}  
        ]}]
    }
    headers = {"Authorization": f"Bearer {PPLX_API_KEY}", "Content-Type": "application/json"}
    try:
        resp = requests.post("https://api.perplexity.ai/chat/completions", json=payload, headers=headers, timeout=20)
        return resp.json()['choices'][0]['message']['content']
    except:
        return "TÍTULO: Vinil | ARTISTA: Artista"

def get_vinyl_search_link(title_artist):
    clean_query = re.sub(r'[\[\]()**!]', ' ', title_artist).strip()
    params = {
        'k': clean_query,
        'rh': f'n:{VINIL_NODE},p_6:{AMAZON_BR},p_n_binding_browse-bin:{VINIL_BINDING}',
        'ref': 'sr_nr_p_6_1',
        'tag': AFF_TAG
    }
    return f"https://www.amazon.com.br/s?{urllib.parse.urlencode(params)}"

async def photo_handler(update: Update, context):
    # ✅ IGNORA MENSAGENS DO CANAL
    if update.message.from_user.is_bot or update.message.sender_chat:  
        return  # Ignora bots e canais linked
    
    await update.message.reply_text("Opa, parece que você está compartilhando um vinil com os feirinhers ✨")
    
    photo = update.message.photo[-1]
    photo_file = await photo.get_file()
    img_bytes = await photo_file.download_as_bytearray()
    
    analysis = perplexity_analyze(img_bytes)
    
    title_match = re.search(r'TÍTULO:\s*(.+?)(?:\||\n|$)', analysis, re.I | re.S)
    artist_match = re.search(r'ARTISTA:\s*(.+?)(?:\||\n|$)', analysis, re.I | re.S)
    
    title = title_match.group(1).strip() if title_match else re.search(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)', analysis).group(1) if re.search(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)', analysis) else "Vinil"
    artist = artist_match.group(1).strip() if artist_match else "Artista"
    
    await update.message.reply_text(
        f"Era esse o disco que você compartilhilhou?\n"
        f"📀 Álbum: {title}\n"
        f"🎤 De: {artist}"
    )
    
    search_url = get_vinyl_search_link(f"{title} {artist}")
    
    final_msg = (
        f"**ACHO QUE ENCONTREI O DISCO!**\n\n"
        f"📀 `{title}`\n"
        f"🎤 `{artist}`\n\n"
        f"[🛒 *Clique aqui pra comprar*]({search_url})"
    )
    
    await update.message.reply_text(final_msg, parse_mode='Markdown', disable_web_page_preview=True)

async def start(update: Update, context):
    await update.message.reply_text(
        "🚀 *Feirinha dos Vinis*\n\n"
        "📸 Compartilhe capa → link Amazon filtrado\n\n"
        "🏷️ *diegosfm-20* ativa ✨\n"
        "_Ignora posts do canal_"
    )

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    # ✅ SÓ USUÁRIOS (ignora bots/canais)
    app.add_handler(MessageHandler(filters.PHOTO & ~filters.ChatType.CHANNEL & ~filters.User(user_id=0), photo_handler))
    print("🚀 Feirinha IGNORA CANAL ATIVA! ✨")
    app.run_polling()

if __name__ == '__main__':
    main()
