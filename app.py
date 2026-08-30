import os
import json
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

DATA_FILE = '/tmp/data.json' if os.path.exists('/tmp') else 'data.json'

TRACKS = {
    'med_math': 'مسار الطب وعلوم الحياة / رياضيات',
    'med_physics': 'مسار طب وعلوم الحياة / فيزياء',
    'eng_chem': 'مسار الهندسة وعلوم الحاسب / كيمياء',
    'eng_prog': 'مسار الهندسة وعلوم الحاسب / برمجة',
    'biz_acct': 'مسار الأعمال / محاسبة',
    'biz_mgmt': 'مسار الأعمال / إدارة أعمال',
    'art_psych': 'مسار الآداب والفنون / علم نفس',
    'art_lang': 'مسار الآداب والفنون / لغة أجنبية ثانية'
}

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, dict):
                    return data
        except Exception:
            pass
    return {
        "books": [],
        "platforms": [],
        "lessons": {key: [] for key in TRACKS.keys()}
    }

def save_data(data):
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print("Save error:", e)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/books')
def books():
    data = load_data()
    books_list = data.get('books', []) if isinstance(data, dict) else []
    return render_template('books.html', books=books_list)

@app.route('/platforms')
def platforms():
    data = load_data()
    platforms_list = data.get('platforms', []) if isinstance(data, dict) else []
    return render_template('platforms.html', platforms=platforms_list)

@app.route('/tracks')
def tracks():
    return render_template('tracks.html', tracks=TRACKS)

@app.route('/lessons/<track_id>')
def lessons(track_id):
    data = load_data()
    title = TRACKS.get(track_id, "الشروحات والمراجعات")
    
    lessons_dict = data.get("lessons", {}) if isinstance(data, dict) else {}
    items = []
    if isinstance(lessons_dict, dict):
        items = lessons_dict.get(track_id, [])
        if not isinstance(items, list):
            items = []

    grouped_lessons = {}
    for item in items:
        if isinstance(item, dict):
            sec = item.get('section', 'شروحات عامة') or 'شروحات عامة'
            if sec not in grouped_lessons:
                grouped_lessons[sec] = []
            grouped_lessons[sec].append(item)

    return render_template('lessons.html', title=title, grouped_lessons=grouped_lessons)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    data = load_data()
    if request.method == 'POST':
        category = request.form.get('category')
        title = request.form.get('title')
        link = request.form.get('link')
        track = request.form.get('track')
        section = request.form.get('section', '').strip() or 'شروحات عامة'

        if category == 'book':
            if 'books' not in data or not isinstance(data['books'], list): 
                data['books'] = []
            data['books'].append({'title': title, 'link': link})

        elif category == 'platform':
            if 'platforms' not in data or not isinstance(data['platforms'], list): 
                data['platforms'] = []
            data['platforms'].append({'title': title, 'link': link})

        elif category == 'lesson' and track:
            if 'lessons' not in data or not isinstance(data['lessons'], dict): 
                data['lessons'] = {}
            if track not in data['lessons'] or not isinstance(data['lessons'][track], list): 
                data['lessons'][track] = []
            data['lessons'][track].append({'title': title, 'link': link, 'section': section})

        save_data(data)
        return redirect(url_for('admin'))

    return render_template('admin.html', tracks=TRACKS)

if __name__ == '__main__':
    app.run(debug=True)
