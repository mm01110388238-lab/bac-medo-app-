from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
app.secret_key = 'bac_medo_secret_key_2026'

# قاعدة بيانات مؤقتة للمحتوى
data = {
    'books': [],      # الكتب والمذكرات
    'platforms': [],  # المنصات التعليمية
    'lessons': {      # الشروحات والمراجعات
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

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/books')
def books():
    return render_template('books.html', books=data['books'])

@app.route('/platforms')
def platforms():
    return render_template('platforms.html', platforms=data['platforms'])

@app.route('/tracks')
def tracks():
    return render_template('tracks.html', tracks=TRACK_NAMES)

@app.route('/lessons/<track_id>')
def lessons(track_id):
    track_title = TRACK_NAMES.get(track_id, 'الشروحات')
    items = data['lessons'].get(track_id, [])
    return render_template('lessons.html', title=track_title, items=items)

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

    return render_template('admin.html', tracks=TRACK_NAMES)

if __name__ == '__main__':
    app.run(debug=True)
