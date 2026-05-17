from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import MoonMemory, SongDedication, BookMemory, JournalEntry
from app.utils import (get_moon_phase, get_moon_meaning,
                       get_book_for_wedding_month,
                       get_wedding_weather, get_wedding_stars,
                       get_rain_meaning)
from datetime import datetime
import requests


memory = Blueprint('memory', __name__)


@memory.route('/dashboard')
@login_required
def dashboard():
    moon_data = None

    if current_user.wedding_date:
        existing_moon = MoonMemory.query.filter_by(
            couple_id  = current_user.id,
            event_name = 'wedding night'
        ).first()

        if existing_moon:
            moon_data = existing_moon
        else:
            emoji, phase_name = get_moon_phase(current_user.wedding_date)
            new_moon = MoonMemory(
                couple_id   = current_user.id,
                event_name  = 'wedding night',
                event_date  = current_user.wedding_date,
                phase_name  = phase_name,
                phase_emoji = emoji
            )
            try:
                db.session.add(new_moon)
                db.session.commit()
                moon_data = new_moon
            except Exception as e:
                db.session.rollback()
                print("MOON ERROR:", str(e))

    bride_dedication = SongDedication.query.filter_by(
        couple_id    = current_user.id,
        dedicated_by = 'bride'
    ).first()

    groom_dedication = SongDedication.query.filter_by(
        couple_id    = current_user.id,
        dedicated_by = 'groom'
    ).first()

    return render_template(
        'memory/dashboard.html',
        couple           = current_user,
        moon_data        = moon_data,
        bride_dedication = bride_dedication,
        groom_dedication = groom_dedication
    )


@memory.route('/song-dedication', methods=['GET', 'POST'])
@login_required
def song_dedication():
    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'search':
            song_name   = request.form.get('song_name', '').strip()
            artist_name = request.form.get('artist_name', '').strip()

            if not song_name or not artist_name:
                flash('Please enter both song name and artist name.', 'error')
                return redirect(url_for('memory.song_dedication'))

            try:
                url      = f"https://api.lyrics.ovh/v1/{artist_name}/{song_name}"
                response = requests.get(url, timeout=10)

                if response.status_code == 200:
                    data   = response.json()
                    lyrics = data.get('lyrics', '')
                    lines  = [
                        line.strip()
                        for line in lyrics.split('\n')
                        if line.strip()
                    ]
                    return render_template(
                        'memory/song_dedication.html',
                        lines       = lines,
                        song_name   = song_name,
                        artist_name = artist_name
                    )
                else:
                    flash('Song not found. Try different spelling.', 'error')
                    return redirect(url_for('memory.song_dedication'))

            except requests.exceptions.Timeout:
                flash('Request timed out. Please try again.', 'error')
                return redirect(url_for('memory.song_dedication'))
            except Exception as e:
                print("LYRICS ERROR:", str(e))
                flash('Could not fetch lyrics. Please try again.', 'error')
                return redirect(url_for('memory.song_dedication'))

        elif action == 'save':
            song_name        = request.form.get('song_name')
            artist_name      = request.form.get('artist_name')
            highlighted_line = request.form.get('highlighted_line')
            dedicated_by     = request.form.get('dedicated_by')

            if not highlighted_line:
                flash('Please select a line first.', 'error')
                return redirect(url_for('memory.song_dedication'))

            existing = SongDedication.query.filter_by(
                couple_id    = current_user.id,
                dedicated_by = dedicated_by
            ).first()

            if existing:
                existing.song_name        = song_name
                existing.artist_name      = artist_name
                existing.highlighted_line = highlighted_line
            else:
                dedication = SongDedication(
                    couple_id        = current_user.id,
                    dedicated_by     = dedicated_by,
                    song_name        = song_name,
                    artist_name      = artist_name,
                    highlighted_line = highlighted_line
                )
                db.session.add(dedication)

            try:
                db.session.commit()
                flash('Your song dedication has been saved. 🎵', 'success')
                return redirect(url_for('memory.dashboard'))
            except Exception as e:
                db.session.rollback()
                print("SAVE ERROR:", str(e))
                flash('Could not save. Please try again.', 'error')

    return render_template('memory/song_dedication.html',
                           lines       = None,
                           song_name   = None,
                           artist_name = None)


@memory.route('/book-memory')
@login_required
def book_memory():
    if not current_user.wedding_date:
        flash('Please add your wedding date first.', 'error')
        return redirect(url_for('memory.dashboard'))

    wedding_month = current_user.wedding_date.month
    wedding_year  = current_user.wedding_date.year
    language      = current_user.language

    existing_books = BookMemory.query.filter_by(
        couple_id = current_user.id
    ).all()

    if existing_books:
        return render_template(
            'memory/book_memory.html',
            books         = existing_books,
            wedding_month = wedding_month,
            wedding_year  = wedding_year,
            already_saved = True
        )

    books_data = get_book_for_wedding_month(
        wedding_month,
        wedding_year,
        language
    )

    if not books_data:
        return render_template(
            'memory/book_memory.html',
            books         = None,
            wedding_month = wedding_month,
            wedding_year  = wedding_year,
            already_saved = False
        )

    saved_books = []
    for book in books_data:
        new_book = BookMemory(
            couple_id     = current_user.id,
            title         = book['title'],
            author        = book['author'],
            cover_url     = book['cover_url'],
            buy_link      = book['buy_link'],
            language      = book['language'],
            wedding_month = wedding_month,
            wedding_year  = wedding_year
        )
        db.session.add(new_book)
        saved_books.append(new_book)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print("BOOK SAVE ERROR:", str(e))

    return render_template(
        'memory/book_memory.html',
        books         = saved_books,
        wedding_month = wedding_month,
        wedding_year  = wedding_year,
        already_saved = False
    )


@memory.route('/wedding-night')
@login_required
def wedding_night():
    if not current_user.wedding_date:
        flash('Please add your wedding date first.', 'error')
        return redirect(url_for('memory.dashboard'))

    moon_data = MoonMemory.query.filter_by(
        couple_id  = current_user.id,
        event_name = 'wedding night'
    ).first()

    city        = current_user.city or 'India'
    weather     = get_wedding_weather(current_user.wedding_date, city)
    stars       = get_wedding_stars(current_user.wedding_date)
    rain_meaning = None

    if weather:
        rain_meaning = get_rain_meaning(weather['weathercode'])

    return render_template(
        'memory/wedding_night.html',
        couple       = current_user,
        moon_data    = moon_data,
        weather      = weather,
        stars        = stars,
        rain_meaning = rain_meaning
    )

@memory.route('/journal', methods=['GET','POST'])
@login_required
def journal():
    if request.method=='POST':
        content= request.form.get('content','').strip()
        written_by=request.form.get('written_by')

        if not content:
            flash('Please write something before saving.','error')
            return redirect(url_for('memory.journal'))
        
        if not written_by:
            flash('Please select who is writing','error')
            return redirect(url_for('memory.journal'))
        
        # get tonight moon phase
        from datetime import datetime
        tonight=datetime.utcnow()
        emoji,phase_name=get_moon_phase(tonight)

        entry=JournalEntry(
            couple_id=current_user.id,
            written_by=written_by,
            content=content,
            moon_phase=phase_name,
            is_private=True
        )

        try:
            db.session.add(entry)
            db.session.commit()
            flash('Your letter has been saved 💌','success')
            return redirect(url_for('memory.journal'))
        except Exception as e:
            db.session.rollback()
            print("JOURNAL ERROR: ",str(e))
            flash('Could not save. Please try again.','error')

    # fetch all entries for this couple
    entries=JournalEntry.query.filter_by(
        couple_id=current_user.id
    ).order_by(JournalEntry.created_at.desc()).all()

    # get tonight's moon for display
    from datetime import datetime
    tonight=datetime.utcnow()
    emoji,phase_name=get_moon_phase(tonight)

    return render_template(
        'memory/journal.html',
        entries=entries,
        moon_emoji=emoji,
        moon_phase=phase_name
    )