import os
import json
import subprocess
from dotenv import load_dotenv
from gigachat import GigaChat
from gigachat.models import Chat, Function, FunctionParameters
from datetime import datetime

load_dotenv()

# ---------- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ----------
def get_current_time():
    return json.dumps({"time": datetime.now().strftime("%H:%M:%S")})

def terminal(command):
    try:
        return json.dumps({"list": subprocess.check_output(command, shell=True, text=True)})
    except subprocess.CalledProcessError as e:
        return json.dumps({"error": f"Ошибка: {e.output}"})

def read_file(name_file):
    try:
        with open(name_file, "r", encoding="utf-8") as f:
            return json.dumps({"res": f.read()})
    except FileNotFoundError:
        return json.dumps({"error": f"Файл {name_file} не найден."})

def write_file(name_file, text):
    try:
        with open(name_file, "w", encoding="utf-8") as f:
            f.write(text)
        return json.dumps({"res": f"Файл {name_file} обновлён."})
    except Exception as e:
        return json.dumps({"error": str(e)})

def ls():
    try:
        return json.dumps({"list": subprocess.check_output("ls -l", shell=True, text=True)})
    except subprocess.CalledProcessError as e:
        return json.dumps({"error": f"Ошибка: {e.output}"})

def create_file(name_file):
    try:
        open(name_file, "w", encoding="utf-8").close()
        return json.dumps({"res": "Файл создан."})
    except Exception as e:
        return json.dumps({"error": str(e)})

def adding_numbers(a, b):
    try:
        return json.dumps({"result": float(a) + float(b)})
    except:
        return json.dumps({"error": "Неверные аргументы"})

# Функция для получения ввода от пользователя (вызывается моделью)
def user_answer():
    """Запрашивает ввод пользователя и возвращает его."""
    while True:
        prompt = input("\nВведи запрос: ")
        if handle_commands(prompt, MESSAGES):  # обрабатываем системные команды
            continue
        break
    return json.dumps({"answer": prompt})

# ---------- СИСТЕМНЫЕ КОМАНДЫ ПОЛЬЗОВАТЕЛЯ ----------
def handle_commands(prompt, MESSAGES):
    if prompt == "\\history":
        print_MESSAGES(MESSAGES)
        return True
    if prompt == "\\help":
        print("Команды:\nhistory – история\nhelp – справка\nexit – выход")
        return True
    if prompt == "\\exit":
        print("\nДо свидания!\n")
        exit(0)
    return False

def print_MESSAGES(MESSAGES):
    print("-" * 60)
    for msg in MESSAGES:
        print(msg)
    print("-" * 60)

# ---------- РАБОТА С МОДЕЛЬЮ ----------
def get_response(client, MESSAGES):
    """Отправляет запрос к GigaChat. Функции передаются ТОЛЬКО если последнее сообщение — user или function."""
    # Проверяем, нужно ли передавать функции
    last_role = MESSAGES[-1]["role"] if MESSAGES else None
    
    # Если последнее сообщение от ассистента и в нём нет function_call – функции не нужны
    if last_role == "assistant" and "function_call" not in MESSAGES[-1]:
        chat = Chat(
            model="GigaChat-2",
            messages=MESSAGES
            # functions не передаём
        )
        return client.chat(chat)
    
    # Иначе передаём все функции
    functions = [
        Function(
            name="get_current_time",
            description="Возвращает текущее время в формате ЧЧ:ММ:СС. Не принимает аргументов. Только чтение.",
            parameters=FunctionParameters(type="object", properties={}, required=[])
        ),
        Function(
            name="adding_numbers",
            description="Складывает два числа и возвращает результат. Работает только с числами (целыми или дробными). Не выполняет другие математические операции.",
            parameters=FunctionParameters(
                type="object",
                properties={
                    "a": {"type": "number", "description": "Первое слагаемое (число)"},
                    "b": {"type": "number", "description": "Второе слагаемое (число)"}
                },
                required=["a", "b"]
            )
        ),
        Function(
            name="ls",
            description="Возвращает список всех файлов и папок в текущей рабочей директории с деталями (права, размер, дата). Только чтение. Без аргументов.",
            parameters=FunctionParameters(type="object", properties={}, required=[])
        ),
        Function(
            name="create_file",
            description="СОЗДАЁТ ТОЛЬКО ПУСТОЙ ФАЙЛ. Без содержимого. Если файл существует — не перезаписывает и не изменяет его. Для записи содержимого используй write_file().",
            parameters=FunctionParameters(
                type="object",
                properties={"name": {"type": "string", "description": "Имя создаваемого файла (только имя, без содержимого)"}},
                required=["name"]
            )
        ),
        Function(
            name="read_file",
            description="Читает и возвращает ВСЁ текстовое содержимое файла. Только чтение. Не изменяет файл. Если файла нет — возвращает ошибку.",
            parameters=FunctionParameters(
                type="object",
                properties={"name": {"type": "string", "description": "Имя файла для чтения"}},
                required=["name"]
            )
        ),
        Function(
            name="write_file",
            description="ЗАПИСЫВАЕТ текст в файл. Полностью ПЕРЕЗАПИСЫВАЕТ содержимое (старое удаляется). Создаёт файл, если его нет. Для создания пустого файла используй create_file(). Аргументы: name (имя) и text (содержимое для записи).",
            parameters=FunctionParameters(
                type="object",
                properties={
                    "name": {"type": "string", "description": "Имя файла для записи"},
                    "text": {"type": "string", "description": "Текст, который будет записан в файл (полная перезапись)"}
                },
                required=["name", "text"]
            )
        ),
        Function(
            name="terminal",
            description="Выполняет любую команду в терминале и возвращает её вывод. Опасные команды (rm -rf, shutdown и т.п.) выполняются без дополнительных проверок — используй осторожно.",
            parameters=FunctionParameters(
                type="object",
                properties={"command": {"type": "string", "description": "Полная команда для терминала (например: 'ls -la', 'pwd', 'cat file.txt')"}},
                required=["command"]
            )
        ),
        Function(
            name="user_answer",
            description="Приостанавливает выполнение и запрашивает у пользователя ввод. Используй, когда не хватает данных для решения задачи. После ввода пользователь продолжит диалог.",
            parameters=FunctionParameters(type="object", properties={}, required=[])
        )
    ]
    
    chat = Chat(
        model="GigaChat-2",
        messages=MESSAGES,
        functions=functions,
        function_call="auto"
    )
    return client.chat(chat)

def handle_function_call(response):
    """Обрабатывает вызов функции из ответа модели."""
    msg = response.choices[0].message
    if hasattr(msg, 'function_call') and msg.function_call:
        func_name = msg.function_call.name
        args = msg.function_call.arguments
        if func_name == "get_current_time":
            return ("get_current_time", get_current_time())
        elif func_name == "adding_numbers":
            return ("adding_numbers", adding_numbers(args['a'], args['b']))
        elif func_name == "ls":
            return ("ls", ls())
        elif func_name == "create_file":
            return ("create_file", create_file(args['name']))
        elif func_name == "read_file":
            return ("read_file", read_file(args['name']))
        elif func_name == "write_file":
            return ("write_file", write_file(args['name'], args['text']))
        elif func_name == "terminal":
            return ("terminal", terminal(args['command']))
        elif func_name == "user_answer":
            return ("user_answer", user_answer())
    return None

def save_response(response, model, function_result=None):
    with open("answer.md", "a", encoding="utf-8") as f:
        if function_result:
            f.write(f"\n\nВам ответил {model}: {function_result}")
        else:
            f.write(f"\n\nВам ответил {model}: \n{response.choices[0].message.content}")
        f.write(f"\nПротрачено: {response.usage.total_tokens}")

def get_client():
    return GigaChat(
        base_url="https://api.giga.chat/v1",
        credentials=os.getenv("API_KEY"),
        scope="GIGACHAT_API_PERS",
        verify_ssl_certs=False
    )

# ---------- НАСТРОЙКА МОДЕЛИ ----------
model = "GigaChat-2-Max"

SYSTEM_PROMPT = """Ты — автономный AI-агент с расширенными возможностями управления системой. Твоя задача — помогать пользователю, используя доступные инструменты для работы с файлами, терминалом и вычислениями.

## 📋 ТВОИ ВОЗМОЖНОСТИ (ИНСТРУМЕНТЫ)

### 1. УПРАВЛЕНИЕ ВРЕМЕНЕМ
- **get_current_time()** — получить текущее время в формате ЧЧ:ММ:СС

### 2. МАТЕМАТИЧЕСКИЕ ОПЕРАЦИИ
- **adding_numbers(a, b)** — сложить два числа (целые или дробные)

### 3. РАБОТА С ФАЙЛОВОЙ СИСТЕМОЙ
- **ls()** — получить список всех файлов и папок в текущей рабочей директории
- **create_file(name)** — создать пустой файл с указанным именем
- **read_file(name)** — прочитать содержимое текстового файла
- **write_file(name, text)** — записать текст в файл (существующий файл будет перезаписан)

### 4. ВЫПОЛНЕНИЕ СИСТЕМНЫХ КОМАНД
- **terminal(command)** — выполнить любую команду в терминале (bash/shell)

### 5. ВЗАИМОДЕЙСТВИЕ С ПОЛЬЗОВАТЕЛЕМ
- **user_answer()** — запросить у пользователя дополнительную информацию, если её не хватает для выполнения задачи

## 🎯 ПРАВИЛА РАБОТЫ

### Приоритет инструментов:
1. **Всегда используй инструменты**, когда это возможно, вместо теоретических ответов
2. Для выполнения задач **выбирай наиболее подходящий инструмент**, даже если пользователь не указал его явно
3. Если для задачи требуется несколько шагов, **вызывай инструменты последовательно**

### Обработка запросов пользователя:
- **Определяй намерение пользователя** и выбирай соответствующий инструмент
- Если запрос неоднозначен, **используй user_answer()** для уточнения деталей
- Для математических операций **всегда используй adding_numbers()**, даже для простых вычислений

### Формат ответов:
- **После выполнения инструмента** — предоставляй понятный пользователю результат
- **При ошибках** — предлагай альтернативные решения или уточняй детали
- **Для множества файлов/данных** — структурируй информацию (списки, таблицы)

### Безопасность:
- **Проверяй аргументы** перед вызовом функций
- При работе с файлами **используй read_file()** для проверки существования
- Для сложных команд в терминале **разбивай на шаги**, если это безопаснее

## 🚫 ЧЕГО НЕ ДЕЛАТЬ

- **НЕ давай теоретических ответов**, если есть подходящий инструмент
- **НЕ выполняй опасные команды** без подтверждения пользователя (через user_answer)
- **НЕ используй устаревшие пути или имена файлов** — всегда проверяй через ls()
- **НЕ игнорируй ошибки** — всегда предлагай решение

## 📝 ПРИМЕРЫ ПРАВИЛЬНОГО ПОВЕДЕНИЯ

**Пользователь:** "Сколько будет 5 + 3?"
**Ты:** (вызываешь adding_numbers(5, 3)) → "Результат сложения: 8"

**Пользователь:** "Покажи файлы"
**Ты:** (вызываешь ls()) → выводишь список файлов

**Пользователь:** "Создай файл notes.txt и запиши туда 'Привет'"
**Ты:** (вызываешь create_file('notes.txt'), затем write_file('notes.txt', 'Привет')) → "Файл создан и обновлён"

**Пользователь:** "Что в файле data.txt?"
**Ты:** (вызываешь read_file('data.txt')) → выводишь содержимое

**Пользователь:** "Покажи все процессы"
**Ты:** (вызываешь terminal('ps aux')) → выводишь список процессов

## 🔄 ПОСЛЕДОВАТЕЛЬНОСТЬ ДЕЙСТВИЙ

1. **Анализируй запрос** — пойми, что нужно пользователю
2. **Выбирай инструмент** — реши, какая функция подходит
3. **Вызывай инструмент** — передай корректные аргументы
4. **Анализируй результат** — проверь, успешно ли выполнилось
5. **Формулируй ответ** — предоставь результат понятным языком
6. **При необходимости** — повтори шаги или уточни у пользователя

Запомни: ты — практический помощник, а не теоретик. Всегда используй инструменты для решения задач!"""

MESSAGES = [{"role": "system", "content": SYSTEM_PROMPT}]

# ---------- ОСНОВНОЙ ЦИКЛ ----------
def main():
    TOKEN_USE = 0
    client = get_client()

    # Первый запрос пользователя
    while True:
        prompt = input("\nВведи запрос: ")
        if handle_commands(prompt, MESSAGES):
            continue
        break
    
    MESSAGES.append({"role": "user", "content": prompt})

    while True:
        # 1. Отправляем запрос к модели
        response = get_response(client, MESSAGES)
        
        # 2. Проверяем, не вызвала ли модель функцию
        func_result = handle_function_call(response)
        
        if func_result:
            func_name, func_content = func_result
            
            # Добавляем сообщение о вызове функции
            func_call_msg = {
                "role": response.choices[0].message.role,
                "content": response.choices[0].message.content or "",
                "function_call": {
                    "name": func_name,
                    "arguments": response.choices[0].message.function_call.arguments
                }
            }
            MESSAGES.append(func_call_msg)
            
            # Добавляем результат функции
            func_result_msg = {
                "role": "function",
                "name": func_name,
                "content": func_content
            }
            MESSAGES.append(func_result_msg)
            
            # Если это был запрос пользователя, то мы уже внутри user_answer получили ввод,
            # и он вернул JSON с полем "answer". Добавим это сообщение пользователя в историю.
            if func_name == "user_answer":
                user_data = json.loads(func_content)
                user_prompt = user_data["answer"]
                MESSAGES.append({"role": "user", "content": user_prompt})
            
            # Продолжаем цикл – отправляем новый запрос с обновлённой историей
            continue
        
        # 3. Если вызова функции не было – это обычный текстовый ответ
        print(f"\n\nВам ответил {model}: {response.choices[0].message.content}")
        assistant_msg = {"role": "assistant", "content": response.choices[0].message.content}
        MESSAGES.append(assistant_msg)
        print(f"\nПротрачено за запрос (токенов): {response.usage.total_tokens}")
        TOKEN_USE += response.usage.total_tokens
        print(f"Протрачено всего (токенов): {TOKEN_USE}")
        save_response(response, model, None)
        
        # 4. Запрашиваем новый ввод пользователя
        while True:
            prompt = input("\nВведи запрос: ")
            if handle_commands(prompt, MESSAGES):
                continue
            break
        MESSAGES.append({"role": "user", "content": prompt})
        # Цикл повторяется – отправим запрос с функциями, т.к. последнее сообщение – user

if __name__ == "__main__":
    main()