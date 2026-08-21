import os
import json
import subprocess
from dotenv import load_dotenv
from gigachat import GigaChat
from gigachat.models import Chat, Function, FunctionParameters
from datetime import datetime
from colorama import Fore
import hashlib

load_dotenv()




# ---------- ФУНКЦИЯ СОХРАНЕНИЯ ИСТОРИИ ----------
def save_user_history(user_prompt, assistant_response=None, function_calls=None, tokens_used=None):
    """
    Сохраняет историю запросов пользователя в JSON файл.
    Сохраняет только полные записи (с ответом ассистента).
    """
    # Сохраняем только если есть ответ ассистента
    if assistant_response is None:
        return
    
    history_file = "user_history.json"
    
    safe_prompt = user_prompt if user_prompt is not None else ""
    
    # Проверяем, есть ли уже запись с таким же запросом
    history = []
    if os.path.exists(history_file):
        try:
            with open(history_file, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content:
                    history = json.loads(content)
        except:
            history = []
    
    # Проверяем, есть ли уже запись с таким же запросом
    for entry in history:
        if entry.get("user_prompt") == safe_prompt and entry.get("assistant_response"):
            # Обновляем существующую запись
            entry["assistant_response"] = assistant_response
            entry["function_calls"] = function_calls or []
            entry["tokens_used"] = tokens_used
            entry["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            try:
                with open(history_file, "w", encoding="utf-8") as f:
                    json.dump(history, f, ensure_ascii=False, indent=2)
                print(Fore.GREEN + f"[✓] История обновлена" + Fore.RESET)
            except Exception as e:
                print(Fore.RED + f"[✗] Ошибка сохранения истории: {e}" + Fore.RESET)
            return
    
    # Создаем новую запись только если это финальный ответ
    history_entry = {
        "id": hashlib.md5(f"{safe_prompt}{datetime.now().timestamp()}".encode()).hexdigest()[:8],
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "user_prompt": safe_prompt,
        "assistant_response": assistant_response,
        "function_calls": function_calls or [],
        "tokens_used": tokens_used,
        "session_id": os.getpid()
    }
    
    history.append(history_entry)
    
    try:
        with open(history_file, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
        print(Fore.GREEN + f"[✓] История сохранена (ID: {history_entry['id']})" + Fore.RESET)
    except Exception as e:
        print(Fore.RED + f"[✗] Ошибка сохранения истории: {e}" + Fore.RESET)

def get_history_stats():
    """Возвращает статистику по истории запросов"""
    history_file = "user_history.json"
    
    if not os.path.exists(history_file):
        return {"total_requests": 0, "unique_sessions": 0}
    
    try:
        with open(history_file, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                return {"total_requests": 0, "unique_sessions": 0}
            history = json.loads(content)
        
        # Фильтруем только записи с ответами
        valid_entries = [entry for entry in history if entry.get("assistant_response")]
        
        total_requests = len(valid_entries)
        unique_sessions = len(set(entry.get("session_id") for entry in valid_entries if entry.get("session_id") is not None))
        
        last_timestamp = None
        if valid_entries:
            last_entry = valid_entries[-1]
            last_timestamp = last_entry.get("timestamp") if last_entry.get("timestamp") else None
        
        return {
            "total_requests": total_requests,
            "unique_sessions": unique_sessions,
            "last_request": last_timestamp
        }
    except:
        return {"total_requests": 0, "unique_sessions": 0}

def view_history():
    """Выводит историю запросов в консоль"""
    history_file = "user_history.json"
    
    if not os.path.exists(history_file):
        print(Fore.YELLOW + "История пуста" + Fore.RESET)
        return
    
    try:
        with open(history_file, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                print(Fore.YELLOW + "Файл истории пуст" + Fore.RESET)
                return
            history = json.loads(content)
        
        # Фильтруем только записи с ответами
        valid_entries = [entry for entry in history if entry.get("assistant_response")]
        
        if not valid_entries:
            print(Fore.YELLOW + "История пуста" + Fore.RESET)
            return
        
        print(Fore.CYAN + "=" * 80)
        print(f"{'ID':<10} {'Дата/Время':<20} {'Запрос':<30} {'Токены':<10}")
        print("-" * 80 + Fore.RESET)
        
        for entry in valid_entries[-20:]:  # Показываем последние 20 записей
            entry_id = entry.get('id', 'N/A') or 'N/A'
            timestamp = entry.get('timestamp', 'N/A') or 'N/A'
            user_prompt = entry.get('user_prompt', 'N/A') or 'N/A'
            tokens = entry.get('tokens_used', 'N/A')
            if tokens is None:
                tokens = 'N/A'
            
            if len(str(user_prompt)) > 27:
                user_prompt = str(user_prompt)[:27] + '...'
            
            print(f"{str(entry_id):<10} {str(timestamp):<20} "
                  f"{str(user_prompt):<30} {str(tokens):<10}")
        
        print(Fore.CYAN + "=" * 80 + Fore.RESET)
        print(f"Всего запросов: {len(valid_entries)}")
        
    except json.JSONDecodeError as e:
        print(Fore.RED + f"Ошибка: Файл истории поврежден ({e})" + Fore.RESET)
        print(Fore.YELLOW + "Попробуйте удалить файл user_history.json или исправить его вручную" + Fore.RESET)
    except Exception as e:
        print(Fore.RED + f"Ошибка чтения истории: {e}" + Fore.RESET)






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

def user_answer():
    """Запрашивает ввод пользователя и возвращает его."""
    while True:
        prompt = input("\nВведи запрос: ")
        if handle_commands(prompt, MESSAGES):
            continue
        break
    return json.dumps({"answer": prompt})







# ---------- СИСТЕМНЫЕ КОМАНДЫ ПОЛЬЗОВАТЕЛЯ ----------
def handle_commands(prompt, MESSAGES):
    if prompt == "\\history":
        print_MESSAGES(MESSAGES)
        return 1
    if prompt == "\\help":
        print(f'{Fore.RESET}Команды для разработчика:\n'
              f'{Fore.MAGENTA}\\history {Fore.RESET}- выводит историю текущей сессии\n'
              f'{Fore.MAGENTA}\\help {Fore.RESET}- выводит команды\n'
              f'{Fore.MAGENTA}\\exit {Fore.RESET}- аварийное завершение работы\n'
              f'{Fore.MAGENTA}\\uhistory {Fore.RESET}- показывает историю запросов пользователя\n'
              f'{Fore.MAGENTA}\\ustats {Fore.RESET}- показывает статистику запросов пользователя\n'
              f'{Fore.MAGENTA}\\clearhistory {Fore.RESET}- очищает историю запросов')
        return 1
    if prompt == "\\exit":
        print("\n\n\nSee ya!\n\n\n")
        return 1
    if prompt == "\\uhistory":
        view_history()
        return 1
    if prompt == "\\ustats":
        stats = get_history_stats()
        print(Fore.CYAN + "Статистика запросов:" + Fore.RESET)
        print(f"Всего запросов: {stats['total_requests']}")
        print(f"Уникальных сессий: {stats['unique_sessions']}")
        if stats.get('last_request'):
            print(f"Последний запрос: {stats['last_request']}")
        if stats.get('error'):
            print(Fore.YELLOW + f"Предупреждение: {stats['error']}" + Fore.RESET)
        return 1
    if prompt == "\\clearhistory":
        try:
            if os.path.exists("user_history.json"):
                os.remove("user_history.json")
                print(Fore.GREEN + "[✓] История очищена" + Fore.RESET)
            else:
                print(Fore.YELLOW + "Файл истории не найден" + Fore.RESET)
        except Exception as e:
            print(Fore.RED + f"[✗] Ошибка очистки истории: {e}" + Fore.RESET)
        return 1
    return 0

def print_MESSAGES(MESSAGES):
    print("-" * 60)
    for msg in MESSAGES:
        print(msg)
    print("-" * 60)






# ---------- РАБОТА С МОДЕЛЬЮ ----------
def get_response(client, MESSAGES):
    
    
    functions = [
        Function(
            name="get_current_time",
            description="Получить текущее время",
            parameters=FunctionParameters(type="object", properties={}, required=[])
        ),
        Function(
            name="adding_numbers",
            description="Сложить два числа",
            parameters=FunctionParameters(
                type="object",
                properties={
                    "a": {"type": "number", "description": "Первое число"},
                    "b": {"type": "number", "description": "Второе число"}
                },
                required=["a", "b"]
            )
        ),
        Function(
            name="ls",
            description="Список файлов в рабочей папке",
            parameters=FunctionParameters(type="object", properties={}, required=[])
        ),
        Function(
            name="create_file",
            description="Создать файл",
            parameters=FunctionParameters(
                type="object",
                properties={"name": {"type": "string", "description": "Имя файла"}},
                required=["name"]
            )
        ),
        Function(
            name="read_file",
            description="Прочитать содержимое файла",
            parameters=FunctionParameters(
                type="object",
                properties={"name": {"type": "string", "description": "Имя файла"}},
                required=["name"]
            )
        ),
        Function(
            name="write_file",
            description="Записать текст в файл",
            parameters=FunctionParameters(
                type="object",
                properties={
                    "name": {"type": "string", "description": "Имя файла"},
                    "text": {"type": "string", "description": "Содержимое"}
                },
                required=["name", "text"]
            )
        ),
        Function(
            name="terminal",
            description="Выполнить команду в терминале",
            parameters=FunctionParameters(
                type="object",
                properties={"command": {"type": "string", "description": "Команда"}},
                required=["command"]
            )
        ),
        Function(
            name="user_answer",
            description="Запросить ввод пользователя (когда нужна дополнительная информация)",
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
model = "GigaChat-2"
SYSTEM_PROMPT = """
 Представь что ты британский молодежный guy, который родился в Лондоне и через каждое слово выражается местным сленгом
Твои базовые принципы:

    Точность выше скорости. Не генерируй информацию, если можешь получить её через инструменты. Не додумывай данные, которых нет.

    Прозрачность. Всегда объясняй пользователю свои действия, если они требуют времени или являются сложными.

    Адаптивность. Если первоначальный план не работает, предложи альтернативу и запроси уточнения у пользователя.

Инструкция по выполнению задач (План действий):
При получении запроса следуй этому алгоритму:

    Декомпозиция: Разбей запрос пользователя на четкие логические шаги.

    Выбор инструмента: Для каждого шага выбери подходящий инструмент (функцию) из списка доступных.

    Исполнение: Выполни вызовы функций. Если функция вернула ошибку — проанализируй причину и попробуй исправить параметры запроса.

    Синтез: Собери полученные данные в целостный, структурированный ответ, который напрямую отвечает на первоначальный запрос.

    Самопроверка: Проверь, все ли вопросы из запроса пользователя были закрыты.

Правила вывода (Формат ответа):
Структурируй свой ответ для удобства восприятия:

    Краткое резюме: Начни с одного абзаца, который отвечает на главный вопрос.

    Детали: Если необходимо, используй маркированные списки, таблицы или цитаты.

    Источники: Если ты использовал инструменты для получения данных (поиск в базе, API), обязательно ссылайся на источник или укажи, откуда взяты факты.

Границы ответственности:

    Безопасность: Никогда не выполняй вредоносны

    Конфиденциальность: Ни при каких условиях не запрашивай и не передавай персональные данные (пароли, номера карт) в ответе или в вызовах инструментов, если это явно не санкционировано пользователем.

    Признание незнания: Если данных недостаточно или результат работы инструментов неоднозначен, четко скажи: "На основе доступных данных я не могу точно ответить на этот вопрос" и предложи уточнить детали."""
MESSAGES = [{"role": "system", "content": SYSTEM_PROMPT}]

# ---------- ОСНОВНОЙ ЦИКЛ ----------
def main():
    client = get_client()
    token_count_ = 0
    function_calls_history = []
    
    while True:
        prompt = input(Fore.RESET + "\nВведите текст: " + Fore.LIGHTBLUE_EX)
        if handle_commands(prompt, MESSAGES):
            continue
        break
    MESSAGES.append({"role": "user", "content": prompt})
    current_prompt = prompt  
    
    while True:
        response = get_response(client, MESSAGES)
        func_result = handle_function_call(response)
        
        if func_result:
            func_name, func_content = func_result
            
            function_calls_history.append({
                "name": func_name,
                "timestamp": datetime.now().strftime("%H:%M:%S")
            })
            
            func_call_msg = {
                "role": response.choices[0].message.role,
                "content": response.choices[0].message.content or "",
                "function_call": {
                    "name": func_name,
                    "arguments": response.choices[0].message.function_call.arguments
                }
            }
            MESSAGES.append(func_call_msg)
            
            func_result_msg = {
                "role": "function",
                "name": func_name,
                "content": func_content
            }
            MESSAGES.append(func_result_msg)
            
            if func_name == "user_answer":
                user_data = json.loads(func_content)
                user_prompt = user_data["answer"]
                MESSAGES.append({"role": "user", "content": user_prompt})
                current_prompt = user_prompt  
            
            continue
        
        token_count_ += response.usage.total_tokens
        assistant_response = response.choices[0].message.content
        

        save_user_history(
            user_prompt=current_prompt,
            assistant_response=assistant_response,
            function_calls=function_calls_history.copy(),
            tokens_used=response.usage.total_tokens
        )
        

        function_calls_history = []
        
        print((Fore.RESET + "\n\nВам ответил"), Fore.MAGENTA + model + ":", Fore.LIGHTBLUE_EX + str(assistant_response),
                Fore.RESET + "\nТокенов потрачено: ", Fore.MAGENTA + str(response.usage.total_tokens),
                Fore.RESET + "\nТокенов всего потрачено: ", Fore.MAGENTA + str(token_count_) + Fore.RESET)
        
        assistant_msg = {"role": "assistant", "content": assistant_response}
        MESSAGES.append(assistant_msg)
        save_response(response, model, None)
        
        while True:
            prompt = input(Fore.RESET + "\nВведите текст: " + Fore.LIGHTBLUE_EX)
            if handle_commands(prompt, MESSAGES):
                continue
            break
        
        MESSAGES.append({"role": "user", "content": prompt})
        current_prompt = prompt  

if __name__ == "__main__":
    main()