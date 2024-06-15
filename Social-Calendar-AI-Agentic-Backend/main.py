# import frameworks and llms
from crewai import Crew, Process
from langchain.llms import Ollama # TODO: swap for api
#from langchain_fireworks import Fireworks #TODO: switch to AWS Bedrock if this does not work!!

#from textwrap import dedent #useful for inputs

# import agents and tasks
from agents import AISoCalAgents
from tasks import AISoCalTasks

import os


# Define Article Writing Crew
class AISoCalCrew:
    def __init__(self):
        #TODO: swap for api
        self.ollama_llama3_8B = Ollama(model="crewai-llama3")
        '''
        os.environ["FIREWORKS_API_KEY"] = "KR5gGO0yzeqMhNgOzWecYtoismP9PahJsBs5uUt9YgGv9Hdn"
        self.fireworks_llama3_70B = Fireworks(
                                        model="accounts/fireworks/models/llama3-70B-instruct",
                                        max_tokens=2048 #TODO: check if this token max works
                                    )'''

    def run(self, user_data_1, user_data_2):
        # Define your agents and tasks in agents.py and tasks.py and import here
        agents = AISoCalAgents()
        tasks = AISoCalTasks()

        # set up agents
        experience_strategist_agent = agents.experience_strategist_agent()
        event_curator_agent = agents.event_curator_agent()
        meeting_maestro_agent = agents.meeting_maestro_agent()

        # set up tasks
        experience_recomendation_task = tasks.experience_recomendation_task(
                experience_strategist_agent, 
                user_data_1, 
                user_data_2
        ) 
        event_curation_task = tasks.event_curation_task(event_curator_agent)
        final_selection_task = tasks.final_selection_task(meeting_maestro_agent)

        # define crew with all agents and tasks
        crew = Crew(
            agents = [experience_strategist_agent, event_curator_agent, meeting_maestro_agent],
            tasks = [experience_recomendation_task, event_curation_task, final_selection_task],
            process = Process.sequential,
            verbose=True,
        )

        # run crew
        result = crew.kickoff()
        return result


# This is the main function that you will use to run your custom crew.
if __name__ == "__main__":
    print("## Let's generate some recommendations")
    user_data_1 = '''
        {
        "userId": 1,
        "name": "John Doe",
        "friends": [2, 3, 5],
        "eventPreferences": ["sushi", "boba", "coffee", "concerts", "bar", "movies", "hiking", "bar", "comedy club", "bookstore"],
        "availability": {
                "tuesday": [12, 13, 14, 19, 20],
                "wednesday": [7, 8, 9, 12, 13, 14, 15, 18, 19],
                "thursday": [19, 20],
                "friday": [7, 8, 9, 18, 19],
                "saturday": [9, 10, 11, 15, 16, 17, 18, 21, 22],
                "sunday": [8, 9, 10, 14, 15, 16, 17, 20, 21]
            }
        }
        '''
    
    user_data_2 = '''{
        "userId": 2,
        "name": "Jane Doe",
        "friends": [1, 3, 4],
        "eventPreferences": ["pizza", "boba", "gym", "travelling", "dancing", "live music", "brewery", "restaurants", "video games", "pub quiz"],
        "availability": {
                "monday": [18, 19],
                "tuesday": [18, 19],
                "wednesday": [18, 19],
                "thursday": [18, 19, 20, 21, 22],
                "friday": [18, 19, 20, 21, 22],
                "saturday": [9, 10, 11, 18, 19, 20, 21, 22],
                "sunday": [8, 9, 10, 14, 15, 16, 17, 20, 21]
            }
        }
        '''

    custom_crew = AISoCalCrew()
    result = custom_crew.run(user_data_1, user_data_2)
    print("\n\n########################")
    print("## Recommendation generation result:")
    print("########################\n")
    print(result)