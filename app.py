from flask import Flask, render_template, request, redirect
import json
from datetime import datetime
import requests
import pytz

app = Flask(__name__, static_folder='static')
NEWS_FILE = 'news.json'

def load_news():
    try:
        with open(NEWS_FILE, 'r') as f:
            return json.load(f)
    except:
        return []

def save_news(data):
    with open(NEWS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def get_show():
    now = datetime.now(pytz.timezone('Africa/Johannesburg'))
    h = now.hour + now.minute/60
    shows = [
        (6, 9, '06:00-09:00', 'Re Moteng Breakfast Show'),
        (9, 12, '09:00-12:00', 'Midday Connect'),
        (12, 15, '12:00-15:00', 'Re Mmogo'),
        (15, 18, '15:00-18:00', 'Best Drive Show'),
        (18, 19, '18:00-19:00', 'Sports Corner'),
        (19, 21, '19:00-21:00', 'Take Me To Bed With Bra Jay')
    ]
    for s in shows:
        if s[0] <= h < s[1]:
            return {'time': s[2], 'name': s[3]}
    return None

def fetch_news():
    try:
        # Try South Africa first
        url = 'https://newsapi.org/v2/top-headlines?country=za&apiKey=24269104ec924f07aecb456c6d94b0f4'
        r = requests.get(url)
        data = r.json()
        
        if data['status'] == 'ok' and len(data['articles']) > 0:
            articles = []
            for item in data['articles'][:5]:
                articles.append({
                    'date': datetime.now(pytz.timezone('Africa/Johannesburg')).strftime('%d %b').upper(),
                    'title': item['title'],
                    'summary': item['description'] or 'Read more...',
                    'url': item['url']
                })
            return articles
        else:
            # Fallback to US news
            url2 = 'https://newsapi.org/v2/top-headlines?country=us&apiKey=24269104ec924f07aecb456c6d94b0f4'
            r2 = requests.get(url2)
            data2 = r2.json()
            articles = []
            for item in data2['articles'][:5]:
                articles.append({
                    'date': datetime.now(pytz.timezone('Africa/Johannesburg')).strftime('%d %b').upper(),
                    'title': item['title'],
                    'summary': item['description'] or 'Read more...',
                    'url': item['url']
                })
            return articles
    except:
        return load_news()

@app.route('/')
def index():
    news = fetch_news()
    show = get_show()
    return render_template('index.html', news=news, show=show)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        news = load_news()
        news.append({
            'date': request.form['date'],
            'title': request.form['title'],
            'summary': request.form['summary']
        })
        save_news(news)
        return redirect('/admin')
    return render_template('admin.html', news=load_news())

@app.route('/delete/<int:idx>')
def delete(idx):
    news = load_news()
    if idx < len(news):
        news.pop(idx)
        save_news(news)
    return redirect('/admin')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)