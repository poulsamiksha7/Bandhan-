# memory.py
from flask import Blueprint, render_template, redirect,url_for,flash, request
from flask_login import login_required, current_user
from app import db
from app.models import MoonMemory
from app.utils import get_moon_phase, get_moon_meaning
from app.models import MoonMemory, SongDedication
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

    return render_template(
        'memory/dashboard.html',
        couple    = current_user,
        moon_data = moon_data
    )

@memory.route('/song-dedication', methods=['GET', 'POST'])
@login_required
def song_dedication():
    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'search':        # ← 8 spaces indent (inside POST)
            song_name = request.form.get('song_name', '').strip()
            artist_name = request.form.get('artist_name', '').strip()

            if not song_name or not artist_name:
                flash('Please enter both song name and artist name.', 'error')
                return redirect(url_for('memory.song_dedication'))

            try:
                url = f"https://api.lyrics.ovh/v1/{artist_name}/{song_name}"
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

        elif action == 'save':        # ← 8 spaces indent (inside POST)
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

    # GET request — outside POST block, 4 spaces indent
    return render_template('memory/song_dedication.html',
                           lines       = None,
                           song_name   = None,
                           artist_name = None)