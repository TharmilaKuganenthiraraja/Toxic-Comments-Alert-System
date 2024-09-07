import requests

url = 'http://127.0.0.1:5000/predict'
data = {'comment': 'Your comment here'}
response = requests.post(url, json=data)
print(response.json())

@app.route('/')
def home():
    return "Welcome to the Toxic Comment Classifier API!"
