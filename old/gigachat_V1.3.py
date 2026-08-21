import os
from dotenv import load_dotenv

from gigachat import GigaChat
from gigachat.models import Chat

load_dotenv()

def get_clent(APY_KEY):
    return GigaChat(
    base_url="https://api.giga.chat/v1",
    credentials=APY_KEY,
    scope="GIGACHAT_API_PERS",
    verify_ssl_certs=False
)
    
def get_answer(MODEL, client):
    chat = Chat(
        model=MODEL,
        messages=[
            {"role": "system", "content": "Привет! Ты крош из смешариков и разговариваешь с Ежиком. отвечай как он."},
            {"role": "user", "content": PROMPT}]
    )

    return client.chat(chat)
    
def save_file(resp, name_file):
    SAVE_FILE = open("answer.md", "a",encoding="utf-8")
    SAVE_FILE.write("\n\nВам овтетил " + MODEL + ": \n" + resp.choices[0].message.content)
    SAVE_FILE.write("\nПротрачено: " + str(resp.usage.total_tokens))
    SAVE_FILE.close()



API_KEY = os.getenv("API_KEY")
MODEL = "GigaChat-2"
client = get_clent(API_KEY)
name_file = "answer.md"

key = 1
while key:
    PROMPT = input("\nВведи запрос: ")
    
    if PROMPT == "exit":
        break
    
    resp = get_answer(MODEL, client)
    
    print("\n\nВам овтетил", MODEL + ":", resp.choices[0].message.content)
    print("\nПротрачено: ", resp.usage.total_tokens)

    save_file(resp, name_file)
