import os
import json
from flask import Flask, render_template, request, redirect, url_for, session
from upstash_redis import Redis

app = Flask(__name__)
app.secret_key = 'medo_bac_2026_secret_key'

WHATSAPP_NUMBER = "201110388238"

# الاتصال بقاعدة بيانات Upstash / Vercel KV تلقائياً
url = os.getenv("UPSTASH_REDIS_REST_URL") or os.getenv("KV_REST_API_URL")
token = os.getenv("UPSTASH_REDIS_REST_TOKEN") or os.getenv("KV_REST_API_TOKEN")

redis = Redis(url=url, token=token) if url and token else None

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
    if redis:
        try:
            raw = redis.get('site_data')
            if raw:
                data = json.loads(raw) if isinstance(raw, str) else raw
                if isinstance(data, dict):
                    data.setdefault('users', [])
                    data.setdefault('books', [])
                    data.setdefault('platforms', [])
                    data.setdefault('lessons', {key: [] for key in TRACKS.keys()})
                    data.setdefault('forum', [])
                    data.setdefault('notes', {})
                    return data
        except Exception as e:
            print("Redis load error:", e)

    return {
        "users": [],
        "books": [],
        "platforms": [],
        "lessons": {key: [] for key in TRACKS.keys()},
        "forum": [],
        "notes": {}
    }

def save_data(data):
    if redis:
        try:
            redis.set('site_data', json.dumps(data, ensure_ascii=False))
        except Exception as e:
            print("Redis save error:", e)

@app.context_processor
def inject_globals():
    data = load_data()
    user_note = ""
    if 'user' in session:
        user_note = data.get('notes', {}).get(session['user'], "")
    return {
        'whatsapp_number': WHATSAPP_NUMBER,
        'whatsapp_link': f"https://wa.me/{WHATSAPP_NUMBER}",
        'user_note': user_note
    }

# --- مسارات الحسابات والتسجيل ---

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        identifier = request.form.get('identifier', '').strip()
        password = request.form.get('password', '').strip()
        
        if identifier and password:
            data = load_data()
            for u in data.get('users', []):
                if u.get('identifier') == identifier:
                    return "الحساب مسجل بالفعل! <a href='/login'>سجل دخولك من هنا</a>"
            
            data['users'].append({
                'name': name or 'مستخدم',
                'identifier': identifier, 
                'password': password
            })
            save_data(data)
            session['user'] = name or identifier
            return redirect(url_for('index'))
            
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        identifier = request.form.get('identifier', '').strip()
        password = request.form.get('password', '').strip()
        
        data = load_data()
        for u in data.get('users', []):
            if u.get('identifier') == identifier and u.get('password') == password:
                session['user'] = u.get('name', identifier)
                return redirect(url_for('index'))
        
        return "بيانات الدخول غير صحيحة! <a href='/login'>حاول مرة أخرى</a>"
        
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

# --- مسارات المنصة الرئيسية ---

@app.route('/')
def index():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('index.html', user=session.get('user'))

@app.route('/books')
def books():
    if 'user' not in session:
        return redirect(url_for('login'))
    data = load_data()
    return render_template('books.html', books=data.get('books', []))

@app.route('/platforms')
def platforms():
    if 'user' not in session:
        return redirect(url_for('login'))
    data = load_data()
    return render_template('platforms.html', platforms=data.get('platforms', []))

@app.route('/tracks')
def tracks():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('tracks.html', tracks=TRACKS)

@app.route('/lessons/<track_id>')
def lessons(track_id):
    if 'user' not in session:
        return redirect(url_for('login'))
    data = load_data()
    title = TRACKS.get(track_id, "الشروحات والمراجعات")
    lessons_dict = data.get("lessons", {}) if isinstance(data, dict) else {}
    items = lessons_dict.get(track_id, []) if isinstance(lessons_dict, dict) else []
    
    grouped_lessons = {}
    for item in items:
        if isinstance(item, dict):
            sec = item.get('section', 'شروحات عامة') or 'شروحات عامة'
            if sec not in grouped_lessons:
                grouped_lessons[sec] = []
            grouped_lessons[sec].append(item)

    return render_template('lessons.html', title=title, grouped_lessons=grouped_lessons)

# --- مسار المنتدى والملاحظات ---

@app.route('/forum', methods=['GET', 'POST'])
def forum():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    data = load_data()
    if request.method == 'POST':
        question = request.form.get('question', '').strip()
        if question:
            data.setdefault('forum', [])
            data['forum'].append({
                'user': session.get('user'),
                'question': question,
                'reply': None
            })
            save_data(data)
            return redirect(url_for('forum'))

    return render_template('forum.html', forum=data.get('forum', []))

@app.route('/save_note', methods=['POST'])
def save_note():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    note_text = request.form.get('note', '').strip()
    user_key = session.get('user')
    
    data = load_data()
    data.setdefault('notes', {})
    data['notes'][user_key] = note_text
    save_data(data)
    
    return redirect(request.referrer or url_for('index'))

# --- لوحة التحكم للأدمن ---

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST' and 'auth_password' in request.form:
        raw_pass = request.form.get('auth_password', '')
        cleaned_pass = "".join(c for c in raw_pass if c.isalnum()).lower()
        
        if cleaned_pass == "medo2026":
            session['logged_in'] = True
        else:
            return render_template('admin_login.html', error="كلمة السر غير صحيحة!")

    if not session.get('logged_in'):
        return render_template('admin_login.html')

    data = load_data()
    
    if request.method == 'POST' and 'category' in request.form:
        category = request.form.get('category')
        title = request.form.get('title')
        link = request.form.get('link')
        track = request.form.get('track')
        section = request.form.get('section', '').strip() or 'شروحات عامة'

        if category == 'book':
            data.setdefault('books', []).append({'title': title, 'link': link})
        elif category == 'platform':
            data.setdefault('platforms', []).append({'title': title, 'link': link})
        elif category == 'lesson' and track:
            data.setdefault('lessons', {}).setdefault(track, []).append({'title': title, 'link': link, 'section': section})

        save_data(data)
        return redirect(url_for('admin'))

    users = data.get('users', [])
    total_users = len(users)

    return render_template('admin.html', tracks=TRACKS, data=data, users=users, total_users=total_users, forum=data.get('forum', []))

@app.route('/admin/reply_forum/<int:index>', methods=['POST'])
def reply_forum(index):
    if not session.get('logged_in'):
        return redirect(url_for('admin'))

    reply_text = request.form.get('reply', '').strip()
    data = load_data()
    if 'forum' in data and len(data['forum']) > index:
        data['forum'][index]['reply'] = reply_text
        save_data(data)
    return redirect(url_for('admin'))

@app.route('/admin/delete/<cat_type>/<int:index>', methods=['POST'])
def delete_item(cat_type, index):
    if not session.get('logged_in'):
        return redirect(url_for('admin'))

    data = load_data()
    if cat_type in ['book', 'platform']:
        if cat_type + 's' in data and len(data[cat_type + 's']) > index:
            data[cat_type + 's'].pop(index)
            save_data(data)
    elif cat_type.startswith('lesson_'):
        track_key = cat_type.replace('lesson_', '')
        if 'lessons' in data and track_key in data['lessons']:
            if len(data['lessons'][track_key]) > index:
                data['lessons'][track_key].pop(index)
                save_data(data)
    elif cat_type == 'forum':
        if 'forum' in data and len(data['forum']) > index:
            data['forum'].pop(index)
            save_data(data)

    return redirect(url_for('admin'))

if __name__ == '__main__':
    app.run(debug=True)
