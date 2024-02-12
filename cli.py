import requests

def get_dataset_suggestions(description):
    # Replace this URL with the actual URL of your FastAPI application
    url = "http://127.0.0.1:8000/find-dataset/"
    response = requests.post(url, json={"description": description})
    if response.status_code == 200:
        return response.json()["suggestions"]
    else:
        return "An error occurred while fetching dataset suggestions."

if __name__ == "__main__":
    print("Hi, please tell me a bit about your project and I can help you find a dataset.")
    project_description = input("Project Description: ")
    suggestions = get_dataset_suggestions(project_description)
    print("Suggestions:", suggestions)
