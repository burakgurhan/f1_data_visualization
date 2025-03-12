from dotenv import load_dotenv
import os
import groq
import streamlit as st
load_dotenv()

class Summary():
    def __init__(self, year, race_name, lap_times_df, fastest_lap, top_10_df, speed_trap_df, driver_df):
        self.year = year
        self.race_name = race_name
        self.lap_times = lap_times_df.to_json(orient='columns')
        self.fastest_lap = fastest_lap.to_json(orient='columns')
        self.top_10 = top_10_df.to_json(orient='columns')
        self.drivers = driver_df.to_json(orient='columns')
        self.speed_trap = speed_trap_df.to_json(orient='columns')
        self.model_name = "llama-3.3-70b-versatile"
        self.api_key = os.environ["GROQ_API_KEY"]
        self.api_key_st = st.secrets["API"]["KEY"]
        self.max_tokens = 500
        self.temperature = 0.1
        self.top_p = 0.95
        self.frequency_p = 0.2
        self.presence_p = 0.1


    def create_prompt(self):
        return  f"""
You are an experienced Formula 1 journalist tasked with creating a concise race summary for the {self.year} {self.race_name}.

IMPORTANT: Base your summary ONLY on the factual data provided below. Do not include any information that is not present in the data.

Race Information:
- Year: {self.year}
- Race: {self.race_name}
- Fastest Lap: {self.fastest_lap}

Final Results (Top 10):
{self.top_10}

Speed Trap Data:
{self.speed_trap}

Detailed Instructions:
1. Write a 2-3 paragraph summary of the race focused ONLY on the data provided.
2. In the first paragraph, highlight the podium finishers, and overall race result.
3. In the second paragraph, mention notable performances, the fastest lap.
4. If speed trap data is available, briefly mention the highest speed achieved on the speed trap.
5. Your tone should be professional and objective, similar to official F1 race reports.
6. Your summary should be approximately 150-200 words.
7. Do not mention events, rivalries, championships, or race incidents unless explicitly provided in the data.
8. DO NOT invent or include information that's not present in the provided data.
"""


    def create_summary(self):
        prompt = self.create_prompt()

        client = groq.Client(api_key=self.api_key_st)

        response = client.chat.completions.create(
            model=self.model_name,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            top_p=self.top_p,
            presence_penalty=self.presence_p,
            frequency_penalty=self.frequency_p,
            stream=False,
            response_format={"type":"text"},
            messages=[
                {
                "role": "user",
                "content": prompt
                }
            ]
            )
        return response.choices[0].message.content
