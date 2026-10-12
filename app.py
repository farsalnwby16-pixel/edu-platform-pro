import os
import uuid
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'lingo_go_super_secret_key_2026'

db_url = 'postgresql+psycopg2://neondb_owner:npg_ZECSXyova0b9@ep-fragrant-firefly-zaojv26y-pooler.c-2.eu-west-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require'

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), default='student')
    full_name = db.Column(db.String(120), default='')

class Lesson(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    level = db.Column(db.String(10), nullable=False)

class LessonProgress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    lesson_id = db.Column(db.Integer, nullable=False)
    completed = db.Column(db.Boolean, default=True)

class Certificate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cert_code = db.Column(db.String(50), unique=True, nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    student_name = db.Column(db.String(120), nullable=False)
    issue_date = db.Column(db.String(50), nullable=False)
    level_achieved = db.Column(db.String(50), default='جميع المستويات (A1 - C2)')

with app.app_context():
    db.create_all()
    if Lesson.query.count() == 0:
        default_lessons = [
            # Lessons
            Lesson(title="1. Introduction to English Basics", url="https://www.youtube.com/embed/kJQP7kiw5Fk", category="Lessons", level="A1"),
            Lesson(title="2. Simple Sentence Structure", url="https://www.youtube.com/embed/zSWdZVtXT7E", category="Lessons", level="A2"),
            Lesson(title="1. Intermediate Grammar & Tenses", url="https://www.youtube.com/embed/X5P5655gghY", category="Lessons", level="B1"),
            Lesson(title="2. Complex Sentence Patterns", url="https://www.youtube.com/embed/w7vK_u5Zg_o", category="Lessons", level="B2"),
            Lesson(title="1. Advanced Grammar Structures", url="https://www.youtube.com/embed/8X2k_ic0PP4", category="Lessons", level="C1"),
            Lesson(title="1. Mastery of Idiomatic Expressions", url="https://www.youtube.com/embed/5qap5aO4i9A", category="Lessons", level="C2"),
            
            # Listening
            Lesson(title="1. Daily English Listening Practice", url="https://www.youtube.com/embed/w7vK_u5Zg_o", category="Listening", level="A1"),
            Lesson(title="2. Everyday Conversations", url="https://www.youtube.com/embed/kJQP7kiw5Fk", category="Listening", level="A2"),
            Lesson(title="1. Intermediate Audio Clips", url="https://www.youtube.com/embed/zSWdZVtXT7E", category="Listening", level="B1"),
            Lesson(title="1. News & Talk Shows Listening", url="https://www.youtube.com/embed/8X2k_ic0PP4", category="Listening", level="B2"),
            Lesson(title="1. Academic Lectures Listening", url="https://www.youtube.com/embed/5qap5aO4i9A", category="Listening", level="C1"),
            Lesson(title="1. Advanced Native Speed Listening", url="https://www.youtube.com/embed/R8_Zs5s21c4", category="Listening", level="C2"),
            
            # Accent
            Lesson(title="1. American Accent Foundations", url="https://www.youtube.com/embed/hS03xMvQ_Zs", category="Accent", level="A1"),
            Lesson(title="2. Vowels and Consonants Sound", url="https://www.youtube.com/embed/kJQP7kiw5Fk", category="Accent", level="A2"),
            Lesson(title="1. Intonation & Stress Patterns", url="https://www.youtube.com/embed/zSWdZVtXT7E", category="Accent", level="B1"),
            Lesson(title="1. Connected Speech & Linking", url="https://www.youtube.com/embed/w7vK_u5Zg_o", category="Accent", level="B2"),
            Lesson(title="1. Advanced Accent Refinement", url="https://www.youtube.com/embed/8X2k_ic0PP4", category="Accent", level="C1"),
            Lesson(title="1. Native Pronunciation & Reductions", url="https://www.youtube.com/embed/V9vjXg6w3x0", category="Accent", level="C2"),

            # Shadowing
            Lesson(title="1. Basic Shadowing Technique", url="https://www.youtube.com/embed/X5P5655gghY", category="Shadowing", level="A1"),
            Lesson(title="2. Short Sentences Shadowing", url="https://www.youtube.com/embed/kJQP7kiw5Fk", category="Shadowing", level="A2"),
            Lesson(title="1. Medium Pace Shadowing", url="https://www.youtube.com/embed/zSWdZVtXT7E", category="Shadowing", level="B1"),
            Lesson(title="1. Fluent Speech Shadowing", url="https://www.youtube.com/embed/w7vK_u5Zg_o", category="Shadowing", level="B2"),
            Lesson(title="1. Advanced Speed Shadowing", url="https://www.youtube.com/embed/8X2k_ic0PP4", category="Shadowing", level="C1"),
            Lesson(title="1. Expert Speed Shadowing Practice", url="https://www.youtube.com/embed/5qap5aO4i9A", category="Shadowing", level="C2"),

            # Podcast
            Lesson(title="1. English Podcast for Beginners", url="https://www.youtube.com/embed/w7vK_u5Zg_o", category="Podcast", level="A1"),
            Lesson(title="2. Casual Daily Chats Podcast", url="https://www.youtube.com/embed/kJQP7kiw5Fk", category="Podcast", level="A2"),
            Lesson(title="1. Intermediate Storytelling Podcast", url="https://www.youtube.com/embed/zSWdZVtXT7E", category="Podcast", level="B1"),
            Lesson(title="1. Culture & Society Discussion", url="https://www.youtube.com/embed/w7vK_u5Zg_o", category="Podcast", level="B2"),
            Lesson(title="1. Expert Insights Podcast", url="https://www.youtube.com/embed/8X2k_ic0PP4", category="Podcast", level="C1"),
            Lesson(title="1. C2 Advanced Philosophical English Podcast", url="https://www.youtube.com/embed/8X2k_ic0PP4", category="Podcast", level="C2"),
            Lesson(title="2. C2 Business & Academic Deep Talk", url="https://www.youtube.com/embed/R8_Zs5s21c4", category="Podcast", level="C2"),

            # Stories (القصص التفاعلية)
            Lesson(title="1. Easy Interactive Story: The Lost Key", url="https://www.youtube.com/embed/kJQP7kiw5Fk", category="Stories", level="A1"),
            Lesson(title="2. A Walk in the Park Story", url="https://www.youtube.com/embed/zSWdZVtXT7E", category="Stories", level="A2"),
            Lesson(title="1. The Mystery Box Story", url="https://www.youtube.com/embed/X5P5655gghY", category="Stories", level="B1"),
            Lesson(title="1. Journey to the Mountains", url="https://www.youtube.com/embed/w7vK_u5Zg_o", category="Stories", level="B2"),
            Lesson(title="1. Classic Fiction Adaptation", url="https://www.youtube.com/embed/8X2k_ic0PP4", category="Stories", level="C1"),
            Lesson(title="1. Advanced C2 Literary Story Analysis", url="https://www.youtube.com/embed/8X2k_ic0PP4", category="Stories", level="C2")
        ]
        db.session.bulk_save_objects(default_lessons)
        db.session.commit()

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    cat = request.args.get('cat', 'Lessons')
    level = request.args.get('level', 'A1')

    lessons_raw = Lesson.query.filter_by(category=cat, level=level).order_by(Lesson.id.asc()).all()
    lessons = [{'id': l.id, 'title': l.title, 'url': l.url, 'category': l.category, 'level': l.level} for l in lessons_raw]
    
    completed_lessons = [p.lesson_id for p in LessonProgress.query.filter_by(user_id=session.get('user_id')).all()] if 'user_id' in session else []

    total_lessons = Lesson.query.count()
    completed_count = len(completed_lessons)
    progress_pct = int((completed_count / total_lessons * 100)) if total_lessons > 0 else 0
    if progress_pct > 100: progress_pct = 100

    user_data = User.query.get(session['user_id'])
    student_name = user_data.full_name if user_data and user_data.full_name else session['username']

    return render_template('index.html', 
                           completed_lessons=completed_lessons,
                           lessons=lessons,
                           progress_pct=progress_pct,
                           current_cat=cat,
                           current_level=level,
                           student_name=student_name)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            return redirect(url_for('admin') if user.role == 'admin' else url_for('index'))
        else:
            flash('اسم المستخدم أو كلمة المرور غير صحيحة')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        full_name = request.form.get('full_name', '').strip()

        if User.query.filter_by(username=username).first():
            flash('اسم المستخدم مستخدم بالفعل')
        else:
            new_user = User(username=username, password=password, role='student', full_name=full_name)
            db.session.add(new_user)
            db.session.commit()
            flash('تم إنشاء الحساب وحفظه بنجاح، يمكنك تسجيل الدخول الآن')
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/complete_lesson', methods=['POST'])
def complete_lesson():
    if 'user_id' not in session:
        return jsonify({'status': 'error'}), 401
    lesson_id = request.form.get('lesson_id')
    user_id = session['user_id']
    if lesson_id:
        p = LessonProgress.query.filter_by(user_id=user_id, lesson_id=int(lesson_id)).first()
        if not p:
            p = LessonProgress(user_id=user_id, lesson_id=int(lesson_id), completed=True)
            db.session.add(p)
        else:
            p.completed = True
        db.session.commit()
        return jsonify({'status': 'ok'})
    return jsonify({'status': 'invalid'})

@app.route('/update_student_name', methods=['POST'])
def update_student_name():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    new_name = request.form.get('full_name', '').strip()
    if new_name:
        user = User.query.get(session['user_id'])
        if user:
            user.full_name = new_name
            db.session.commit()
    return redirect(url_for('index'))

@app.route('/certificate')
def certificate():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    u = User.query.get(session['user_id'])
    student_name = u.full_name if u and u.full_name else u.username

    cert = Certificate.query.filter_by(user_id=u.id).first()
    if not cert:
        cert_code = f"CERT-{uuid.uuid4().hex[:8].upper()}"
        issue_date = datetime.now().strftime("%B %d, %Y")
        cert = Certificate(
            cert_code=cert_code,
            user_id=u.id,
            student_name=student_name,
            issue_date=issue_date,
            level_achieved='جميع المستويات (A1 - C2)'
        )
        db.session.add(cert)
        db.session.commit()
    else:
        cert.student_name = student_name
        db.session.commit()

    return render_template('certificate.html', student_name=cert.student_name, cert_id=cert.cert_code, issue_date=cert.issue_date)

@app.route('/admin')
def admin():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))
    return render_template('admin.html')

@app.route('/admin/add_lesson', methods=['POST'])
def admin_add_lesson():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))
    category = request.form.get('category', 'Lessons')
    level = request.form.get('level', 'A1')
    title = request.form.get('title', '').strip()
    url = request.form.get('url', '').strip()

    if 'watch?v=' in url:
        v_id = url.split('watch?v=')[1].split('&')[0]
        url = f"https://www.youtube.com/embed/{v_id}"
    elif 'youtu.be/' in url:
        v_id = url.split('youtu.be/')[1].split('?')[0]
        url = f"https://www.youtube.com/embed/{v_id}"

    new_lesson = Lesson(title=title, url=url, category=category, level=level)
    db.session.add(new_lesson)
    db.session.commit()
    flash('تمت إضافة الدرس وحفظه في القاعدة الدائمة بنجاح')
    return redirect(url_for('admin'))

@app.route('/admin/preview_certificate', methods=['POST'])
def admin_preview_certificate():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))
    student_name = request.form.get('preview_name', 'Student Name').strip()
    if not student_name:
        student_name = 'Student Name'

    cert_code = f"CERT-ADM-{uuid.uuid4().hex[:6].upper()}"
    issue_date = datetime.now().strftime("%B %d, %Y")

    cert = Certificate(
        cert_code=cert_code,
        user_id=session['user_id'],
        student_name=student_name,
        issue_date=issue_date,
        level_achieved='جميع المستويات (A1 - C2)'
    )
    db.session.add(cert)
    db.session.commit()

    return render_template('certificate.html', student_name=cert.student_name, cert_id=cert.cert_code, issue_date=cert.issue_date)

@app.route('/verify/<cert_id>')
def verify_certificate(cert_id):
    cert = Certificate.query.filter_by(cert_code=cert_id.strip()).first()
    if cert:
        return f"""
        <!DOCTYPE html>
        <html lang="ar" dir="rtl">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>التحقق من صحة الشهادة - Lingo Go Academy</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
            <style>
                body {{ background: #0b0f19; color: #e2e8f0; font-family: Tahoma, sans-serif; min-height: 100vh; display: flex; align-items: center; justify-content: center; padding: 20px; }}
                .verify-card {{ background: rgba(22, 31, 48, 0.95); border: 1px solid #10b981; border-radius: 20px; box-shadow: 0 15px 35px rgba(0,0,0,0.6); max-width: 550px; width: 100%; padding: 35px; text-align: center; }}
                .badge-status {{ display: inline-flex; align-items: center; gap: 8px; background: rgba(16, 185, 129, 0.15); color: #10b981; border: 1px solid rgba(16, 185, 129, 0.3); padding: 8px 18px; border-radius: 30px; font-weight: 600; margin-bottom: 20px; }}
                .info-group {{ background: rgba(15, 23, 42, 0.8); border-radius: 10px; padding: 12px 16px; margin-bottom: 10px; text-align: right; display: flex; justify-content: space-between; }}
            </style>
        </head>
        <body>
            <div class="verify-card">
                <div style="font-size: 3.5rem; color: #10b981; margin-bottom: 15px;"><i class="fas fa-certificate"></i></div>
                <div class="badge-status"><i class="fas fa-check-circle"></i> شهادة موثقة ورسمية ودائمة</div>
                <h3 style="color: #fff; margin-bottom: 20px;">Lingo Go International Academy</h3>
                <div class="info-group">
                    <span style="color: #94a3b8;">اسم الطالب:</span>
                    <span style="color: #fff; font-weight: bold;">{cert.student_name}</span>
                </div>
                <div class="info-group">
                    <span style="color: #94a3b8;">كود التوثيق (ID):</span>
                    <span style="color: #3b82f6; font-family: monospace; font-weight: bold;">{cert.cert_code}</span>
                </div>
                <div class="info-group">
                    <span style="color: #94a3b8;">تاريخ الإصدار:</span>
                    <span style="color: #fff;">{cert.issue_date}</span>
                </div>
                <div class="info-group">
                    <span style="color: #94a3b8;">المستوى:</span>
                    <span style="color: #10b981; font-weight: bold;">{cert.level_achieved}</span>
                </div>
                <div class="info-group">
                    <span style="color: #94a3b8;">حالة السجل:</span>
                    <span style="color: #10b981; font-weight: bold;">محفوظ بشكل دائم في قاعدة البيانات</span>
                </div>
            </div>
        </body>
        </html>
        """
    else:
        return f"""
        <!DOCTYPE html>
        <html lang="ar" dir="rtl">
        <head>
            <meta charset="UTF-8">
            <title>خطأ في التوثيق</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
            <style>
                body {{ background: #0b0f19; color: #fff; display: flex; align-items: center; justify-content: center; height: 100vh; font-family: Tahoma, sans-serif; }}
                .card-box {{ background: #161f30; padding: 40px; border-radius: 15px; border: 2px solid #ef4444; text-align: center; max-width: 500px; width: 100%; }}
            </style>
        </head>
        <body>
            <div class="card-box">
                <h2 style="color: #ef4444; margin-bottom: 20px;">❌ شهادة غير صالحة أو غير مسجلة</h2>
                <p style="color: #94a3b8;">كود التوثيق ({cert_id}) غير موجود في سجلات قاعدة البيانات الدائمة.</p>
            </div>
        </body>
        </html>
        """

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
