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

def get_response(client, MESSEGES):
    chat = Chat(
        model="GigaChat-2",
        messages=MESSEGES
    )
    return client.chat(chat)

def save_response(response, model):
    with open("history/answer.md", "a", encoding="utf-8") as file:
        file.write(f"\n\nВам овтетил {model}:")
        file.write(response.choices[0].message.content)
        file.write(f"\nПротрачено: {response.usage.total_tokens}")

def main():
    API_KEY = os.getenv("API_KEY")
    client = get_client(API_KEY)
    model = "GigaChat-2"
    MESSEGES = [{"role": "system", "content": "Ты агент который может вызывать функции. Помогай тому кто тебя спрашивает"}]
    
    while True:
        
        prompt = input("\nВведи запрос: ")
        USER_PROMT = {"role": "user", "content": prompt}
        MESSEGES.append(USER_PROMT)
        
        if prompt == "exit":
            break
            
            
        
        response = get_response(client, MESSEGES)
        answer = {"role": response.choices[0].message.role, "content": response.choices[0].message.content}
        MESSEGES.append(answer)
        
        print(f"\n\nВам овтетил {model}: {response.choices[0].message.content} {response.choices[0].message.role}")
        print(f"\nПротрачено: {response.usage.total_tokens}")
        save_response(response, model)
        
        
        print(response)

if __name__ == "__main__":
    main()