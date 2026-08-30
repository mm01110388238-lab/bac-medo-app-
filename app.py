from flask import Flask, render_template_string, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = "medo_secret_key_bac"  # مفتاح أمان الجلسة

# كلمة سر لوحة التحكم
ADMIN_PASSWORD = "admin"

# قاعدة البيانات المؤقتة
data_store = {
    "books": [{"id": 1, "title": "مذكرة الفيزياء - الفصل الأول", "link": "https://example.com/physics.pdf"}],
    "platforms": [{"id": 1, "name": "منصة مصر التعليمية", "link": "https://moe.gov.eg"}],
    "videos": [{"id": 1, "title": "مراجعة شاملة للرياضيات", "link": "https://youtube.com"}],
    "news": [{"id": 1, "text": "مرحباً بكم في منصة البكالوريا مع ميدو الرسمية!"}]
}

# ----------------- واجهة الطالب -----------------
STUDENT_HTML = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>البكالوريا مع ميدو</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        body { background-color: #0f172a; color: #f8fafc; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        .hero { background: linear-gradient(135deg, #1e293b, #0f172a); border-bottom: 2px solid #38bdf8; padding: 40px 20px; text-align: center; }
        .card-custom { background-color: #1e293b; border: 1px solid #334155; border-radius: 16px; color: #fff; transition: 0.3s; }
        .card-custom:hover { transform: translateY(-4px); border-color: #38bdf8; }
        .btn-link-custom { background-color: #38bdf8; color: #0f172a; font-weight: bold; border-radius: 8px; text-decoration: none; display: inline-block; padding: 8px 16px; width: 100%; text-align: center; }
        .btn-link-custom:hover { background-color: #7dd3fc; color: #0f172a; }
        .news-ticker { background: #0284c7; color: white; padding: 10px; border-radius: 8px; font-weight: 500; }
    </style>
</head>
<body>

<div class="hero">
    <h1 class="fw-bold text-info"><i class="fa-solid fa-graduation-cap"></i> البكالوريا مع ميدو</h1>
    <p class="text-light">منصتك التعليمية المتكاملة للكتب والمنصات والشروحات</p>
</div>

<div class="container my-4">
    <!-- الشريط الإخباري -->
    {% if data.news %}
    <div class="news-ticker mb-4">
        📢 <strong>آخر الأخبار:</strong> {{ data.news[-1].text }}
    </div>
    {% endif %}

    <div class="row g-4">
        <!-- قسم الكتب والمذكرات -->
        <div class="col-md-4">
            <div class="card card-custom p-3 h-100">
                <h4 class="text-info"><i class="fa-solid fa-book"></i> الكتب والمذكرات</h4>
                <hr class="border-secondary">
                {% for item in data.books %}
                <div class="mb-3 p-2 border border-secondary rounded">
                    <h6>{{ item.title }}</h6>
                    <a href="{{ item.link }}" target="_blank" class="btn-link-custom mt-2"><i class="fa-solid fa-download"></i> فتح / تحميل</a>
                </div>
                {% endfor %}
            </div>
        </div>

        <!-- قسم المنصات التعليمية -->
        <div class="col-md-4">
            <div class="card card-custom p-3 h-100">
                <h4 class="text-warning"><i class="fa-solid fa-globe"></i> المنصات التعليمية</h4>
                <hr class="border-secondary">
                {% for item in data.platforms %}
                <div class="mb-3 p-2 border border-secondary rounded">
                    <h6>{{ item.name }}</h6>
                    <a href="{{ item.link }}" target="_blank" class="btn-link-custom mt-2"><i class="fa-solid fa-arrow-up-right-from-square"></i> الانتقال للمنصة</a>
                </div>
                {% endfor %}
            </div>
        </div>

        <!-- قسم الفيديوهات والشروحات -->
        <div class="col-md-4">
            <div class="card card-custom p-3 h-100">
                <h4 class="text-danger"><i class="fa-solid fa-video"></i> الشروحات والمراجعات</h4>
                <hr class="border-secondary">
                {% for item in data.videos %}
                <div class="mb-3 p-2 border border-secondary rounded">
                    <h6>{{ item.title }}</h6>
                    <a href="{{ item.link }}" target="_blank" class="btn-link-custom mt-2"><i class="fa-brands fa-youtube"></i> مشاهدة الشرح</a>
                </div>
                {% endfor %}
            </div>
        </div>
    </div>
</div>

</body>
</html>
"""

# ----------------- لوحة التحكم للأدمن -----------------
ADMIN_HTML = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>لوحة تحكم الأدمن - البكالوريا مع ميدو</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
</head>
<body class="bg-light p-4">
<div class="container">
    <div class="d-flex justify-content-between align-items-center mb-4">
        <h2>⚙️ لوحة تحكم المنصة (الأدمن)</h2>
        <a href="/" class="btn btn-secondary">العودة للمنصة</a>
    </div>

    <!-- إضافة عنصر جديد -->
    <div class="card p-4 mb-4 shadow-sm">
        <h4>إضافة محتوى جديد</h4>
        <form method="POST" action="/admin/add">
            <div class="row g-3">
                <div class="col-md-3">
                    <label class="form-label">القسم</label>
                    <select name="category" class="form-select" required>
                        <option value="books">الكتب والمذكرات</option>
                        <option value="platforms">المنصات التعليمية</option>
                        <option value="videos">الفيديوهات</option>
                        <option value="news">خبر جديد</option>
                    </select>
                </div>
                <div class="col-md-4">
                    <label class="form-label">العنوان / الاسم</label>
                    <input type="text" name="title" class="form-control" placeholder="أدخل العنوان" required>
                </div>
                <div class="col-md-5">
                    <label class="form-label">الرابط (ليس مطلوباً للأخبار)</label>
                    <input type="text" name="link" class="form-control" placeholder="https://...">
                </div>
            </div>
            <button type="submit" class="btn btn-primary mt-3">إضافة للمنصة</button>
        </form>
    </div>

    <!-- إدارة الحذف -->
    <div class="card p-4 shadow-sm">
        <h4>المحتوى الحالي (إمكانية الحذف)</h4>
        
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
