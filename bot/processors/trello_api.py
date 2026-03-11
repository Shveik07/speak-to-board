import requests
from bot.core import config

#Функция получения списков доски
def get_board_lists():
    # Запрос API. Возвращает список всех колонок на доске.
    url = f"https://api.trello.com/1/boards/{config.TRELLO_BOARD_ID}/lists"
    params = {
        'key': config.TRELLO_API_KEY,
        'token': config.TRELLO_API_TOKEN
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Ошибка получения списков Trello: {e}")
        return []

def create_task(title, description, member_name=None, list_id=None):
    # Создаём карточку в указанном списке (или в списке по умолчанию).
    if list_id is None:
        list_id = config.TRELLO_LIST_ID

    url = "https://api.trello.com/1/cards"
    
    params = {
        'key': config.TRELLO_API_KEY,
        'token': config.TRELLO_API_TOKEN,
        'idList': list_id,
        'name': title,
            'desc': description,
        'due': None
    }
    
    try:
        response = requests.post(url, params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Ошибка создания задачи в Trello: {e}")
        return None

def find_member_by_name(member_name):
    """
    Поиск участника доски по имени
    """
    url = f"https://api.trello.com/1/boards/{config.TRELLO_BOARD_ID}/members"
    params = {
        'key': config.TRELLO_API_KEY,
        'token': config.TRELLO_API_TOKEN
    }
    
    try:
        response = requests.get(url, params=params)
        members = response.json()
        for member in members:
            if member_name.lower() in member['fullName'].lower():
                return member
        return None
    except:
        return None