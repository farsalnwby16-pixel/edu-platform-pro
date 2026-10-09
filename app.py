import os
import uuid
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
import yt_dlp

app = Flask(__name__)
app.secret_key = 'lingo_go_super_secret_key_2026'

db_url = os.environ.get('DATABASE_URL', 'sqlite:///lingo_go.db')
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql+pg8000://", 1)
elif db_url.startswith("postgresql+psycopg2://") and "+pg8000" not in db_url:
    db_url = db_url.replace("postgresql+psycopg2://", "postgresql+pg8000://", 1)

import os
db_url = os.environ.get('DATABASE_URL', 'postgresql+psycopg2://neondb_owner:npg_ZECSXyova0b9@ep-fragrant-firefly-zaojv26y-pooler.c-2.eu-west-2.aws.neon.tech/neondb?sslmode=require')
if db_url.startswith('postgres://'):
    db_url = db_url.replace('postgres://', 'postgresql+psycopg2://', 1)
elif db_url.startswith('Postgresql://'):
    db_url = db_url.replace('Postgresql://', 'postgresql+psycopg2://', 1)

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

class Progress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    lesson_id = db.Column(db.Integer, nullable=False)

class Certificate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cert_code = db.Column(db.String(50), unique=True, nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    student_name = db.Column(db.String(120), nullable=False)
    issue_date = db.Column(db.String(50), nullable=False)
    level_achieved = db.Column(db.String(50), default='جميع المستويات (A1 - C1)')

with app.app_context():
    # db.create_all()  # Disabled for Vercel
    admin_user = User.query.filter_by(username='farsalnwby16@gmail.com').first()
    if not admin_user:
        admin_user = User(username='farsalnwby16@gmail.com', password='farsalnwby16@gmail.com', role='admin', full_name='System Admin')
        db.session.add(admin_user)
    else:
        admin_user.password = 'farsalnwby16@gmail.com'
        admin_user.role = 'admin'
    db.session.commit()

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    cat = request.args.get('cat', 'Lessons')
    level = request.args.get('level', 'A1')
    
    lessons = Lesson.query.filter_by(category=cat, level=level).order_by(Lesson.id.asc()).all()
    
    completed_records = Progress.query.filter_by(user_id=session['user_id']).all()
    completed_ids = [int(p.lesson_id) for p in completed_records]
    
    total_lessons = Lesson.query.count()
    completed_count = len(completed_ids)
    progress_pct = int((completed_count / total_lessons * 100)) if total_lessons > 0 else 0
    
    user_data = User.query.get(session['user_id'])
    student_name = user_data.full_name if user_data and user_data.full_name else session['username']

    return render_template('index.html', 
                           lessons=lessons, 
                           completed_ids=completed_ids, 
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
            flash('تم إنشاء الحساب بنجاح، يمكنك تسجيل الدخول الآن')
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
    if lesson_id:
        existing = Progress.query.filter_by(user_id=session['user_id'], lesson_id=int(lesson_id)).first()
        if not existing:
            p = Progress(user_id=session['user_id'], lesson_id=int(lesson_id))
            db.session.add(p)
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
            level_achieved='جميع المستويات (A1 - C1)'
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
    flash('تمت إضافة الدرس بنجاح')
    return redirect(url_for('admin'))

@app.route('/admin/import_playlist', methods=['POST'])
def admin_import_playlist():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))
    category = request.form.get('category', 'Lessons')
    level = request.form.get('level', 'A1')
    playlist_url = request.form.get('playlist_url', '').strip()
    
    if playlist_url:
        ydl_opts = {'extract_flat': 'in_playlist', 'skip_download': True, 'quiet': True}
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(playlist_url, download=False)
                if 'entries' in info:
                    for entry in info['entries']:
                        if entry:
                            v_id = entry.get('id')
                            v_title = entry.get('title', 'Video Lesson')
                            if v_id:
                                embed_url = f"https://www.youtube.com/embed/{v_id}"
                                l = Lesson(title=v_title, url=embed_url, category=category, level=level)
                                db.session.add(l)
            db.session.commit()
            flash('تم استيراد قائمة التشغيل بنجاح')
        except Exception as e:
            flash(f'حدث خطأ أثناء الاستيراد: {e}')
            
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
    
    # حفظ الشهادة الصادرة من الأدمن في قاعدة البيانات فوراً
    cert = Certificate(
        cert_code=cert_code,
        user_id=session['user_id'],
        student_name=student_name,
        issue_date=issue_date,
        level_achieved='جميع المستويات (A1 - C1)'
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
                body {{ background: #0b0f19; color: #e2e8f0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; min-height: 100vh; display: flex; align-items: center; justify-content: center; padding: 20px; }}
                .verify-card {{ background: rgba(22, 31, 48, 0.9); border: 1px solid rgba(255, 255, 255, 0.12); border-radius: 20px; box-shadow: 0 15px 35px rgba(0,0,0,0.6); backdrop-filter: blur(12px); max-width: 550px; width: 100%; padding: 35px; text-align: center; position: relative; overflow: hidden; }}
                .verify-card::before {{ content: ''; position: absolute; top: 0; left: 0; right: 0; height: 5px; background: linear-gradient(90deg, #10b981, #3b82f6); }}
                .badge-status {{ display: inline-flex; align-items: center; gap: 8px; background: rgba(16, 185, 129, 0.15); color: #10b981; border: 1px solid rgba(16, 185, 129, 0.3); padding: 8px 18px; border-radius: 30px; font-weight: 600; font-size: 0.95rem; margin-bottom: 20px; }}
                .cert-title {{ font-size: 1.5rem; font-weight: 700; color: #fff; margin-bottom: 4px; }}
                .academy-name {{ color: #94a3b8; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 25px; }}
                .info-group {{ background: rgba(15, 23, 42, 0.6); border-radius: 12px; padding: 14px 18px; margin-bottom: 12px; text-align: right; display: flex; justify-content: space-between; align-items: center; border: 1px solid rgba(255, 255, 255, 0.05); }}
                .info-label {{ color: #94a3b8; font-size: 0.88rem; margin: 0; }}
                .info-value {{ color: #f8fafc; font-weight: 600; font-size: 0.98rem; margin: 0; }}
                .seal-icon {{ font-size: 3.5rem; color: #10b981; margin-bottom: 15px; filter: drop-shadow(0 0 12px rgba(16,185,129,0.4)); }}
            </style>
        </head>
        <body>
            <div class="verify-card">
                <div class="seal-icon"><i class="fas fa-certificate"></i></div>
                <div class="badge-status"><i class="fas fa-check-circle"></i> شهادة موثقة ورسمية</div>
                <div class="cert-title">نظام التوثيق الأكاديمي المباشر</div>
                <div class="academy-name">Lingo Go International Academy</div>
                <hr style="border-color: rgba(255,255,255,0.1); margin: 20px 0;">
                
                <div class="info-group">
                    <span class="info-label"><i class="fas fa-user-graduate text-primary me-2"></i> اسم الطالب:</span>
                    <span class="info-value">{cert.student_name}</span>
                </div>
                <div class="info-group">
                    <span class="info-label"><i class="fas fa-barcode text-info me-2"></i> كود التوثيق (ID):</span>
                    <span class="info-value" style="font-family: monospace; color: #3b82f6;">{cert.cert_code}</span>
                </div>
                <div class="info-group">
                    <span class="info-label"><i class="fas fa-calendar-alt text-warning me-2"></i> تاريخ الحصول عليها:</span>
                    <span class="info-value">{cert.issue_date}</span>
                </div>
                <div class="info-group">
                    <span class="info-label"><i class="fas fa-award text-success me-2"></i> المستوى المحقق:</span>
                    <span class="info-value">{cert.level_achieved}</span>
                </div>
                <div class="info-group">
                    <span class="info-label"><i class="fas fa-shield-alt text-success me-2"></i> حالة السجل:</span>
                    <span class="info-value" style="color: #10b981;">نشط ومسجل بالسجلات الرسمية</span>
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
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>خطأ في التوثيق - Lingo Go Academy</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
            <style>
                body {{ background: #0b0f19; color: #e2e8f0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; min-height: 100vh; display: flex; align-items: center; justify-content: center; padding: 20px; }}
                .verify-card {{ background: rgba(22, 31, 48, 0.9); border: 1px solid rgba(239, 68, 68, 0.3); border-radius: 20px; box-shadow: 0 15px 35px rgba(0,0,0,0.6); backdrop-filter: blur(12px); max-width: 550px; width: 100%; padding: 35px; text-align: center; position: relative; overflow: hidden; }}
                .verify-card::before {{ content: ''; position: absolute; top: 0; left: 0; right: 0; height: 5px; background: #ef4444; }}
                .badge-status {{ display: inline-flex; align-items: center; gap: 8px; background: rgba(239, 68, 68, 0.15); color: #ef4444; border: 1px solid rgba(239, 68, 68, 0.3); padding: 8px 18px; border-radius: 30px; font-weight: 600; font-size: 0.95rem; margin-bottom: 20px; }}
                .cert-title {{ font-size: 1.5rem; font-weight: 700; color: #fff; margin-bottom: 10px; }}
                .seal-icon {{ font-size: 3.5rem; color: #ef4444; margin-bottom: 15px; filter: drop-shadow(0 0 12px rgba(239,68,68,0.4)); }}
                .error-msg {{ color: #94a3b8; font-size: 0.95rem; line-height: 1.6; margin-top: 15px; }}
            </style>
        </head>
        <body>
            <div class="verify-card">
                <div class="seal-icon"><i class="fas fa-times-circle"></i></div>
                <div class="badge-status"><i class="fas fa-exclamation-triangle"></i> غير موثقة / كود غير موجود</div>
                <div class="cert-title">شهادة غير صالحة أو غير مسجلة</div>
                <p class="error-msg">كود التوثيق المرفق (<strong style="color: #ef4444;">{cert_id}</strong>) غير موجود في قاعدة بيانات الأكاديمية. هذه الشهادة تعتبر <span style="color: #ef4444; font-weight: bold;">غير رسمية أو مزورة</span>.</p>
            </div>
        </body>
        </html>
        """

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)