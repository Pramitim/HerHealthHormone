from groq import Groq
import os
import json
from dotenv import load_dotenv

from ics import Calendar, Event
from datetime import datetime, date, timedelta


load_dotenv()

# Load the key from environment variable
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Prompts AI using user data
def generate_schedule(user_input):
    """
    Generate daily schedule for someone with PCOS using Llama 3.
    """

    prompt = f"""
    User Info:
    Timezone: {user_input.get('timezone')}
    Hours of Sleep per day: {user_input.get('sleep')}
    Time between meals(including snacks): {user_input.get('time_meal')}
    Hours awake until first meal: {user_input.get('first_meal')}
    Sufficient Protien, Fiber, Healthy Fats everyday: {user_input.get('diet')}
    Ethnicity: {user_input.get('ethnicity')}
    Number of times excerise per week: {user_input.get('times_exercised')}
    Types of excerise: {user_input.get('type_excerise')}
    Duration of excercises: {user_input.get('duration_exercised')}
    Recent Stress Levels: {user_input.get('stress')}
    Mood in past 24 hours: {user_input.get('mood')}
    Hours of day in work/school/occupied: {user_input.get('busy')}
    Medications taken {user_input.get('meds')}
    Consistent water intake through day {user_input.get('consistent_water')}
    More than 2 Liters of Water per day {user_input.get('enough_water')}
    Hours of day most fatigued {user_input.get('fatigue')}
    Symptoms {user_input.get('symptoms')}



    Time Guidelines (STRICT):
    - Breakfast: 07:00–11:00
    - Lunch: 11:00–14:00
    - Dinner: 17:00–21:00
    - Morning activities: 07:00–11:00
    - Midday activities: 11:00–15:00
    - Afternoon activities: 15:00–18:00
    - Evening activities: 18:00–22:00
    - Wind-down activities: after 20:00
    - No event may end before it starts.
    - All times must be realistic for a normal day.
    - Schedule activties/excerises outside of work/school hours

    Output ONLY valid JSON (list of events) like:

    [
      {{
        "title": "Morning Yoga",
        "start": "09:00",
        "end": "09:30"
        "notes":"Focusing on breathing and slow movements.
                Start streches from head to toe, spending 
                10 seconds per repition and 1 minute per strech
      }}
    ]

    Each event MUST inlcude a "notes"; field with suggestions and giving more context
    Notes should be 2-4 sentences.

    No commentary. No extra text.
    """

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )

    ai_output = response.choices[0].message.content

    return json.loads(ai_output)


# ICS Creation
def create_ics(events):
    cal = Calendar()
    from ics.grammar.parse import ContentLine
    cal.extra.append(ContentLine(name="X-WR-TIMEZONE", value="America/Toronto"))

    today = date.today()

    for e in events:
        event = Event()
        event.name = e["title"]

        event.description = e.get("notes","")

        start_time = datetime.strptime(e["start"], "%H:%M").time()
        end_time = datetime.strptime(e["end"], "%H:%M").time()

        # If end time invalid → add 30 min
        if end_time <= start_time:
            end_time = (datetime.combine(today, start_time) +
                        timedelta(minutes=30)).time()

        from zoneinfo import ZoneInfo
        local_tz = ZoneInfo("America/Toronto")

        event.begin = datetime.combine(today, start_time).replace(tzinfo=local_tz)
        event.end   = datetime.combine(today, end_time).replace(tzinfo=local_tz)


        cal.events.add(event)

    return cal.serialize()

