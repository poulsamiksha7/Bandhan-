from datetime import datetime
import requests as req

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

def get_book_for_wedding_month(month, year, language='english'):
    """
    Fetch a book using Open Library API.
    Free, no key, no quota limits.
    """
    lang_map = {
        'english'         : ['eng'],
        'hindi'           : ['hin'],
        'marathi'         : ['mar'],
        'english+hindi'   : ['eng', 'hin'],
        'english+marathi' : ['eng', 'mar']
    }

    lang_codes = lang_map.get(language, ['eng'])
    books_found = []
    years_to_try = [year, year - 1, year + 1]

    for lang_code in lang_codes:
        found = False
        for try_year in years_to_try:
            if found:
                break
            try:
                url = (
                    f"https://openlibrary.org/search.json"
                    f"?q=love+romance"
                    f"&first_publish_year={try_year}"
                    f"&language={lang_code}"
                    f"&limit=10"
                    f"&fields=title,author_name,cover_i,key,first_publish_year"
                )

                response = req.get(url, timeout=10)
                if response.status_code != 200:
                    continue

                data = response.json()
                docs = data.get('docs', [])

                for doc in docs:
                    title   = doc.get('title', '')
                    authors = doc.get('author_name', ['Unknown Author'])
                    author  = authors[0] if authors else 'Unknown Author'
                    cover_i = doc.get('cover_i')
                    key     = doc.get('key', '')

                    # Open Library cover URL format
                    cover_url = None
                    if cover_i:
                        cover_url = f"https://covers.openlibrary.org/b/id/{cover_i}-M.jpg"

                    # Open Library book page
                    buy_link = f"https://openlibrary.org{key}" if key else '#'

                    if title and author:
                        books_found.append({
                            'title'     : title,
                            'author'    : author,
                            'cover_url' : cover_url,
                            'buy_link'  : buy_link,
                            'language'  : lang_code
                        })
                        found = True
                        break

            except Exception as e:
                print("BOOK API ERROR:", str(e))
                continue

    return books_found if books_found else None