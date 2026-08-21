import os
from dotenv import load_dotenv

from gigachat import GigaChat
from gigachat.models import Chat, Messages, MessagesRole

load_dotenv()

APY_KEY = os.getenv("APY_KEY")

MODEL = "GigaChat-2"

client = GigaChat(
    base_url="https://api.giga.chat/v1",
    credentials=APY_KEY,
    scope="GIGACHAT_API_PERS",
    verify_ssl_certs=False
)

key = 1
name = 0
while key:
    PROMPT = input("\nВведи запрос: ")
    
    if PROMPT == "exit":
        break

    chat = Chat(
        model=MODEL,
        messages=[
            {"role": "system", "content": "Ты ИИ агент. Твоя задача писать код. На ответ пользователя ты должен написать код на Python не используюя маркдаун или другой верстки. Твой ответ будет автоматически записан в файл с расширением .py"},
            {"role": "user", "content": PROMPT}]
    )

    resp = client.chat(chat)
    print("\n\nВам овтетил", MODEL + ":", resp.choices[0].message.content)
    print("\nПротрачено: ", resp.usage.total_tokens)
    
    SAVE_FILE = open("answer.md", "a",encoding="utf-8")
    SAVE_FILE.write("\n\nВам овтетил " + MODEL + ": \n" + resp.choices[0].message.content)
    SAVE_FILE.write("\nПротрачено: " + str(resp.usage.total_tokens))
    SAVE_FILE.close()

