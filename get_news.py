import config as cfg

import requests

appid = input("ID игры, новости которой хотите получить: ")
url = f'https://api.steampowered.com/ISteamNews/GetNewsForApp/v0002/&count=1&format=json'
params = {'key': cfg.API_KEY, 'appids': appid}

response = requests.get(url, params=params)
data = response.json()

news_title = data['appnews']['newsitems'][0]['title']
news_url = ''.join(data['appnews']['newsitems'][0]['url'].split(' '))
print(f'Последняя новость о игре: {news_title}')
print(f'Ссылка на новость: {news_url}')
