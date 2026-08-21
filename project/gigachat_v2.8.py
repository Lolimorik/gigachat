# gigachat_v2.8.py

import os
import json
import subprocess
from dotenv import load_dotenv
from gigachat import GigaChat
from gigachat.models import Chat, Function, FunctionParameters, FunctionCall
from datetime import datetime

# Загружаем переменные окружения
load_dotenv()

# Вспомогательные функции для работы с временем и терминалом
def get_current_time():
    """Получить текущее время"""
    return json.dumps({"time": datetime.now().strftime("%H:%M:%S")})

def terminal(command):
    """Выполнить команду в терминале"""
    return json.dumps({"list": subprocess.check_output(command, shell=True, text=True)})

# Функции для чтения и записи файлов
def read_file(name_file):
    """Получить содержимое файла"""
    try:
        with open(name_file, "r", encoding="utf-8") as file:
            content = file.read()
        return json.dumps({"res": content})
    except FileNotFoundError:
        return json.dumps({"error": f"Файл {name_file} не найден."})

def write_file(name_file, text):
    """Записать текст в файл"""
    try:
        with open(name_file, "w", encoding="utf-8") as file:
            file.write(text)
        return json.dumps({"res": f"Файл {name_file} успешно обновлен."})
    except Exception as e:
        return json.dumps({"error": str(e)})

# Функция для получения списка файлов в текущей директории
def ls():
    """Получить список файлов в текущей директории"""
    return json.dumps({"list": subprocess.check_output("ls -l", shell=True, text=True)})

# Функция для создания файла
def create_file(name_file):
    """Создать файл"""
    try:
        open(name_file, "w", encoding="utf-8").close()
        return json.dumps({"res": "Файл успешно создан."})
    except Exception as e:
        return json.dumps({"error": str(e)})

# Новая функция для последовательного вызова функций
def sequential_function_call(response):
    if hasattr(response.choices[0].message, 'function_call'):
        func_name = response.choices[0].message.function_call.name
        arguments = response.choices[0].message.function_call.arguments
        
        # Определяем функцию для вызова в зависимости от имени
        if func_name == "get_current_time":
            result = get_current_time()
        elif func_name == "adding_numbers":
            a = float(arguments.get('a', 0))
            b = float(arguments.get('b', 0))
            result = json.dumps({"sum": a + b})
        elif func_name == "ls":
            result = ls()
        elif func_name == "create_file":
            name = arguments.get('name')
            create_file(name)
            result = json.dumps({"res": f"Файл {name} успешно создан."})
        elif func_name == "read_file":
            name = arguments.get('name')
            result = read_file(name)
        elif func_name == "write_file":
            name = arguments.get('name')
            text = arguments.get('text')
            write_file(name, text)
            result = json.dumps({"res": f"Текст успешно записан в файл {name}"})
        elif func_name == "terminal":
            command = arguments.get('command')
            result = terminal(command)
            
        # Возвращаем результат вызова функции
        return result

# Основная функция
def main():
    # Получаем клиента
    client = GigaChat(
        base_url="https://api.giga.chat/v1",
        credentials=os.getenv("API_KEY"),
        scope="GIGACHAT_API_PERS",
        verify_ssl_certs=False
    )

    # Инициализируем модель
    model = "GigaChat-2"

    # Инициализируем историю сообщений
    MESSAGES = [{"role": "system", "content": "Ты - автономный AI-агент..."}]

    while True:
        # Получаем запрос пользователя
        prompt = input("\nВведи запрос: ")

        # Обрабатываем команды пользователя
        if prompt == "\history":
            print_MESSAGES(MESSAGES)
            continue
        if prompt == "\help":
            print("Команды для разработчика:\n"
                  "history - выводит историю текущей сессии\n"
                  "help - выводит команды\n"
                  "exit - аварийное завершение работы")
            continue
        if prompt == "\exit":
            print("\n\n\nПрощай!\n\n\n")
            break

        # Добавляем сообщение пользователя в историю
        USER_PROMT = {"role": "user", "content": prompt}
        MESSAGES.append(USER_PROMT)

        # Получаем ответ от модели
        response = client.chat(Chat(model=model, messages=MESSAGES, function_call="auto"))

        # Последовательно вызываем функции
        while len(response.choices) > 0:
            function_result = sequential_function_call(response)
            if function_result is not None:
                # Добавляем сообщение о вызове функции
                FUNCTION_CALL_MESSAGE = {"role": response.choices[0].message.role,
                                         "content": response.choices[0].message.content,
                                         "function_call": {
                                             "name": response.choices[0].message.function_call.name,
                                             "arguments": response.choices[0].message.function_call.arguments
                                         }}
                MESSAGES.append(FUNCTION_CALL_MESSAGE)

                # Получаем результат вызова функции
                FUNCTION_CALL = {"role": "function", "name": function_result["name"], "content": function_result["res"]}
                MESSAGES.append(FUNCTION_CALL)

                # Получаем ответ от модели после вызова функции
                response = client.chat(Chat(model=model, messages=MESSAGES, function_call="auto"))

        # Выводим ответ модели
        print(f"\n\nВам ответил {model}: {response.choices[0].message.content}")
        ANSWER = {"role": response.choices[0].message.role, "content": response.choices[0].message.content}
        MESSAGES.append(ANSWER)

        # Выводим количество потраченных токенов
        print(f"\nПротрачено: {response.usage.total_tokens}")

        # Сохраняем ответ в файл
        save_response(response, model, function_result)

# Запуск программы
if __name__ == "__main__":
    main()
# конец файла
