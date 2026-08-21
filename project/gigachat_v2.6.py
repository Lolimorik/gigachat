import os
import json
import subprocess
from dotenv import load_dotenv
from gigachat import GigaChat
from gigachat.models import Chat, Function, FunctionParameters, FunctionCall
from datetime import datetime

load_dotenv()

def print_MESSAGES(MESSAGES):
    print("-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=")
    print("Вывод истории текущей сессии:")
    for elem in MESSAGES:
        print(elem)
    print("-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=")
    

def if_command(prompt, MESSAGES):
    
    if prompt == "\history":
        print_MESSAGES(MESSAGES)
        return 1
    if prompt == "\help":
        print("Команды для разработчика:\nhistory - выводит историю текущей сессии\nhelp - выводит команды\n\exit - аварийное завершение работы")
        return 1
    if prompt == "\exit":
        print("\n\n\nПрощай!\n\n\n")
        return 1
        
        
    return 0

def read_file(name_file):
    try:
        with open(name_file, "r", encoding="utf-8") as file:
            content = file.read()
        return json.dumps({"res": content})
    except FileNotFoundError:
        return json.dumps({"error": f"Файл {name_file} не найден."})

def write_file(name_file, text):
    try:
        with open(name_file, "w", encoding="utf-8") as file:
            file.write(text)
        return json.dumps({"res": f"Файл {name_file} успешно обновлен."})
    except Exception as e:
        return json.dumps({"error": str(e)})


def get_current_time():
    return json.dumps({"time": datetime.now().strftime("%H:%M:%S")})

def ls():
    return json.dumps({"list": subprocess.check_output("ls -l", shell=True, text=True)})

def create_file(name_file):
    open(name_file, "w", encoding="utf-8").close()
    return json.dumps({"res": "file create"})

def adding_numbers(a, b):
    return json.dumps({"res": a + b}, ensure_ascii=False)

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
            ),
            Function(
                name="ls",
                description="Вызови, чтобы узнать какие файлы лежат в рабочей папке",
                parameters=FunctionParameters(
                    type="object",
                    properties={},
                    required=[]
                )
            ),
            Function(
                name="create_file",
                description="Вызывай чтобы создайть файл",
                parameters=FunctionParameters(
                    type="object",
                    properties={"name": {"type": "string",
                                      "description": "название будущего файла"}},
                    required=["name"]
                )
            ),
            Function(
                name="read_file",
                description="Вызывай чтобы получить содержимое файла",
                parameters=FunctionParameters(
                    type="object",
                    properties={"name": {"type": "string",
                                      "description": "название файла который нужно прочитать"}},
                    required=["name"]
                )
            ),
            Function(
                name="write_file",
                description="Вызывай чтобы записать текст в файл",
                parameters=FunctionParameters(
                    type="object",
                    properties={"name": {"type": "string",
                                        "description": "название файла куда нужно записать текст"},
                                "text": {"type": "string",
                                         "description": "содержимое которое нужно записать в файл"}},
                    required=["name", "text"]
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
            args = response.choices[0].message.function_call.arguments
            return ["adding_numbers", adding_numbers(args['a'], args['b'])]

        if func_name == "ls":
            return ["ls", ls()]

        if func_name == "create_file":
            args = response.choices[0].message.function_call.arguments
            return ["create_file", create_file(args['name'])]

        if func_name == "read_file":
            args = response.choices[0].message.function_call.arguments
            return ["read_file", read_file(args['name'])]

        if func_name == "write_file":
            args = response.choices[0].message.function_call.arguments
            return ["write_file", write_file(args['name'], args['text'])]


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

        if if_command(prompt, MESSAGES):
            continue
        
        
        USER_PROMT = {"role": "user", "content": prompt}
        MESSAGES.append(USER_PROMT)

        if prompt == "exit":
            break

        response = get_response(client, MESSAGES)


        #print(response, '\n', hasattr(response.choices[0].message, 'function_call'), response.choices[0].message.function_call)

        function_result = handle_function_call(response)
        #print(function_result)

        if function_result:


            FUNCTION_CALL_MESSAGE = {"role": response.choices[0].message.role,
                "content":  response.choices[0].message.content,
                "function_call": {
                    "name": response.choices[0].message.function_call.name,
                    "arguments": response.choices[0].message.function_call.arguments
                }
            }
            MESSAGES.append(FUNCTION_CALL_MESSAGE)


            print(f"\n\n                  Произошел вызов функции!    MODEL: {model} \n")
            FUNCTION_CALL = {"role": "function", "name": function_result[0], "content": function_result[1]}
            MESSAGES.append(FUNCTION_CALL)

            response = get_response(client, MESSAGES)


        print(f"\n\nВам овтетил {model}: {response.choices[0].message.content}")
        ANSWER = {"role": response.choices[0].message.role, "content": response.choices[0].message.content}
        MESSAGES.append(ANSWER)

        print(f"\nПротрачено: {response.usage.total_tokens}")

        #print_MASSAGES(MESSAGES)

        save_response(response, model, function_result)

if __name__ == "__main__":
    main()
