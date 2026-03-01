import requests
from bot.core import config

def create_task(title, description, member_name=None):
    """
    Создает карточку в Trello [4]
    """
    url = "https://api.trello.com/1/cards"
    
    params = {
        'key': config.TRELLO_API_KEY,
        'token': config.TRELLO_API_TOKEN,
        'idList': config.TRELLO_LIST_ID,
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