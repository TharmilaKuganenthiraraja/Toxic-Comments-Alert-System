from flask import Flask, request, jsonify, render_template, Request
import joblib
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail, Message
import logging
import os
import pytz


app = Flask(__name__)

# Configure the PostgreSQL database connection
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:tharmi@localhost/toxic_comment_system'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database and mail services
db = SQLAlchemy(app)
mail = Mail(app)


# Load the model and vectorizer
model = joblib.load('toxic_comment_model.pkl')
vectorizer = joblib.load('vectorizer.pkl')



# Define the Comment model
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.String, nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
    toxic = db.Column(db.Boolean, nullable=False)
    resolved = db.Column(db.Boolean, default=False)


# Define the Admin model
class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Create the database tables
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin')
def admin_dashboard():
    comments = Comment.query.all()
    return render_template('admin_dashboard.html', comments=comments)

       
@app.route('/submit_comment', methods=['POST'])
def submit_comment():
    data = request.get_json()
    comment_text = data['comment']
 
    # Transform the comment using the vectorizer
    transformed_comment = vectorizer.transform([comment_text])
    
    # Predict using the model
    prediction = model.predict(transformed_comment)
    is_toxic = bool(prediction[0])
    
       # Add comment to the database
    comment = Comment(comment=comment_text, toxic=is_toxic)
    db.session.add(comment)
    db.session.commit()
            
    return jsonify({'result': 'Comment submitted successfully!', 'toxic': is_toxic})


@app.route('/delete_comment/<int:id>', methods=['POST'])
def delete_comment(id):
    comment = Comment.query.get_or_404(id)
    db.session.delete(comment)
    db.session.commit()
    return jsonify({'result': 'Comment deleted successfully!'})

# generating a hashed password
hashed_password = generate_password_hash('PT2024')
print(hashed_password)


@app.route('/get_toxic_comments', methods=['GET'])
def get_toxic_comments():
    toxic_comments = Comment.query.filter_by(toxic=True).all()  # Assuming you have a 'Comment' model
    result = [
        {"comment": comment.comment, "timestamp": comment.timestamp}
        for comment in toxic_comments
    ]
    return jsonify(result)


@app.route('/notifications')
def notifications():
    # Query the database for all comments
    comments_from_db = Comment.query.all()

    # Sri Lanka time zone
    sri_lanka_tz = pytz.timezone('Asia/Colombo')

    # Create a list of toxic comments with timestamps converted to Sri Lanka time
    toxic_comments = []
    
    for comment in comments_from_db:
        if comment.timestamp:
            # Assuming comment.timestamp is a datetime object
            utc_timestamp = comment.timestamp
            sri_lanka_time = utc_timestamp.astimezone(sri_lanka_tz)
        else:
            sri_lanka_time = None  # Handle cases where timestamp is None or invalid
        
        toxic_comments.append({
            'id': comment.id,
            'comment': comment.comment,
            'timestamp': sri_lanka_time
        })

    return render_template('notifications.html', toxic_comments=toxic_comments)

@app.route('/notifications_count', methods=['GET'])
def notifications_count():
    # Query for unresolved toxic comments
    toxic_count = Comment.query.filter_by(toxic=True, resolved=False).count()
    return render_template('notifications.html', count=toxic_count)

@app.route('/resolve_comment/<int:id>', methods=['POST'])
def resolve_comment(id):
    comment = Comment.query.get_or_404(id)
    comment.resolved = True
    db.session.commit()
    return render_template({'notifications.html': 'Comment marked as resolved!'})

if __name__ == '__main__':
    app.run(debug=True)
