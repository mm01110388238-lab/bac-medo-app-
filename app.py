import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "Medo#Secur3_Bac2026"

ADMIN_PASSWORD = "Medo#Secur3_Bac2026"

# إعداد قاعدة البيانات لحفظ الحسابات
def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            identifier TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# الصفحة الرئيسية للمنصة
@app.route('/')
def home():
    # التحقق مما إذا كان المستخدم مسجلاً للدخول أم لا
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('index.html', user=session['user'])

# صفحة التسجيل وإنشاء حساب جديد
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        identifier = request.form.get('identifier') # جيميل أو رقم الهاتف
        password = request.form.get('password')
        
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO users (identifier, password) VALUES (?, ?)', (identifier, password))
            conn.commit()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            return "الحساب مسجل من قبل بالفعل! <a href='/login'>سجل دخولك</a>"
        finally:
            conn.close()
            
    return render_template('register.html')

# صفحة تسجيل الدخول
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        identifier = request.form.get('identifier')
        password = request.form.get('password')
        
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE identifier = ? AND password = ?', (identifier, password))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            session['user'] = identifier
            return redirect(url_for('home'))
        else:
            return "بيانات الدخول غير صحيحة! <a href='/login'>حاول مرة أخرى</a>"
            
    return render_template('login.html')

# لوحة التحكم الخاصة بالأدمن (تعرض عدد المستخدمين وبياناتهم)
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        if request.form.get('password') == ADMIN_PASSWORD:
            session['is_admin'] = True
        else:
            return "كلمة سر الأدمن خاطئة!"
            
    if not session.get('is_admin'):
        return '''
            <div style="font-family: Tahoma; direction: rtl; padding: 20px; background: #121212; color: #fff; text-align: center;">
                <h2>تسجيل دخول الأدمن</h2>
                <form method="POST">
                    <input type="password" name="password" placeholder="أدخل كلمة سر الأدمن" style="padding: 10px; margin: 10px;">
                    <button type="submit" style="padding: 10px 20px; background: #00ffcc; border: none; cursor: pointer;">دخول</button>
                </form>
            </div>
        '''
    
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT identifier, password FROM users')
    users = cursor.fetchall()
    total_users = len(users)
    conn.close()
    
    users_html = "".join([f"<li><strong>{u[0]}</strong> - كلمة السر: <code>{u[1]}</code></li>" for u in users])
    return f'''
        <div style="font-family: Tahoma; direction: rtl; padding: 20px; background: #121212; color: #fff;">
            <h1>لوحة تحكم المنصة - سهلتها لك</h1>
            <p style="font-size: 20px; color: #00ffcc;">إجمالي عدد المستخدمين المسجلين: <strong>{total_users}</strong></p>
            <h3>قائمة الحسابات وكلمات السر:</h3>
            <ul>{users_html}</ul>
            <br><a href="/logout" style="color: #ff4d4d; text-decoration: none;">تسجيل خروج الأدمن</a>
        </div>
    '''

# تسجيل الخروج
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
