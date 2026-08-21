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
while key:
    PROMPT = input("\nВведи запрос: ")
    
    if PROMPT == "exit":
        break

    chat = Chat(
        model=MODEL,
        messages=[Messages(role=MessagesRole.USER, content=PROMPT)]
    )

    resp = client.chat(chat)
    print("\n\nВам овтетил", MODEL + ":", resp.choices[0].message.content)
    print("\nПротрачено: ", resp.usage.total_tokens)
