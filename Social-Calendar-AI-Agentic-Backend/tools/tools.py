#import json
from pydantic import BaseModel, Field, HttpUrl
from typing import List, Text, Optional
from textwrap import dedent
from datetime import datetime

from langchain.llms import Ollama #TODO: swap for api
#rom langchain_fireworks import Fireworks #TODO: switch to AWS Bedrock if this does not work!!
#from langchain_fireworks import Fireworks
from langchain.prompts import PromptTemplate
from langchain.tools import tool

import pymongo
from llama_index.vector_stores.mongodb import MongoDBAtlasVectorSearch
from llama_index.core import VectorStoreIndex
from llama_index.embeddings.openai import OpenAIEmbedding
import os
'''
import boto3
import json
from langchain_aws import ChatBedrock
bedrock_client = boto3.client(service_name="bedrock-runtime", region_name="us-west-2") # to be changed
model_id = "anthropic.claude-3-haiku-20240307-v1:0"

model_kwargs = {
    "max_tokens": 8192,
}

# Create the LangChain Chat object
llm = ChatBedrock(
    client=bedrock_client,
    model_id=model_id,
    model_kwargs=model_kwargs,
)
'''

'''
class Schedule(BaseModel):
    """Schedule class to define a schedule object"""
    monday:    Optional[List] = Field("Monday's list of hourly availability")
    tuesday:   Optional[List] = Field("Tuesday's list of hourly availability within a day")
    wednesday: Optional[List] = Field("Wednesday's list of hourly availability within a day")
    thursday:  Optional[List] = Field("Thursday's list of hourly availability within a day")
    friday:    Optional[List] = Field("Friday's list of hourly availability within a day")
    saturday:  Optional[List] = Field("Saturday's list of hourly availability within a day")
    sunday:    Optional[List] = Field("Sunday's list of hourly availability within a day")

class Venue(BaseModel):
    """Venue model"""
    name: str = Field(description="Name of venue")
    cuisine: str = Field(description="Cuisine of venue")
    id: str = Field(description="ID of venue")

class CommonScheduleInput(BaseModel):
    """Two schedules to compare"""
    schedule1: dict[List[int]] = Field("Weekly availability of User1")
    schedule2: dict[List[int]] = Field("Weekly availability of User2")

class CommonPreferencesInput(BaseModel):
    """Two lists of common interests to compare"""
    interests1: List = Field("Hangout Preferences of User1")
    interests2: List = Field("Hangout Preferences of User2")

class SearchInput(BaseModel):
    """Inputs to search MongoDB"""
    description: str = Field(description="food cuisine type to search")

class SearchOutput(BaseModel):
    """Outputs from search MongoDB"""
    results_list: List[Venue] = Field(description="List of venue datapoints")
'''
    

class AgentTools():
    @tool("find common schedule")
    def find_common_schedule(schedule1, schedule2):
        """
        Finds the common schedule between two schedules.

        Args:
            schedule1 (dict): first person's schedule.
            schedule2 (dict): second person's schedule.

        Returns:
            dict: Common schedule between the two schedules.
        """
        print("hola")
        
        # Initialize an empty dictionary to store the common schedule
        common_schedule = {}

        # Iterate through each day in the schedule
        for day in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]:
            # Initialize an empty list for the common schedule for the current day
            common_schedule[day] = []

            # Check if day is available in both schedules
            if day not in schedule1 or day not in schedule2:
                continue
            
            # Check for common availability between blocks
            common_schedule[day] = [hour for hour in schedule1[day] if hour in schedule2[day]]
        
        # Return the common schedule
        return common_schedule
    
    @tool("find common hangout preferences")
    def find_common_preferences(interests1, interests2):
        """
        Finds the common preferences between two people.

        Args:
            interests1 (str): first person's interests.
            interests2 (str): second person's interests.
        Returns:
            str: Common preferences between the two people.
        """
        os.environ["FIREWORKS_API_KEY"] = "KR5gGO0yzeqMhNgOzWecYtoismP9PahJsBs5uUt9YgGv9Hdn"

        # Instantiate ollama model to run queries TODO: swap for api
        ollama_llama3_8B = Ollama(model="llama3", stop=["<|eot_id|>"])
        '''fireworks_llama3_70B = Fireworks(
                                    model="accounts/fireworks/models/llama3-70B-instruct",
                                    max_tokens=2048 #TODO: check if this token max works
                                )'''

        # Define prompt template to find common interests and provide reasoning
        # TODO: Add template for extracting common interests and reasoning
        prompt_template = dedent("""
                        **Context:** You are an agent which finds common interests between two 
                        people hoping to hangout.
                        **Objective:** Return two lists if possible of shared interests or indirect 
                        connections with explananations for each connection found.
                        **Style:** clear and concise, make it easy to quickly scan and understand 
                        the shared interests, availability, and potential meetup suggestions. Use 
                        headings (**Shared Interests:** and **Indirect Connections:**), bullet 
                        points, and descriptive text to make the output organized and easy to 
                        follow.
                        **Tone:** Friendly, informal and approachable, making it feel like a 
                        personal invitation or suggestion, Encouraging, suggestions are presented 
                        in a positive light, emphasizing the potential for a fun and enjoyable 
                        experience, Personalized, specific details about each person's preferences, 
                        upbeat, enthusiastic, and inviting.
                        **Response:** Provide two short lists of shared interests and indirect 
                        connections between two people and give a one to two sentence explanation 
                        for each shared interest or indirect connection found. Shared interests 
                        MUST appear on both preference lists and this section may be left blank if 
                        there are no shared interests. Try to relate the indirect connections as 
                        much as possible.
                        
                        *Example Input:*
                        ["sushi", "museum", "coffee", "concerts", "reading", "movies", "hiking", 
                        "bar", "comedy club", "bookstore"]
                        ["pizza", "movies", "gym", "travelling", "dancing", "live music", 
                        "brewery", "restaurants", "video games", "pub quiz"]
                        
                        *Example Output:*
                        **Shared Interests:**
                        * **Movies**: Both lists include "movies" (list 1, list 2) as an interest.
                        * **Live Music**: One list has "concerts" (list 1) and the other has "live 
                        music" (list 2), which are related to live performances.
                        **Indirect Connections:**
                        * **Food/Beverages**: Both lists include "sushi" (list 1) and "pizza" (list 
                        2), which are types of food. List 2 also includes "brewery" and 
                        "restaurants", which are related to food and drink.
                        * **Workout Activities**: Lists 1 and 2 both contain activities like 
                        "hiking" (list 1), "gym" (list 2), "dancing" (list 2), which are all 
                        excercise oriented.
                        * **Entertainment**: Both lists have a focus on entertainment, with items 
                        like "movies", "concerts", "live music", "video games" (list 2), and 
                        "comedy club" (list 1) that suggest an interest in being entertained.
                        
                        *Input:*                        
                        {interests1}
                        {interests2}
                        
                        *Output:*
                        """)

        # Create prompt template with langchain
        prompt = PromptTemplate(
            input_variables=["interests1", "interests2"],
            template=prompt_template
        )

        # Run Ollama Query TODO: swap for api
        response = ollama_llama3_8B(prompt.format(interests1=interests1, interests2=interests2))

        # Return response from llm
        return response
    
    @tool("search restaurant database")
    def query_database(description):
        """
        Does a RAG Query on the database for a given description.

        Args:
            description (str): very short description for what to input.
        Returns:
            str: Events from the database.
        """
        username = 'ybordag'
        password = 'PASS'

        dburi="mongodb+srv://{}:{}@socialcalenderai.qimcftw.mongodb.net/?retryWrites=true&w=majority&appName=SocialCalenderAI".format(username, password)
        dbname='SocialCalenderDB'
        table='RestaurantsVectorDB'
        search_index='restaurantvectorindex'

        os.environ["OPENAI_API_KEY"] = "sk-proj-DmGRWGw6WeTUaBtnmiRYT3BlbkFJEyEy34zGByNm4Y9kMvyA"

        def get_mongo_client(dburi):
            """Establish connection to the MongoDB."""
            try:
                client = pymongo.MongoClient(dburi)
                print("Connection to MongoDB successful")
                return client
            except pymongo.errors.ConnectionFailure as e:
                print(f"Connection failed: {e}")
                return None
        
        #Test data embedding in Vector DB with OpenAI-3.5-turbo
        mongo_client = get_mongo_client(dburi)
        vector_store = MongoDBAtlasVectorSearch(mongo_client, db_name=dbname, collection_name=table, index_name=search_index)

        # Initialize OpenAI embedding model
        model_name = "text-embedding-3-small"
        embed_model = OpenAIEmbedding(model=model_name, dimensions=256)

        #Test data embedding in Vector DB with OpenAI-3.5-turbo
        index = VectorStoreIndex.from_vector_store(vector_store=vector_store, embed_model=embed_model)

        #Filter top k results from db....internal cosine similarity
        query_engine = index.as_query_engine(similarity_top_k=3) #can I just input the entire description????

        response = []
        for node_with_score in query_engine.query(description).source_nodes:
            node = {
                    'title' : node_with_score.node.metadata["properties.name"],
                    'cuisine' : node_with_score.node.metadata["properties.name"],
                    'id': node_with_score.node.metadata["id"]
                }
            response.append(node)

        return response