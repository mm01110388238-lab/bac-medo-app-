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

GENERAL_SUBJECTS = {
    'arabic': 'اللغة العربية',
    'history': 'التاريخ المصري',
    'english': 'اللغة الأجنبية الأولى'
}

SECTION_NAMES = {
    'books': 'الكتب الدراسية',
    'summaries': 'المذكرات والتلخيصات',
    'evaluations': 'التقييمات المدرسية',
    'lessons': 'الشروحات والمسارات'
}

def load_data():
    default_data = {
        "users": [],
        "books": [],
        "summaries": [],
        "evaluations": [],
        "platforms": [],
        "lessons": {key: [] for key in TRACKS.keys()},
        "general_items": {
            "books": {key: [] for key in GENERAL_SUBJECTS.keys()},
            "summaries": {key: [] for key in GENERAL_SUBJECTS.keys()},
            "evaluations": {key: [] for key in GENERAL_SUBJECTS.keys()},
            "lessons": {key: [] for key in GENERAL_SUBJECTS.keys()}
        },
        "specialized_items": {
            "books": {key: [] for key in TRACKS.keys()},
            "summaries": {key: [] for key in TRACKS.keys()},
            "evaluations": {key: [] for key in TRACKS.keys()},
            "lessons": {key: [] for key in TRACKS.keys()}
        },
        "forum": [],
        "notes": {}
    }
    
    if redis:
        try:
            raw = redis.get('site_data')
            if raw:
                data = json.loads(raw) if isinstance(raw, str) else raw
                if isinstance(data, dict):
                    data.setdefault('users', [])
                    data.setdefault('books', [])
                    data.setdefault('summaries', [])
                    data.setdefault('evaluations', [])
                    data.setdefault('platforms', [])
                    data.setdefault('lessons', {key: [] for key in TRACKS.keys()})
                    
                    # تهيئة أقسام المواد الأساسية والتخصصية
                    gen = data.setdefault('general_items', {})
                    for cat in ['books', 'summaries', 'evaluations', 'lessons']:
                        gen.setdefault(cat, {})
                        for sub in GENERAL_SUBJECTS.keys():
                            gen[cat].setdefault(sub, [])

                    spec = data.setdefault('specialized_items', {})
                    for cat in ['books', 'summaries', 'evaluations', 'lessons']:
                        spec.setdefault(cat, {})
                        for trk in TRACKS.keys():
                            spec[cat].setdefault(trk, [])
                            
                    data.setdefault('forum', [])
                    data.setdefault('notes', {})
                    return data
        except Exception as e:
            print("Redis load error:", e)

    return default_data

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
        user_note = data.get('notes', {}).get(str(session['user']), "")
    return {
        'whatsapp_number': WHATSAPP_NUMBER,
        'whatsapp_link': f"https://wa.me/{WHATSAPP_NUMBER}",
        'user_note': user_note,
        'SECTION_NAMES': SECTION_NAMES,
        'GENERAL_SUBJECTS': GENERAL_SUBJECTS,
        'TRACKS': TRACKS
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

# 1. صفحة اختيار نوع المواد (أساسية أم تخصصية)
@app.route('/select_type/<cat_type>')
def select_type(cat_type):
    if 'user' not in session:
        return redirect(url_for('login'))
    if cat_type not in SECTION_NAMES:
        return redirect(url_for('index'))
    
    cat_title = SECTION_NAMES[cat_type]
    return render_template('select_type.html', cat_type=cat_type, cat_title=cat_title)

# 2. صفحة المواد الأساسية لجميع المسارات
@app.route('/general/<cat_type>')
def general_subjects(cat_type):
    if 'user' not in session:
        return redirect(url_for('login'))
    if cat_type not in SECTION_NAMES:
        return redirect(url_for('index'))
        
    cat_title = SECTION_NAMES[cat_type]
    return render_template('general_subjects.html', cat_type=cat_type, cat_title=cat_title, subjects=GENERAL_SUBJECTS)

# 3. عرض المحتوى لمادة أساسية محددة
@app.route('/general/<cat_type>/<subject_id>')
def general_items(cat_type, subject_id):
    if 'user' not in session:
        return redirect(url_for('login'))
        
    data = load_data()
    subject_title = GENERAL_SUBJECTS.get(subject_id, "المادة الأساسية")
    cat_title = SECTION_NAMES.get(cat_type, "")
    
    items = data.get('general_items', {}).get(cat_type, {}).get(subject_id, [])
    
    template_map = {
        'books': 'books.html',
        'summaries': 'summaries.html',
        'evaluations': 'evaluations.html',
        'lessons': 'lessons.html'
    }
    template_name = template_map.get(cat_type, 'books.html')
    
    context = {
        'title': f"{cat_title} - {subject_title}",
        'items': items,
        'books': items if cat_type == 'books' else [],
        'summaries': items if cat_type == 'summaries' else [],
        'evaluations': items if cat_type == 'evaluations' else [],
        'back_url': url_for('general_subjects', cat_type=cat_type)
    }
    return render_template(template_name, **context)

# 4. صفحة اختيار المسار التخصصي
@app.route('/specialized/<cat_type>')
def specialized_tracks(cat_type):
    if 'user' not in session:
        return redirect(url_for('login'))
    if cat_type not in SECTION_NAMES:
        return redirect(url_for('index'))
        
    cat_title = SECTION_NAMES[cat_type]
    return render_template('tracks.html', tracks=TRACKS, cat_type=cat_type, cat_title=cat_title)

# 5. عرض المحتوى لمسار تخصصي محدد
@app.route('/specialized/<cat_type>/<track_id>')
def specialized_items(cat_type, track_id):
    if 'user' not in session:
        return redirect(url_for('login'))
        
    data = load_data()
    track_title = TRACKS.get(track_id, "المسار التخصصي")
    cat_title = SECTION_NAMES.get(cat_type, "")
    
    if cat_type == 'lessons':
        items = data.get('specialized_items', {}).get('lessons', {}).get(track_id, [])
        if not items:
            items = data.get('lessons', {}).get(track_id, [])
    else:
        items = data.get('specialized_items', {}).get(cat_type, {}).get(track_id, [])
        
    template_map = {
        'books': 'books.html',
        'summaries': 'summaries.html',
        'evaluations': 'evaluations.html',
        'lessons': 'lessons.html'
    }
    template_name = template_map.get(cat_type, 'books.html')
    
    grouped_lessons = {}
    if cat_type == 'lessons':
        for item in items:
            if isinstance(item, dict):
                sec = item.get('section', 'شروحات عامة') or 'شروحات عامة'
                if sec not in grouped_lessons:
                    grouped_lessons[sec] = []
                grouped_lessons[sec].append(item)

    context = {
        'title': f"{cat_title} - {track_title}",
        'items': items,
        'books': items if cat_type == 'books' else [],
        'summaries': items if cat_type == 'summaries' else [],
        'evaluations': items if cat_type == 'evaluations' else [],
        'grouped_lessons': grouped_lessons,
        'back_url': url_for('specialized_tracks', cat_type=cat_type)
    }
    return render_template(template_name, **context)

# مسارات متوافقة تلقائياً
@app.route('/books')
def books():
    return redirect(url_for('select_type', cat_type='books'))

@app.route('/summaries')
def summaries():
    return redirect(url_for('select_type', cat_type='summaries'))

@app.route('/evaluations')
def evaluations():
    return redirect(url_for('select_type', cat_type='evaluations'))

@app.route('/platforms')
def platforms():
    if 'user' not in session:
        return redirect(url_for('login'))
    data = load_data()
    return render_template('platforms.html', platforms=data.get('platforms', []))

@app.route('/tracks')
def tracks():
    return redirect(url_for('select_type', cat_type='lessons'))

@app.route('/lessons/<track_id>')
def lessons(track_id):
    return redirect(url_for('specialized_items', cat_type='lessons', track_id=track_id))

# --- مسار المنتدى والملاحظات ---

@app.route('/forum', methods=['GET', 'POST'])
def forum():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    data = load_data()
    if 'forum' not in data or not isinstance(data['forum'], list):
        data['forum'] = []

    if request.method == 'POST':
        question = request.form.get('question', '').strip()
        if question:
            data['forum'].append({
                'user': session.get('user', 'طالب'),
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
    user_key = str(session.get('user'))
    
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
        sub_type = request.form.get('subject_type', 'general')
        gen_sub = request.form.get('general_subject')
        track = request.form.get('track')
        section = request.form.get('section', '').strip() or 'شروحات عامة'

        if category == 'platform':
            data.setdefault('platforms', []).append({'title': title, 'link': link})
        else:
            item_data = {'title': title, 'link': link}
            if category == 'lesson':
                item_data['section'] = section
                
            cat_key = 'summaries' if category == 'summary' else category + 's'
            if sub_type == 'general' and gen_sub:
                data.setdefault('general_items', {}).setdefault(cat_key, {}).setdefault(gen_sub, []).append(item_data)
            elif sub_type == 'specialized' and track:
                data.setdefault('specialized_items', {}).setdefault(cat_key, {}).setdefault(track, []).append(item_data)
                if category == 'lesson':
                    data.setdefault('lessons', {}).setdefault(track, []).append(item_data)

        save_data(data)
        return redirect(url_for('admin'))

    users = data.get('users', [])
    total_users = len(users)

    return render_template('admin.html', tracks=TRACKS, general_subjects=GENERAL_SUBJECTS, data=data, users=users, total_users=total_users, forum=data.get('forum', []))

@app.route('/admin/reply_forum/<int:index>', methods=['POST'])
def reply_forum(index):
    if not session.get('logged_in'):
        return redirect(url_for('admin'))

    reply_text = request.form.get('reply', '').strip()
    data = load_data()
    if 'forum' in data and isinstance(data['forum'], list) and len(data['forum']) > index:
        data['forum'][index]['reply'] = reply_text
        save_data(data)
    return redirect(url_for('admin'))

@app.route('/admin/delete/<cat_type>/<int:index>', methods=['POST'])
def delete_item(cat_type, index):
    if not session.get('logged_in'):
        return redirect(url_for('admin'))

    data = load_data()
    mapping = {
        'book': 'books',
        'summary': 'summaries',
        'evaluation': 'evaluations',
        'platform': 'platforms'
    }
    
    if cat_type in mapping:
        key = mapping[cat_type]
        if key in data and isinstance(data[key], list) and len(data[key]) > index:
            data[key].pop(index)
            save_data(data)
    elif cat_type.startswith('lesson_'):
        track_key = cat_type.replace('lesson_', '')
        if 'lessons' in data and track_key in data['lessons']:
            if len(data['lessons'][track_key]) > index:
                data['lessons'][track_key].pop(index)
                save_data(data)
    elif cat_type == 'forum':
        if 'forum' in data and isinstance(data['forum'], list) and len(data['forum']) > index:
            data['forum'].pop(index)
            save_data(data)

    return redirect(url_for('admin'))

if __name__ == '__main__':
    app.run(debug=True)
