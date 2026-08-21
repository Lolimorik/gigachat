import os
from dotenv import load_dotenv
from gigachat import GigaChat
from gigachat.models import Chat, Function, FunctionParameters, FunctionCall
from datetime import datetime

load_dotenv()

def print_MESSEGES(MESSEGES):
    print("-----------------------")
    print("Текущяя история:")
    for elem in MESSEGES:
        print(elem)
    print("-----------------------")

def get_current_time():
    return datetime.now().strftime("%H:%M:%S")

def my_func():
    return "Hello world"

def get_client():
    return GigaChat(
        base_url="https://api.giga.chat/v1",
        credentials=os.getenv("API_KEY"),
        scope="GIGACHAT_API_PERS",
        verify_ssl_certs=False
    )

def get_response(client, MESSEGES):
    chat = Chat(
        model="GigaChat-2",
        
        messages=MESSEGES,
        
        functions=[
            Function(
                name="get_current_time",
                description="Получить текущее время",
                parameters=FunctionParameters(
                    type="object",
                    properties={},
                    required=[]
                )
            ),
            Function(
                name="my_func",
                description="Пишет ради прикола hello world. Исспользуй ее когда пользователь просит использоваться свою функцию",
                parameters=FunctionParameters(
                    type="object",
                    properties={},
                    required=[]
                )
            )
        ],
        function_call="auto"
    )
    return client.chat(chat)

def handle_function_call(response):
    if hasattr(response.choices[0].message, 'function_call') and response.choices[0].message.function_call:
        func_name = response.choices[0].message.function_call.name
        if func_name == "get_current_time":
            return get_current_time()
        if func_name == "my_func":
            return my_func()
    return None

def save_response(response, model, function_result=None):
    with open("answer.md", "a", encoding="utf-8") as f:
        if function_result:
            f.write(f"\n\nВам овтетил {model}: Сейчас {function_result}")
        else:
            f.write(f"\n\nВам овтетил {model}: \n{response.choices[0].message.content}")
        f.write(f"\nПротрачено: {response.usage.total_tokens}")

def main():
    client = get_client()
    model = "GigaChat-2"
    MESSEGES = [{"role": "system", "content": "Ты агент который может вызывать функции. Помогай тому кто тебя спрашивает"}]
    
    while True:
        prompt = input("\nВведи запрос: ")
        USER_PROMT = {"role": "user", "content": prompt}
        MESSEGES.append(USER_PROMT)
        
        if prompt == "exit":
            break
            
        response = get_response(client, MESSEGES)
        
        print("-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=")
        print("-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=")
        print(response)
        print("-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=")
        print("-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=")
        
        
        ANSWER = {"role": response.choices[0].message.role, "content": response.choices[0].message.content}
        MESSEGES.append(ANSWER)
        
        function_result = handle_function_call(response)
       
        print_MESSEGES(MESSEGES)
        
        print(function_result)
        
        print("-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=")
        print("-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=")
 
        if function_result:
            print(f"\n\nВам овтетил {model}: Сейчас {function_result}")
        
        print(f"\n\nВам овтетил {model}: {response.choices[0].message.content}")
        
        print(f"\nПротрачено: {response.usage.total_tokens}")
        save_response(response, model, function_result)

if __name__ == "__main__":
    main()