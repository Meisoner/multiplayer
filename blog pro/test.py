from requests import get, post

print(get('http://localhost:5000/api/v2/news').json())

print(get('http://localhost:5000/api/v2/news/1').json())

print(get('http://localhost:5000/api/v2/news/999').json())

print(get('http://localhost:5000/api/v2/news/q').json())

print(post('http://localhost:5000/api/v2/news').json())

print(post('http://localhost:5000/api/v2/news',
           json={'title': 'Заголовок'}).json())

print(post('http://localhost:5000/api/v2/news',
           json={'title': 'Заголовок',
                 'content': 'Текст новости',
                 'user_id': 1,
                 'is_private': False}).json())