from datetime import datetime

def get_moon_phase(date):
     
    '''
    Calculate moon phase for any given date.Returns(emoji,phase_name)
    '''
    #Known new moon reference date
    known_new_moon=datetime(2000,1,6)
    #Days since that known new moon
    if isinstance(date,datetime):
       target=date
    else:
        target=datetime.combine(date,datetime.min.time())

    days_since=(target-known_new_moon).days
    cycle_position=days_since % 29.53059

    #Map position to phase

    if cycle_position<1.85:
        return "🌑", "New Moon"
    elif cycle_position<7.38:
        return "🌒","Waxing Crescent"
    elif cycle_position<9.22:
        return "🌓","First Quarter"
    elif cycle_position<14.77:
        return "🌔","Waxing Gibbous"
    elif cycle_position<16.61:
        return "🌕", "Full Moon"
    elif cycle_position<22.15:
        return "🌖","Waning Gibbous"
    elif cycle_position<23.99:
        return "🌗","Last Quarter"
    else:
        return "🌘","Waning Crescent"
    
def get_moon_meaning(phase_name):
    '''
    Returns a poetic meaning for each moon phase
    '''

    meanings={
        "New Moon": "A new beginning. The perfect night to start your forever.",
        "Waxing Crescent": "Intentions growing. Love quietly building toward something beautiful.",
        "First Quarter": "Halfway to fullness. Challenges faced, commitments made.",
        "Waxing Gibbous": "Almost there. The universe was preparing for this moment.",
        "Full Moon": "Complete. Whole. Your love illuminated the entire sky that night.",
        "Waning Gibbous": "Gratitude moon. A night for counting every blessing.",
        "Last Quarter": "Reflection moon. Releasing the old, making room for forever.",
        "Waning Crescent": "Surrender moon. Trusting the universe with your story."

    }
        
    return meanings.get(phase_name,"A night written in stars")