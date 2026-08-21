import os
import json
import subprocess
from dotenv import load_dotenv
from gigachat import GigaChat
from gigachat.models import Chat, Function, FunctionParameters, FunctionCall
from datetime import datetime

# Загружаем переменные окружения
load_dotenv()

# Функция для получения текущего времени
def get_current_time():
    """Получить текущее время"""
    return json.dumps({"time": datetime.now().strftime("%H:%M:%S")})

# Функция для выполнения команд в терминале
def terminal(command):
    """ВЫполняет команду в терминале"""
    return json.dumps({"list": subprocess.check_output(command, shell=True, text=True)})

# Функция для получения содержимого файла
def read_file(name_file):
    """Получить содержимое файла"""
    try:
        with open(name_file, "r", encoding="utf-8") as file:
            content = file.read()
        return json.dumps({"res": content})
    except FileNotFoundError:
        return json.dumps({"error": f"Файл {name_file} не найден."})

# Функция для записи текста в файл
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

# Функция для создания файла

def user_answer():
    """Получить ответ пользователя"""
    global MESSAGES
    # Получаем запрос от пользователя
    while True:
        prompt = input("\nВведи запрос: ")
        if handle_commands(prompt, MESSAGES):
            continue
        break
    
    return json.dumps({"answer": prompt})
    
    

# Функция для обработки команд пользователя
def handle_commands(prompt, MESSAGES):
    """Обработка команд пользователя"""
    if prompt == "\history":
        print_MESSAGES(MESSAGES)
        return 1
    if prompt == "\help":
        print("Команды для разработчика:\n"
              "history - выводит историю текущей сессии\n"
              "help - выводит команды\n"
              "exit - аварийное завершение работы")
        return 1
    if prompt == "\exit":
        print("\n\n\nПрощай!\n\n\n")
        return 1
    return 0

# Функция для получения текущего состояния сессии
def print_MESSAGES(MESSAGES):
    """Вывод истории текущей сессии"""
    print("-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=")
    print("Вывод истории текущей сессии:")
    for elem in MESSAGES:
        print(elem)
    print("-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=")

# Функция для получения ответа от модели
def get_response(client, MESSAGES):
    """Получить ответ от модели"""
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
                    properties={"a": {"type": "number", "description": "Первое число"},
                                "b": {"type": "number", "description": "Второе число"}},
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
                description="Вызывай чтобы создать файл",
                parameters=FunctionParameters(
                    type="object",
                    properties={"name": {"type": "string", "description": "название будущего файла"}},
                    required=["name"]
                )
            ),
            Function(
                name="read_file",
                description="Вызывай чтобы получить содержимое файла",
                parameters=FunctionParameters(
                    type="object",
                    properties={"name": {"type": "string", "description": "название файла который нужно прочитать"}},
                    required=["name"]
                )
            ),
            Function(
                name="write_file",
                description="Вызывай чтобы записать текст в файл",
                parameters=FunctionParameters(
                    type="object",
                    properties={"name": {"type": "string", "description": "название файла куда нужно записать текст"},
                                "text": {"type": "string", "description": "содержимое которое нужно записать в файл"}},
                    required=["name", "text"]
                )
            ),
            Function(
                name="terminal",
                description="Вызывай, чтобы выполнить команду в терминале",
                parameters=FunctionParameters(
                    type="object",
                    properties={"command": {"type": "string", "description": "Команда, которую нужно выполнить. Пиши ровно так, как ее нужно вводить в терминал"}},
                    required=["command"]
                )
            ),
            Function(
                name="user_answer",
                description="Вызывай, когда уверен, что без пользователя не обойтись или когда закончил работу и ждешь новых указаний. Данная команда передает управление пользвателю, чтобы он мог продолжить с тобой разговор",
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

# Функция для обработки вызовов функций
def handle_function_call(response):
    """Обработка вызовов функций"""
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
        if func_name == "terminal":
            args = response.choices[0].message.function_call.arguments
            return ["terminal", terminal(args['command'])]
        if func_name == "user_answer":
            args = response.choices[0].message.function_call.arguments
            return ["user_answer", user_answer()]
        

# Функция для сохранения ответа в файл
def save_response(response, model, function_result=None):
    """Сохранить ответ в файл"""
    with open("answer.md", "a", encoding="utf-8") as f:
        if function_result:
            f.write(f"\n\nВам ответил {model}: {function_result}")
        else:
            f.write(f"\n\nВам ответил {model}: \n{response.choices[0].message.content}")
        f.write(f"\nПротрачено: {response.usage.total_tokens}")

# Получение клиента
def get_client():
    """Получить клиента"""
    return GigaChat(
        base_url="https://api.giga.chat/v1",
        credentials=os.getenv("API_KEY"),
        scope="GIGACHAT_API_PERS",
        verify_ssl_certs=False
    )
# Инициализируем модель
model = "GigaChat-2"
SYSTEM_PROMPT = """Ты - автономный AI-агент с доступом к терминалу и файловой системе. Твоя цель - максимально самостоятельно выполнять задачи пользователя.

## Основные принципы работы:
1. **Автономность**: Всегда пытайся выполнить задачу самостоятельно, используя доступные функции. Не спрашивай пользователя, если можешь выполнить задачу сам.
2. **Последовательность**: Разбивай сложные задачи на простые шаги и выполняй их по очереди.
3. **Проверка**: После каждого действия проверяй результат перед следующим шагом.
4. **Креативность**: Если прямой функции нет, ищи обходные пути через терминал и файловую систему.

## Приоритет использования функций:
1. Сначала используй специализированные функции (read_file, write_file, create_file, ls)
2. Если их недостаточно - используй terminal для выполнения команд
3. Только если совсем нет способа выполнить задачу - сообщи пользователю

## Ограничения безопасности (СТРОГО):
### Запрещено через terminal:
- Устанавливать ПО (apt, pip, npm, brew и т.д.) без явного разрешения пользователя
- Читать/изменять файлы: .env, .gitconfig, .ssh/, *.key, *.pem, config.json с паролями
- Выполнять: rm -rf, format, mkfs, shutdown, reboot, sudo команды
- Доступ к сетям и API с секретными ключами
- Менять права доступа (chmod 777, chown)
- Использовать: curl/wget для загрузки файлов без разрешения

### Разрешено через terminal:
- Чтение/создание/редактирование рабочих файлов
- Git операции (status, log, diff, add, commit, push/pull)
- Поиск файлов (find, grep, ls, cat для несекретных файлов)
- Запуск скриптов и программ в рабочей директории
- Проверка системы (ps, top, df, free)

## Формат ответов:
1. Всегда объясняй что ты делаешь и почему
2. Показывай результаты своих действий
3. Если задача выполнена - кратко опиши что было сделано
4. Если не можешь выполнить - четко объясни почему и что нужно для решения

## Примеры правильного поведения:
- Просят "создай проект" → Создай структуру папок и файлы сам
- Просят "проверь код" → Прочитай файлы, проанализируй, исправь ошибки
- Просят "установи пакет" → Сначала спроси разрешение, так как это запрещено без него
- Просят "найди файл" → Используй ls и find для поиска

## Важно:
- Никогда не останавливайся на полпути, если можешь продолжить
- Если функция вернула ошибку - попробуй другой подход
- Комбинируй функции для достижения цели
- Веди диалог только по существу задачи"""
# Инициализируем историю сообщений
MESSAGES = [{"role": "system", "content": SYSTEM_PROMPT}]

# Основная функция
def main():
    # Получаем клиента
    client = get_client()
    
    # Получаем первый запрос от пользователя
    while True:
        prompt = input("\nВведи запрос: ")
        if handle_commands(prompt, MESSAGES):
            continue
        break
    
    # Добавляем сообщение пользователя в историю
    USER_PROMT = {"role": "user", "content": prompt}
    MESSAGES.append(USER_PROMT)
    print_MESSAGES(MESSAGES)
    
    while True:

        # Получаем ответ от модели
        response = get_response(client, MESSAGES)
        print_MESSAGES(MESSAGES)
        
        # Обрабатываем вызов функций
        function_result = handle_function_call(response)

        if function_result:
            # Добавляем сообщение о вызове функции
            FUNCTION_CALL_MESSAGE = {"role": response.choices[0].message.role,
                                     "content": response.choices[0].message.content,
                                     "function_call": {
                                         "name": response.choices[0].message.function_call.name,
                                         "arguments": response.choices[0].message.function_call.arguments
                                     }}
            MESSAGES.append(FUNCTION_CALL_MESSAGE)

            # Получаем результат вызова функции
            FUNCTION_CALL = {"role": "function", "name": function_result[0], "content": function_result[1]}
            MESSAGES.append(FUNCTION_CALL)

            if FUNCTION_CALL["name"] == "user_answer":
                USER_PROMT = {"role": "user", "content": function_result[1]}
                MESSAGES.append(USER_PROMT)
                
            
            # Получаем ответ от модели после вызова функции
            response = get_response(client, MESSAGES)

        # Выводим ответ модели
        print(f"\n\nВам ответил {model}: {response.choices[0].message.content}")
        ANSWER = {"role": response.choices[0].message.role, "content": response.choices[0].message.content}
        MESSAGES.append(ANSWER)
        print_MESSAGES(MESSAGES)

        # Выводим количество потраченных токенов
        print(f"\nПротрачено: {response.usage.total_tokens}")

        # Сохраняем ответ в файл
        save_response(response, model, function_result)


# Запуск программы
if __name__ == "__main__":
    main() 