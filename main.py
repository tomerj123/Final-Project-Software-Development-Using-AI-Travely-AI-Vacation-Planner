from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI
import os
from kaggle.api.kaggle_api_extended import KaggleApi
from dotenv import load_dotenv
import re

load_dotenv()
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)
kaggle_api = KaggleApi()
# tryingggc omiitt
def get_dataset_suggestions(client, prompt):
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt + ". which dataset should I use for this project? i want to search for a dataset "
                                    "that is relevant to my project, please help me to create search queries so i "
                                    "will find in websites the best fitting datasets for this project. just write the search queries and nothing else.",
            }
        ],
        model="gpt-3.5-turbo"
    )
    return chat_completion.choices[0].message.content

def search_kaggle_datasets(search_term):
    api = KaggleApi()
    api.authenticate()
    search_results = api.dataset_list(search=search_term)
    print(search_results)
    return [{"title": dataset.title, "url": f'https://www.kaggle.com/{dataset.ref}'} for dataset in search_results]



app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


class ProjectDescription(BaseModel):
    description: str


@app.post("/find-dataset/")
async def find_dataset(project: ProjectDescription):
    suggestions = get_dataset_suggestions(client, project.description)
    # Use regex to find all occurrences of text within double quotes
    matched_suggestions = re.findall(r'"([^"]*)"', suggestions)

    # Take the first 2 matched suggestions if they exist
    top2suggestions = matched_suggestions[:2]

    print(top2suggestions)  # Debugging: Print matched suggestions to verify

    kaggle_results = []
    for suggestion in top2suggestions:
        # Search Kaggle datasets with the matched suggestion
        kaggle_results.extend(search_kaggle_datasets(suggestion))
    return {"Kaggle Results": kaggle_results}
