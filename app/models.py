from app import db
from flask_login import UserMixin
from datetime import datetime

class CoupleProfile(UserMixin,db.Model):
    __tablename__='couple_profile'

    id=db.Column(db.Integer,primary_key=True)
    bride_name=db.Column(db.String(100),nullable=False)
    groom_name=db.Column(db.String(100),nullable=False)
    email=db.Column(db.String(150),unique=True,nullable=False)
    password=db.Column(db.String(200),nullable=False)
    wedding_date=db.Column(db.DateTime,nullable=True)
    their_story=db.Column(db.Text,nullable=True)
    language=db.Column(db.String(20),default='english')
    created_at=db.Column(db.DateTime,default=datetime.utcnow)

class MoonMemory(db.Model):
    __tablename__='moon_memory'

    id= db.Column(db.Integer,primary_key=True)
    couple_id= db.Column(db.Integer, db.ForeignKey('couple_profile.id'),nullable=False)
    event_date=db.Column(db.DateTime)
    phase_name= db.Column(db.String(50))
    phase_emoji = db.Column(db.String(10))
    created_at = db.Column(db.DateTime,default=datetime.utcnow)

class SongDedication(db.Model):
    __tablename__='song_dedication'

    id= db.Column(db.Integer,primary_key=True)
    couple_id= db.Column(db.Integer,db.ForeignKey('couple_profile.id'), nullable=False)
    dedicated_by= db.Column(db.String(10))
    song_name=db.Column(db.String(200))
    artist_name=db.Column(db.String(200))
    full_lyrics=db.Column(db.Text)  
    highlighted_line= db.Column(db.Text)
    created_at= db.Column(db.DateTime,default=datetime.utcnow)

class BookMemory(db.Model):
    __tablename__='book_memory'

    id=db.Column(db.Integer,primary_key=True)
    couple_id=db.Column(db.Integer,db.ForeignKey('couple_profile.id'),nullable=False)
    title=db.Column(db.String(300))
    author=db.Column(db.String(200))
    cover_url=db.Column(db.String(500))
    buy_link=db.Column(db.String(500))
    language=db.Column(db.String(20))
    wedding_month=db.Column(db.Integer)
    wedding_year=db.Column(db.Integer)
    created_at=db.Column(db.DateTime,default=datetime.utcnow)

class BookQuote(db.Model):
    __tablename__='book_quote'

    id=db.Column(db.Integer,primary_key=True)
    couple_id=db.Column(db.Integer,db.ForeignKey('couple_profile.id'),nullable=False)
    quote_text=db.Column(db.Text)
    book_name=db.Column(db.String(300))
    dedicated_by=db.Column(db.String(10))
    created_at=db.Column(db.DateTime,default=datetime.utcnow)

class JournalEntry(db.Model):
    __tablename__='journal_entry'

    id=db.Column(db.Integer,primary_key=True)
    couple_id=db.Column(db.Integer,db.ForeignKey('couple_profile.id'),nullable=False)
    written_by=db.Column(db.String(10))
    content=db.Column(db.Text)
    moon_phase=db.Column(db.String(50))
    is_private=db.Column(db.Boolean,default=True)
    created_at=db.Column(db.DateTime,default=datetime.utcnow)

class ShareToken(db.Model):
    __tablename__='share_token'

    id=db.Column(db.Integer,primary_key=True)
    couple_id=db.Column(db.Integer,db.ForeignKey('couple_profile.id'),nullable=False)
    token=db.Column(db.Integer,default=0)
    view_count=db.Column(db.Integer,default=0)
    created_at=db.Column(db.DateTime,default=datetime.utcnow)