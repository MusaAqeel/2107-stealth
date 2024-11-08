import os
from openai import OpenAI
from dotenv import load_dotenv
import json
import requests

load_dotenv()

def get_gpt_recommendations(prompt: str) -> dict:
   """
   Get song recommendations from GPT based on user prompt
   Args:
       prompt: User's prompt for playlist generation
   Returns:
       Dictionary containing song recommendations
   """
   client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
   
   completion = client.chat.completions.create(
       model="gpt-4o",
       messages=[
           {"role": "system", "content": """
               You are a Spotify playlist curator. Your task is to analyze user prompts and generate song recommendations. Always return a JSON array containing exactly 5 song recommendations. Each song must include "title" and "artist" fields.

               Example format:
               {
               "recommendations": [
                   {
                   "title": "song_title", 
                   "artist": "artist_name"
                   }
               ]
               }

               Rules:
               - Return only the JSON object without any other text
               - Include full artist names (no abbreviations)
               - Include exact song titles as they would appear on Spotify
               - Do not include additional commentary or explanations
               - Do not include song descriptions or reasons for recommendations
               - Ensure consistent JSON formatting
               - Must return exactly 15 songs, no more and no less
           """},
           {
               "role": "user", 
               "content": f"Prompt: {prompt}"
           }
       ]
   )

   return clean_gpt_response(completion.choices[0].message.content)

def clean_gpt_response(response_string: str) -> dict:
   """
   Clean GPT response by removing backticks and 'json' tag.
   Args:
       response_string: Raw response from GPT
   Returns:
       Cleaned dictionary of recommendations
   """
   cleaned = response_string.replace('```json', '').replace('```', '')
   return json.loads(cleaned)

def get_track_ids(recommendations: dict, auth_token: str) -> list:
   """
   Search and get Spotify track IDs for recommended songs.
   Args:
       recommendations: Dictionary containing recommendations
       auth_token: Spotify API bearer token
   Returns:
       List of Spotify track IDs
   """
   track_ids = []
   url = "https://api.spotify.com/v1/search"
   headers = {
       "Authorization": f"Bearer {auth_token}"
   }

   for song in recommendations['recommendations']:
       query = f"{song['title']} {song['artist']}"
       params = {
           "q": query,
           "type": "track",
           "limit": 1
       }
       
       try:
           response = requests.get(url, headers=headers, params=params)
           if response.status_code == 200:
               data = response.json()
               if data['tracks']['items']:
                   track_ids.append(data['tracks']['items'][0]['id'])
               else:
                   print(f"No track found for {song['title']} by {song['artist']}")
       except Exception as e:
           print(f"Error searching for {song['title']} by {song['artist']}: {str(e)}")
           continue

   return track_ids


def main(prompt: str, auth_token: str) -> list:
   """
   Main function to get recommendations and find track IDs
   Args:
       prompt: User's prompt for playlist generation
       auth_token: Spotify API bearer token
   Returns:
       List of Spotify track IDs
   """
   recommendations = get_gpt_recommendations(prompt)
   return get_track_ids(recommendations, auth_token)

if __name__ == "__main__":
   auth_token = "BQCQFQF7eBtomFa1FjYBOAIRdw6UHX9PrUmjAxNxcz_cMC1NJcBfndmS-jNmsimLGsDCkjNEkUcK9EMS6B4hv0hSm0OZH0fWmmqMcO9kHu7bh6mO3FI"
   prompt = "I want rap songs for my gym workout"
   track_ids = main(prompt, auth_token)
   print(track_ids)