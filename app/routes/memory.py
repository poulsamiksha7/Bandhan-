# memory.py
from flask import Blueprint, render_template, redirect,url_for,flash, request
from flask_login import login_required, current_user
from app import db
from app.models import MoonMemory
from app.utils import get_moon_phase, get_moon_meaning
from datetime import datetime

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