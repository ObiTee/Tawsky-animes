from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_login import LoginManager, UserMixin, current_user, login_user, logout_user, login_required
import os
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tawsky_animes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'mp4', 'webm', 'jpg', 'jpeg', 'png', 'gif', 'pdf'}

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    favorite_genres = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    last_login = db.Column(db.DateTime)

class Anime(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    genres = db.Column(db.String(200))
    rating = db.Column(db.Float)
    thumbnail = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, server_default=db.func.now())

class Episode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    anime_id = db.Column(db.Integer, db.ForeignKey('anime.id'), nullable=False)
    episode_number = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(200))
    video_url = db.Column(db.String(200), nullable=False)
    duration = db.Column(db.Integer)  # in seconds
    created_at = db.Column(db.DateTime, server_default=db.func.now())

class Manga(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    genres = db.Column(db.String(200))
    rating = db.Column(db.Float)
    thumbnail = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, server_default=db.func.now())

class Chapter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    manga_id = db.Column(db.Integer, db.ForeignKey('manga.id'), nullable=False)
    chapter_number = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(200))
    pages = db.Column(db.Text)  # JSON array of image URLs
    created_at = db.Column(db.DateTime, server_default=db.func.now())

class WatchHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    episode_id = db.Column(db.Integer, db.ForeignKey('episode.id'), nullable=False)
    watched_at = db.Column(db.DateTime, server_default=db.func.now())
    progress = db.Column(db.Integer)  # in seconds

class ReadHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.id'), nullable=False)
    read_at = db.Column(db.DateTime, server_default=db.func.now())
    page_number = db.Column(db.Integer)

# Flask-Login user loader
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Helper Functions
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/anime')
def anime():
    return render_template('anime.html')

@app.route('/anime/<int:anime_id>')
def anime_detail(anime_id):
    anime = {
        'id': anime_id,
        'title': 'Attack on Titan',
        'description': '...',
        'rating': 9.8,
        'genres': 'Action, Drama, Fantasy'
    }
    return render_template('anime_detail.html', anime=anime)

@app.route('/player/<int:anime_id>')
@app.route('/player/<int:anime_id>/<int:episode_number>')
def player(anime_id, episode_number=1):
    anime_title = "Attack on Titan"
    return render_template('player.html', anime_title=anime_title, episode_number=episode_number)

@app.route('/manga')
def manga():
    return render_template('manga.html')

@app.route('/manga/<int:manga_id>')
def manga_detail(manga_id):
    manga = {
        'id': manga_id,
        'title': 'Berserk',
        'description': '...',
        'rating': 9.9,
        'genres': 'Dark Fantasy, Horror, Action'
    }
    return render_template('manga_detail.html', manga=manga)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Logged in successfully!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        else:
            flash('Invalid email or password.', 'danger')
    
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        genres = request.form.getlist('genres')
        
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('signup'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists.', 'danger')
            return redirect(url_for('signup'))
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'danger')
            return redirect(url_for('signup'))
        
        new_user = User(
            username=username,
            email=email,
            password=generate_password_hash(password, method='sha256'),
            favorite_genres=','.join(genres)
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Account created successfully! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('signup.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('index'))

@app.route('/admin')
@admin_required
def admin():
    return render_template('admin.html')

@app.route('/admin/upload', methods=['POST'])
@admin_required
def upload_content():
    if request.method == 'POST':
        content_type = request.form.get('content_type')
        title = request.form.get('title')
        description = request.form.get('description')
        genres = request.form.getlist('genres')
        
        if 'file' not in request.files:
            flash('No file uploaded.', 'danger')
            return redirect(url_for('admin'))
        
        file = request.files['file']
        if file.filename == '':
            flash('No selected file.', 'danger')
            return redirect(url_for('admin'))
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            thumbnail = request.files['thumbnail']
            if thumbnail and allowed_file(thumbnail.filename):
                thumb_filename = secure_filename(thumbnail.filename)
                thumb_path = os.path.join(app.config['UPLOAD_FOLDER'], thumb_filename)
                thumbnail.save(thumb_path)
            else:
                thumb_path = None
            
            if content_type == 'anime':
                new_anime = Anime(
                    title=title,
                    description=description,
                    genres=','.join(genres),
                    thumbnail=thumb_path
                )
                db.session.add(new_anime)
                db.session.commit()
                flash('Anime added successfully!', 'success')
            elif content_type == 'manga':
                new_manga = Manga(
                    title=title,
                    description=description,
                    genres=','.join(genres),
                    thumbnail=thumb_path
                )
                db.session.add(new_manga)
                db.session.commit()
                flash('Manga added successfully!', 'success')
            elif content_type == 'episode':
                anime_id = request.form.get('anime_id')
                episode_number = request.form.get('episode_number')
                
                new_episode = Episode(
                    anime_id=anime_id,
                    episode_number=episode_number,
                    title=title,
                    video_url=file_path
                )
                db.session.add(new_episode)
                db.session.commit()
                flash('Episode added successfully!', 'success')
            elif content_type == 'chapter':
                manga_id = request.form.get('manga_id')
                chapter_number = request.form.get('chapter_number')
                
                new_chapter = Chapter(
                    manga_id=manga_id,
                    chapter_number=chapter_number,
                    title=title,
                    pages=file_path
                )
                db.session.add(new_chapter)
                db.session.commit()
                flash('Chapter added successfully!', 'success')
            
            return redirect(url_for('admin'))
    
    return redirect(url_for('admin'))

@app.route('/search')
def search():
    query = request.args.get('q', '')
    results = []
    return render_template('search.html', query=query, results=results)

@app.route('/api/suggestions')
def api_suggestions():
    query = request.args.get('q', '')
    suggestions = [
        {'id': 1, 'title': 'Attack on Titan', 'type': 'Anime'},
        {'id': 2, 'title': 'Demon Slayer', 'type': 'Anime'},
        {'id': 3, 'title': 'Death Note', 'type': 'Manga'}
    ]
    return {'results': suggestions}

@app.route('/api/watch-history', methods=['POST'])
@login_required
def api_watch_history():
    if request.method == 'POST':
        episode_id = request.json.get('episode_id')
        progress = request.json.get('progress')
        
        history = WatchHistory.query.filter_by(
            user_id=current_user.id,
            episode_id=episode_id
        ).first()
        
        if history:
            history.progress = progress
            history.watched_at = db.func.now()
        else:
            history = WatchHistory(
                user_id=current_user.id,
                episode_id=episode_id,
                progress=progress
            )
            db.session.add(history)
        
        db.session.commit()
        return {'status': 'success'}
    
    return {'status': 'error'}

# Initialize Database
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)