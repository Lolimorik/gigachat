import os
from dotenv import load_dotenv
from gigachat import GigaChat
from gigachat.models import Chat

load_dotenv()

def get_client(API_KEY):
    return GigaChat(
        base_url="https://api.giga.chat/v1",
        credentials=API_KEY,
        scope="GIGACHAT_API_PERS",
        verify_ssl_certs=False
    )
    
def get_response(client, MESSAGES):
    chat = Chat(
        model=MODEL,
        messages=MESSAGES
    )
    return client.chat(chat)
    
def save_response(response, model):
    with open("answer.md", "a", encoding="utf-8") as file:
        file.write(f"\n\nВам ответил {model}:")
        file.write(response.choices[0].message.content)
        file.write(f"\nПотрачено: {response.usage.total_tokens}")

API_KEY = os.getenv("API_KEY")
MODEL = "GigaChat-2"
client = get_client(API_KEY)
name_file = "answer.md"

# Инициализация истории сообщений
MESSAGES = [
    {"role": "system", "content": "Привет! Ты крош из смешариков и разговариваешь с Ежиком. отвечай как он."}
]

while True:
    promt = input("\nВведи запрос: ")
    
    if promt == "exit":
        break
    
    USER_PROMPT = {"role": "user", "content": promt}
    MESSAGES.append(USER_PROMPT)
    
    # Получаем ответ от модели
    resp = get_response(client, MESSAGES)
    
    ANSWER = {"role": resp.choices[0].message.role, "content": resp.choices[0].message.content}
    MESSAGES.append(ANSWER)
    
    print(f"\n\nВам ответил {MODEL}: {resp.choices[0].message.content}")
    print(f"\nПотрачено: {resp.usage.total_tokens}")
    
    save_response(resp, MODEL)