import os
import json
from dotenv import load_dotenv
from gigachat import GigaChat
from gigachat.models import Chat, Function, FunctionParameters, FunctionCall
from datetime import datetime

load_dotenv()

def print_MASSAGES(MESSAGES):
    for elem in MESSAGES:
         print(elem)

def get_current_time():
    return json.dumps({"time": datetime.now().strftime("%H:%M:%S")})\
        

def adding_numbers():
    return json.dumps({"res": "Их невозможно сложить!"})

def get_client():
    return GigaChat(
        base_url="https://api.giga.chat/v1",
        credentials=os.getenv("API_KEY"),
        scope="GIGACHAT_API_PERS",
        verify_ssl_certs=False
    )

def get_response(client, MESSAGES):
    chat = Chat(
        model="GigaChat-2",
        
        messages=MESSAGES,
        
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
                name="adding_numbers",
                description="вызывай когда просят сложить 2 числа",
                parameters=FunctionParameters(
                    type="object",
                    properties={"a": {"type": "number",
                                      "description": "Первое число"},
                                "b": {"type": "number",
                                      "description": "Второе число"}},
                    required=["a", "b"]
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
            return ["get_current_time", get_current_time()]
        if func_name == "adding_numbers":
            return ["adding_numbers", adding_numbers()]
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
    MESSAGES = [{"role": "system", "content": "Ты агент который может вызывать функции. Помогай тому кто тебя спрашивает"}]
    
    while True:
        prompt = input("\nВведи запрос: ")
        USER_PROMT = {"role": "user", "content": prompt}
        MESSAGES.append(USER_PROMT)
        
        if prompt == "exit":
            break
            
        response = get_response(client, MESSAGES)
        
        
        #print(response, '\n', hasattr(response.choices[0].message, 'function_call'), response.choices[0].message.function_call)
        
        function_result = handle_function_call(response)
        print(function_result)
        
        if function_result:
            
            
            FUNCTION_CALL_MESSAGE = {"role": response.choices[0].message.role,
                "content":  response.choices[0].message.content,
                "function_call": {
                    "name": response.choices[0].message.function_call.name,
                    "arguments": response.choices[0].message.function_call.arguments
                }
            }
            MESSAGES.append(FUNCTION_CALL_MESSAGE)
            
            
            print(f"\n\n                  Произошел вызов функции!    MODEL: {model} \n                  res: {function_result}")
            FUNCTION_CALL = {"role": "function", "name": function_result[0], "content": function_result[1]}
            MESSAGES.append(FUNCTION_CALL)
            
            response = get_response(client, MESSAGES)
            
        
        print(f"\n\nВам овтетил {model}: {response.choices[0].message.content}")
        ANSWER = {"role": response.choices[0].message.role, "content": response.choices[0].message.content}
        MESSAGES.append(ANSWER)
        
        print(f"\nПротрачено: {response.usage.total_tokens}")
        
        print_MASSAGES(MESSAGES)
        
        save_response(response, model, function_result)

if __name__ == "__main__":
    main()