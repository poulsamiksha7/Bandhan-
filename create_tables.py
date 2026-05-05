from app import create_app,db
from app.models import(CoupleProfile,MoonMemory,SongDedication,BookMemory,BookQuote,JournalEntry,ShareToken)

app=create_app()

with app.app_context():
    db.create_all()
    print("All Bandhan Tables created successfully")