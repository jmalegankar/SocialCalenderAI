from crewai import Task
from textwrap import dedent
# from datetime import datetime

# This is an example of how to define custom tasks.
# You can define as many tasks as you want.
# You can also define custom agents in agents.py

# Add output pydantics????

class AISoCalTasks:
    def __tip_section(self):
        return "If you do your BEST WORK, I'll give you a $10,000 commission!"

    def experience_recomendation_task(self, agent, user_data_1, user_data_2):
        return Task(
            description = dedent("""
                        Identify shared interests, hobbies, or passions between the two users, 
                        considering factors like scheduling constraints, location, and personal 
                        preferences. Then, generate hypothetical meetup scenarios that align with 
                        these commonalities.
                        """),
            agent = agent,
            async_execution = True,
            expected_output = dedent(f"""
                        ***Steps to Complete Task***:
                        Identify shared interests, hobbies, or passions between the two users.
                        Identify shared available slots at least 2 hours long during the week. 
                        Generate 3 hypothetical meetup scenarios that align with these 
                        commonalities.
                        
                        ***Output Format***: 
                        Return information about shared interests (**Shared Interests** and 
                        **Indirect Connections**), availability (**Availability**), and potential 
                        events (**Suggestions**) under 4 sections. Be as clear and concise as 
                        possible.

                        ****Example****:
                        ***Example Input***:
                        {{
                            "eventPreferences": ["sushi", "museum", "coffee", "concerts", 
                                    "reading", "movies", "hiking", "bar", "comedy club", 
                                    "bookstore"],
                            "availability": {{
                                "tuesday": [12, 13, 14, 19, 20],
                                "wednesday": [7, 8, 9, 12, 13, 14, 15, 18, 19],
                                "thursday": [19, 20],
                                "friday": [7, 8, 9, 18, 19],
                                "saturday": [9, 10, 11, 15, 16, 17, 18, 21, 22],
                                "sunday": [8, 9, 10, 14, 15, 16, 17, 20, 21]
                            }}
                        }},
                        {{
                            "eventPreferences": ["pizza", "movies", "gym", "travelling", "dancing", 
                                    "live music", "brewery", "restaurants", "video games", 
                                    "pub quiz"],
                            "availability": {{
                                "monday": [18, 19],
                                "tuesday": [18, 19],
                                "wednesday": [18, 19],
                                "thursday": [18, 19, 20, 21, 22],
                                "friday": [18, 19, 20, 21, 22],
                                "saturday": [9, 10, 11, 18, 19, 20, 21, 22],
                                "sunday": [8, 9, 10, 14, 15, 16, 17, 20, 21]
                            }}
                        }}

                        ***Example Output***:
                        **Shared Interests:**
                        Movies, Live Music
                        **Indirect Connections**
                        Food/Beverages, Workout Activities, Entertainment
                                     
                        **Availability:**
                        {{"Tuesday": [19, 20]}}
                        {{"Saturday": [15, 16]}}

                        **Suggestions**
                        1. **Tuesday Movie Night**: Meet at the local cinema to catch a movie 
                            together. 
                        2. **Saturday Live Music Session**: Head to a nearby brewery or pub that 
                            hosts live music events.
                        3. **Weekend Movie**: Meet up on Saturday afternoon for brunch, for a 
                            weekend matinee.

                        ***Input:***
                        {user_data_1}
                        {user_data_2}
                        """)
        )
    
    def event_curation_task(self, agent):
        return Task(
            description = dedent("""
                        Identify three actual events, activities, or venues in the database that 
                        matches the meetup suggestion, considering factors like location, time, and 
                        relevance.
                        """),
            agent = agent,
            async_execution = True,
            expected_output = dedent('''
                        ***Steps to Complete Task***:
                        Use the query_database tool to search the database restaurants for the 
                        users to attend based on hangout suggestions and the shared preferences. 
                        Make sure the input for the query_database only includes the kind of 
                        cuisine which they would like to eat.
                        List three actual events and provide a short 2 sentence explanation for 
                        each about why it is a good fit for the suggestions and the user 
                        preferences.
                                     
                        ***Output Format***: 
                        Return the start time (“start”), end time (“end”), name of the restaurant, 
                        venue or event (“title”), an ACCURATE event id (“id”), and add a short 
                        explanation why this is a great hangout option ADDRESSED TO USER 1 to the 
                        summary field (“summary”) in the JSON. MAKE SURE TO RETURN ACCURATE 
                        INFORMATION!!

                        ****Example****:
                        ***Example Input***:
                        **Shared Interests:**
                        * **Movies**: Both lists include "movies" as an interest.
                        * **Live Music**: One list has "concerts" and the other has "live music", 
                            which are related to live performances.
                        **Indirect Connections**
                        * **Food/Beverages**: Both lists include "sushi" (list 1) and "pizza" 
                            (list 2), which are types of food. List 2 also includes "brewery" and 
                            "restaurants", which are related to food and drink.
                        * **Workout Activities**: Lists 1 and 2 both contain activities like 
                            "hiking" (list 1), "gym" (list 2), "dancing" (list 2), which are all 
                            exercise oriented.
                        * **Entertainment**: Both lists have a focus on entertainment, with items 
                            like "movies", "concerts", "live music", "video games" (list 2), and 
                            "comedy club" (list 1) that suggest an interest in being entertained.

                        **Availability:**
                        * Tuesday: Both John and Jane have a 3-hour window available between 19:00 
                            and 21:00.
                        * Saturday: Both have a 2-hour window available between 15:00 and 17:00. 

                        **Suggestions**
                        **Tuesday Movie Night**: Meet at the local cinema to catch a movie together. 
                        **Saturday Live Music Session**: Head to a nearby brewery or pub that hosts 
                            live music events. Both can enjoy some craft beer and good tunes while 
                            exploring their shared interest in live music.
                        **Weekend Movie**: Meet up on Saturday afternoon for brunch, for a weekend 
                            matinee.

                        ***Example Output***:
                        {
                            "time_slot": {"Tuesday": [19, 20]},
                            "title": "Regal Cinema",
                            "summary": "Jane loves going to the movies, catch one with her on Tuesday",
                            "id": 4
                        },
                        {
                            "time_slot": {"Tuesday": [19, 20]},
                            "title": "Metro City Restaurant & Bar",
                            "summary": "This cool bar opened up recently, maybe you should go check it out with Jane",
                            "id": 2
                        },
                        {
                            "time_slot": {"Saturday": [15, 17]},
                            "title": "Regal Cinema",
                            "summary": "Jane loves going to the movies, catch one with her over the weekend",
                            "id": 4
                        }
                        ''')
        )
    
    def final_selection_task(self, agent):
        return Task(
            description = dedent("""
                        Analyze the meetup suggestion from the Event Curator Agent and confirm 
                        whether it meets the criteria set by the Experience Strategist Agent, 
                        taking into account the shared interests and scheduling constraints. Then 
                        choose the best of the options presented given the constraints.
                        """),
            agent = agent,
            async_execution = True,
            expected_output = dedent("""
                        ***Steps to Complete Task***:
                        Sanity check events returned by ECA and compare the events to users’ 
                        commonalities. Then return the best 
                        
                        ***Output Format***: 
                        Produce a JSON to return to the front end including information about the 
                        start time (“start”), end time (“end”), name of venue or event (“title”), 
                        the ECA’s explanation of the suggestion (“summary”), and the event id to 
                        point to the database (“id”). JSON MUST BE WELL FORMATTED!!

                        ****Example****:
                        ***Example Input***:
                        {
                            “time_slot”: {“Tuesday”: [19, 20]},
                            “title”: “Regal Cinema”,
                            “summary”: “Jane loves going to the movies, catch one with her on Tuesday”,
                            “id”: 4
                        },
                        {
                            “time_slot”: {“Tuesday”: [19, 20]},
                            “title”: “Metro City Restaurant & Bar”,
                            “summary”: “This cool bar opened up recently, maybe you should go check it out with Jane”,
                            “id”: 2
                        },
                        {
                            “time_slot”: {“Saturday”: [15, 17]},
                            “title”: “Regal Cinema”,
                            “summary”: “Jane loves going to the movies, catch one with her over the weekend”,
                            “id”: 4
                        }

                        ***Example Output***:
                        {
                            “time_slot”: {“Saturday”: [15, 17]},
                            “title”: “Regal Cinema”,
                            “summary”: “Jane loves going to the movies, catch one with her over the weekend”,
                            “id”: 4
                        }
                        """)
            #TODO: Add call back??
        )
