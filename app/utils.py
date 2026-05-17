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

def get_coordinates(city):
    '''
    Convert city name to lan/lon
    '''
    try:
        url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1"
        response=req.get(url,timeout=10)
        data=response.json()
        results=data.get('results',[])
        if results:
            return results[0]['latitude'],results[0]['longitude']
    except Exception as e:
        print("GEO ERROR: ",str(e))
# fallback center of india 
    return 20.5937,78.9629

def get_wedding_weather(date,city='India'):
    lat,lon=get_coordinates(city)

    try:
        data_str=date.strftime('%Y-%m-%d')
        url=(f"https://archive-api.open-meteo.com/v1/archive"
             f"?latitude={lat}&longitude={lon}"
             f"&start_date={data_str}&end_date={data_str}"
             f"&daily=temperature_2m_max,temperature_2m_min,weathercode"
             f"&timezone=Asia%2FKolkata"
            )
        
        response=req.get(url,timeout=10)
        if response.status_code!=200:
            return None
        
        data=response.json()
        daily=data.get('daily',{})
        temp_max=daily.get('temperature_2m_max',[None])[0]
        temp_min=daily.get('temperature_2m_min',[None])[0]
        weathercode=daily.get('weathercode',[0])[0]

        return{
            'temp_max': temp_max,
            'temp_min': temp_min,
            'description' : get_weather_description(weathercode),
            'emoji': get_weather_emoji(weathercode),
            'weathercode':weathercode,
            'city':city
        }
    except Exception as e:
        print("WEATHER ERROR:",str(e))
        return None
    
def get_weather_description(code):
    if code == 0:
        return "Clear sky"
    elif code in [1, 2, 3]:
        return "Partly cloudy"
    elif code in [45, 48]:
        return "Foggy"
    elif code in [51, 53, 55]:
        return "Light drizzle"
    elif code in [61, 63, 65]:
        return "Rainy"
    elif code in [71, 73, 75]:
        return "Snowy"
    elif code in [80, 81, 82]:
        return "Rain showers"
    elif code in [95, 96, 99]:
        return "Thunderstorm"
    else:
        return "Mild weather"


def get_weather_emoji(code):
    if code == 0:
        return "☀️"
    elif code in [1, 2, 3]:
        return "⛅"
    elif code in [45, 48]:
        return "🌫️"
    elif code in [51, 53, 55, 61, 63, 65, 80, 81, 82]:
        return "🌧️"
    elif code in [71, 73, 75]:
        return "❄️"
    elif code in [95, 96, 99]:
        return "⛈️"
    else:
        return "🌤️"


def get_wedding_stars(date):
    month = date.month
    constellations = {
        1  : ("Orion",       "The Hunter",       "Betelgeuse, Rigel, Bellatrix",
               "Orion watched over your vows — the mightiest hunter in the sky."),
        2  : ("Gemini",      "The Twins",         "Castor, Pollux",
               "The twin stars shone down — two souls becoming one."),
        3  : ("Leo",         "The Lion",          "Regulus, Denebola",
               "Leo the Lion blessed your union with courage and heart."),
        4  : ("Virgo",       "The Maiden",        "Spica, Porrima",
               "Virgo rose as you said yes — a sign of grace and devotion."),
        5  : ("Boötes",      "The Herdsman",      "Arcturus",
               "Arcturus — one of the brightest stars — lit your wedding night."),
        6  : ("Scorpius",    "The Scorpion",      "Antares, Shaula",
               "Scorpius blazed with passion the night you became forever."),
        7  : ("Sagittarius", "The Archer",        "Kaus Australis, Nunki",
               "The Archer aimed true — as did your hearts — that July night."),
        8  : ("Aquila",      "The Eagle",         "Altair, Tarazed",
               "The Eagle soared above — carrying your promises to the stars."),
        9  : ("Pegasus",     "The Winged Horse",  "Markab, Scheat",
               "Pegasus flew that night — a symbol of boundless love."),
        10 : ("Andromeda",   "The Princess",      "Alpheratz, Mirach",
               "Andromeda shone — a princess finding her forever that night."),
        11 : ("Perseus",     "The Hero",          "Mirfak, Algol",
               "Perseus stood guard — the hero watching over your love story."),
        12 : ("Orion",       "The Hunter",        "Betelgeuse, Rigel, Bellatrix",
               "Orion returned — the winter king blessing your new beginning.")
    }
    data = constellations.get(month, constellations[1])
    return {
        'name'    : data[0],
        'title'   : data[1],
        'stars'   : data[2],
        'meaning' : data[3]
    }


def get_rain_meaning(weathercode):
    if weathercode in [61, 63, 65, 80, 81, 82, 51, 53, 55]:
        return "It rained on your wedding day. In many cultures, rain is the luckiest blessing — washing away the old, making room for something beautiful."
    elif weathercode == 0:
        return "The sky was perfectly clear — as if the universe cleared every cloud just to watch you say yes."
    elif weathercode in [1, 2, 3]:
        return "Clouds drifted softly — the sky was thinking, just like you were, before saying forever."
    elif weathercode in [95, 96, 99]:
        return "Thunder and lightning marked your beginning — a love as powerful as a storm."
    else:
        return "The weather held its breath — waiting for you to begin."