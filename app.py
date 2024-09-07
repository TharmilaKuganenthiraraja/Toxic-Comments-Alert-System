from flask import Flask, request, jsonify, render_template
import joblib
from datetime import datetime

app = Flask(__name__)

# Load the model and vectorizer
model = joblib.load('toxic_comment_model.pkl')
vectorizer = joblib.load('vectorizer.pkl')

# Store comments for simplicity (in a real application, this should be a database)
comments_db = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin')
def admin_dashboard():
    return render_template('admin_dashboard.html', comments=comments_db)

@app.route('/submit_comment', methods=['POST'])
def submit_comment():
    data = request.json
    comment = data['comment']
    
    # Transform the comment using the vectorizer
    transformed_comment = vectorizer.transform([comment])
    
    # Predict using the model
    prediction = model.predict(transformed_comment)
    is_toxic = prediction[0]
    
    # Add comment to the database
    comment_entry = {
        'comment': comment,
        'timestamp': datetime.now(),
        'toxic': is_toxic
    }
    comments_db.append(comment_entry)
    
    # Notify admin if toxic
    if is_toxic:
        # In a real application, you would send an email or other type of notification
        print(f'ALERT: Toxic comment detected - "{comment}"')
    
    return jsonify({'result': 'Comment submitted successfully!'})

if __name__ == '__main__':
    app.run(debug=True)
