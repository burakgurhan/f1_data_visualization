import os
import groq
from dotenv import load_dotenv
from dataclasses import dataclass
import streamlit as st

load_dotenv()
# Load API key
api_key = st.secrets.get("API", {}).get("KEY", None)

# Debugging
if api_key:
    st.write("API key loaded successfully (hidden for security)")
else:
    st.error("API key not found! Check Streamlit secrets.")

@dataclass
class RaceData:
    race_info:dict
    #driver_dict:dict
    podium:dict
    top_10:dict
    fastest_lap:dict
    fastest_in_speed_trap:dict
    fastest_pit_stop_dict:dict


class Summary:
    def __init__(self, race_data: RaceData, model_name:str="llama-3.3-70b-versatile"):
        """
        Initialize the F1 summary generator with race data.
        
        Parameters:
        -----------
        race_data : RaceData
            A dataclass containing all the race information
        model_name : str
            The LLM model to use for generation
        """
        self.race_data = race_data
        self.model_name = model_name
        self.api_key = os.environ["GROQ_API_KEY"]

        if not self.api_key:
            raise ValueError("GROQ_API_KEY environment variable not set")
        
        self.llm_parameters = {
            "max_tokens": 500,
            "temperature": 0.2,
            "top_p": 0.95,
            "frequency_penalty": 0.2,
            "presence_penalty": 0.1
        }

        self.client = groq.Client(api_key=self.api_key)

    def create_prompt(self):
        prompt = f"""
                # Formula 1 Race Summary Task

                ## Race Information
                - Year: {self.race_data.race_info["Year"]}
                - Country: {self.race_data.race_info["Country"]}
                - Grand Prix: {self.race_data.race_info["Meeting Name"]}
                - Circuit Name: {self.race_data.race_info["Circuit"]}

                ## Podium
                {self.race_data.podium}

                ## Race Results
                {self.race_data.top_10}

                ## Fastest Lap Information
                {self.race_data.fastest_lap}

                ## Fastest in Speed Trap
                {self.race_data.fastest_in_speed_trap}

                ## Fastest Pit Stop
                {self.race_data.fastest_pit_stop_dict}
            """
        prompt += f"""
                ## Summary Task Instructions
                1. Write a professional Formula 1 race summary in 2-3 paragraphs (150-200 words).
                2. At first, introduce the race information, including the year, country, grand prix, and circuit name.
                3. First paragraph: Focus on the race winner, podium finishers, and general race outcome mention the names of drivers, do not call them with driver numbers.
                4. Second paragraph: Highlight notable performances, fastest lap and fastest pit stop including the team name.
                5. If available, mention the highest speed trap readings and which drivers achieved them.
                6. Maintain a professional, authoritative tone similar to official F1 media.
                7. Your content must be STRICTLY based on the provided data - do not add speculative or historical information.
                8. Do not reference championship standings or points implications.
                9. You may get help from the driver_dict to pronounce the driver informations better: {self.race_data.driver_dict}

                Create a factual, data-driven race summary that an F1 fan would find informative and engaging.
            """
        return prompt
    
    def create_summary(self):
        prompt = self.create_prompt()

        system_message = """You are an expert Formula 1 journalist with decades of experience covering the sport.
Your task is to write factual, engaging race summaries based STRICTLY on the data provided.
Your summaries should be professional, precise, and focused on what the data reveals.
Never speculate or add information not present in the data."""
        
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
            **self.llm_parameters
            )
        summary = response.choices[0].message.content
        return summary
    
def create_race_summary(race_info,
    #driver_dict,
    podium,
    top_10,
    fastest_lap,
    fastest_in_speed_trap,
    fastest_pit_stop_dict):
    
    # Create race data object
    race_data = RaceData(
        race_info,
    #driver_dict,
    podium,
    top_10,
    fastest_lap,
    fastest_in_speed_trap,
    fastest_pit_stop_dict
    )
    
    # Create summary generator
    generator = Summary(race_data)
    
    # Generate summary
    summary = generator.create_summary()
    
    return summary