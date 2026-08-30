from flask import Flask, render_template_string, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'bac_medo_secret_key_2026'

# قاعدة بيانات مؤقتة للمحتوى
data = {
    'books': [],      # الكتب والمذكرات: {'title': '', 'link': ''}
    'platforms': [],  # المنصات التعليمية: {'title': '', 'link': ''}
    'lessons': {      # الشروحات والمراجعات مقسمة حسب الـ 8 خيارات
        'med_math': [],
        'med_physics': [],
        'eng_chem': [],
        'eng_prog': [],
        'biz_acct': [],
        'biz_mgmt': [],
        'art_psych': [],
        'art_lang': []
    }
}

TRACK_NAMES = {
    'med_math': 'مسار الطب وعلوم الحياة / رياضيات',
    'med_physics': 'مسار الطب وعلوم الحياة / فيزياء',
    'eng_chem': 'مسار الهندسة وعلوم الحاسب / كيمياء',
    'eng_prog': 'مسار الهندسة وعلوم الحاسب / برمجة',
    'biz_acct': 'مسار الأعمال / محاسبة',
    'biz_mgmt': 'مسار الأعمال / إدارة أعمال',
    'art_psych': 'مسار الآداب والفنون / علم نفس',
    'art_lang': 'مسار الآداب والفنون / لغة أجنبية ثانية'
}

BASE_HTML = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>البكالوريا مع ميدو</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #0f172a; color: #f8fafc; margin: 0; padding: 20px; text-align: center; }
        .container { max-width: 800px; margin: 0 auto; background: #1e293b; padding: 25px; border-radius: 15px; box-shadow: 0 10px 25px rgba(0,0,0,0.3); }
        h1 { color: #38bdf8; margin-bottom: 25px; font-size: 28px; }
        .btn { display: block; width: 90%; margin: 15px auto; padding: 16px; background-color: #2563eb; color: white; text-decoration: none; border-radius: 10px; font-size: 18px; font-weight: bold; transition: 0.3s; border: none; cursor: pointer; }
        .btn:hover { background-color: #1d4ed8; transform: translateY(-2px); }
        .btn-track { background-color: #0d9488; }
        .btn-track:hover { background-color: #0f766e; }
        .btn-item { background-color: #334155; text-align: right; padding: 12px 20px; margin: 10px auto; border-right: 5px solid #38bdf8; }
        .btn-item:hover { background-color: #475569; }
        .btn-back { background-color: #64748b; width: auto; display: inline-block; padding: 8px 20px; font-size: 14px; margin-top: 20px; }
        .admin-form { text-align: right; background: #0f172a; padding: 20px; border-radius: 10px; margin-top: 20px; }
        input, select { width: 100%; padding: 10px; margin: 8px 0 18px 0; border-radius: 5px; border: 1px solid #475569; background: #1e293b; color: white; box-sizing: border-box; }
    </style>
</head>
<body>
    <div class="container">
        {% block content %}{% endblock %}
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    html = BASE_HTML + """
    {% block content %}
        <h1>🎓 البكالوريا مع ميدو</h1>
        <p style="color: #94a3b8; margin-bottom: 30px;">اختر القسم المطلوب للوصول للمحتوى التعليمي</p>
        
        <a href="/books" class="btn">📚 الكتب والمذكرات</a>
        <a href="/platforms" class="btn">🌐 المنصات التعليمية</a>
        <a href="/tracks" class="btn">📺 الشروحات والمراجعات</a>
    {% endblock %}
    """
    return render_template_string(html)

@app.route('/books')
def books():
    html = BASE_HTML + """
    {% block content %}
        <h1>📚 الكتب والمذكرات</h1>
        {% if books %}
            {% for b in books %}
                <a href="{{ b.link }}" target="_blank" class="btn btn-item">📖 {{ b.title }} (فتح PDF)</a>
            {% endfor %}
        {% else %}
            <p style="color: #94a3b8;">لا توجد كتب مضافة حالياً.</p>
        {% endif %}
        <a href="/" class="btn btn-back">⬅ العودة للرئيسية</a>
    {% endblock %}
    """
    return render_template_string(html, books=data['books'])

@app.route('/platforms')
def platforms():
    html = BASE_HTML + """
    {% block content %}
        <h1>🌐 المنصات التعليمية</h1>
        {% if platforms %}
            {% for p in platforms %}
                <a href="{{ p.link }}" target="_blank" class="btn btn-item">🚀 {{ p.title }}</a>
            {% endfor %}
        {% else %}
            <p style="color: #94a3b8;">لا توجد منصات مضافة حالياً.</p>
        {% endif %}
        <a href="/" class="btn btn-back">⬅ العودة للرئيسية</a>
    {% endblock %}
    """
    return render_template_string(html, platforms=data['platforms'])

@app.route('/tracks')
def tracks():
    html = BASE_HTML + """
    {% block content %}
        <h1>📺 اختر المسار والتخصص</h1>
        {% for key, name in tracks.items() %}
            <a href="/lessons/{{ key }}" class="btn btn-track">{{ name }}</a>
        {% endfor %}
        <a href="/" class="btn btn-back">⬅ العودة للرئيسية</a>
    {% endblock %}
    """
    return render_template_string(html, tracks=TRACK_NAMES)

@app.route('/lessons/<track_id>')
def lessons(track_id):
    track_title = TRACK_NAMES.get(track_id, 'الشروحات')
    items = data['lessons'].get(track_id, [])
    html = BASE_HTML + """
    {% block content %}
        <h1>{{ title }}</h1>
        {% if items %}
            {% for item in items %}
                <a href="{{ item.link }}" target="_blank" class="btn btn-item">▶ {{ item.title }}</a>
            {% endfor %}
        {% else %}
            <p style="color: #94a3b8;">لا توجد شروحات مضافة لهذا المسار حالياً.</p>
        {% endif %}
        <a href="/tracks" class="btn btn-back">⬅ اختيار مسار آخر</a>
    {% endblock %}
    """
    return render_template_string(html, title=track_title, items=items)

# --- لوحة التحكم (الأدمن) ---

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        category = request.form.get('category')
        title = request.form.get('title')
        link = request.form.get('link')
        track = request.form.get('track')

        if category == 'book':
            data['books'].append({'title': title, 'link': link})
        elif category == 'platform':
            data['platforms'].append({'title': title, 'link': link})
        elif category == 'lesson':
            if track in data['lessons']:
                data['lessons'][track].append({'title': title, 'link': link})

        return redirect(url_for('admin'))

    html = BASE_HTML + """
    {% block content %}
        <h1>⚙️ لوحة تحكم الأدمن</h1>
        <p style="color: #4ade80;">أضف محتوى جديد للمنصة بسهولة</p>

        <form method="POST" class="admin-form">
            <label>اختر قسم المحتوى:</label>
            <select name="category" id="category" onchange="toggleTrackSelect()">
                <option value="book">📚 كتاب / مذكرة (PDF)</option>
                <option value="platform">🌐 منصة تعليمية</option>
                <option value="lesson">📺 شرح / مراجعة (حسب التخصص)</option>
            </select>

            <div id="track-div" style="display: none;">
                <label>اختر المسار والتخصص:</label>
                <select name="track">
                    {% for key, name in tracks.items() %}
                        <option value="{{ key }}">{{ name }}</option>
                    {% endfor %}
                </select>
            </div>

            <label>العنوان / الاسم:</label>
            <input type="text" name="title" placeholder="مثال: ملخص الفيزياء الفصل الأول" required>

            <label>الرابط المباشر (PDF / فيديو / موقع):</label>
            <input type="url" name="link" placeholder="https://..." required>

            <button type="submit" class="btn" style="background-color: #16a34a; width: 100%;">➕ إضافة المحتوى</button>
        </form>

        <a href="/" class="btn btn-back">🏠 العودة للموقع الرئيسي</a>

        <script>
            function toggleTrackSelect() {
                var cat = document.getElementById('category').value;
                var trackDiv = document.getElementById('track-div');
                trackDiv.style.display = (cat === 'lesson') ? 'block' : 'none';
            }
        </script>
    {% endblock %}
    """
    return render_template_string(html, tracks=TRACK_NAMES)

if __name__ == '__main__':
    app.run(debug=True)
        
        <h5 class="mt-3 text-primary">الكتب:</h5>
        <ul class="list-group mb-3">
            {% for b in data.books %}
            <li class="list-group-item d-flex justify-content-between align-items-center">
                {{ b.title }}
                <a href="/admin/delete/books/{{ b.id }}" class="btn btn-danger btn-sm">حذف</a>
            </li>
            {% endfor %}
        </ul>

        <h5 class="text-warning">المنصات:</h5>
        <ul class="list-group mb-3">
            {% for p in data.platforms %}
            <li class="list-group-item d-flex justify-content-between align-items-center">
                {{ p.name }}
                <a href="/admin/delete/platforms/{{ p.id }}" class="btn btn-danger btn-sm">حذف</a>
            </li>
            {% endfor %}
        </ul>

        <h5 class="text-danger">الفيديوهات:</h5>
        <ul class="list-group mb-3">
            {% for v in data.videos %}
            <li class="list-group-item d-flex justify-content-between align-items-center">
                {{ v.title }}
                <a href="/admin/delete/videos/{{ v.id }}" class="btn btn-danger btn-sm">حذف</a>
            </li>
            {% endfor %}
        </ul>
    </div>
</div>
</body>
</html>
"""

# ----------------- المسارات (Routes) -----------------
@app.route('/')
def home():
    return render_template_string(STUDENT_HTML, data=data_store)

@app.route('/admin')
def admin_panel():
    return render_template_string(ADMIN_HTML, data=data_store)

@app.route('/admin/add', methods=['POST'])
def add_item():
    category = request.form.get('category')
    title = request.form.get('title')
    link = request.form.get('link')
    
    new_id = len(data_store[category]) + 1
    if category == "news":
        data_store["news"].append({"id": new_id, "text": title})
    elif category == "platforms":
        data_store["platforms"].append({"id": new_id, "name": title, "link": link})
    else:
        data_store[category].append({"id": new_id, "title": title, "link": link})
        
    return redirect(url_for('admin_panel'))

@app.route('/admin/delete/<category>/<int:item_id>')
def delete_item(category, item_id):
    if category in data_store:
        data_store[category] = [i for i in data_store[category] if i['id'] != item_id]
    return redirect(url_for('admin_panel'))

if __name__ == '__main__':
    app.run(debug=True)
