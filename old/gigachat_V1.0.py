from gigachat import GigaChat
from dotenv import load_dotenv
from gigachat.models import Chat, Messages, MessagesRole
import os
from gigachat import GigaChat

load_dotenv()


APY_KEY = os.getenv("APY_KEY")

client = GigaChat(
    base_url="https://api.giga.chat/v1",
    credentials=APY_KEY,
    scope="GIGACHAT_API_PERS",
    verify_ssl_certs=False
)

PROMPT = "Привет! Как дела?"

chat = Chat(
    model="GigaChat-2-Max",
    messages=[Messages(role=MessagesRole.USER, content=PROMPT)]
)

resp = client.chat(chat)

print(resp)
print(APY_KEY, Messages(role=MessagesRole.USER, content=PROMPT))