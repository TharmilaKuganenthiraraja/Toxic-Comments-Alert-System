from flask import Flask, request, jsonify, render_template, Request
import joblib
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail, Message
import logging
import os


app = Flask(__name__)

# Configure the PostgreSQL database connection
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:tharmi@localhost/toxic_comment_system'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database and mail services
db = SQLAlchemy(app)
mail = Mail(app)

# Flask-Mail configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'tharmila9746@gmail.com'  # Your Gmail
app.config['MAIL_PASSWORD'] = 'Dharmi_p@2016'  # Gmail app password or actual password
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True


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

# Function to send email alert
def send_email_alert(comment_text):
    try:
        msg = Message(
            'Toxic Comment Alert',
            sender='piranatharmi@gmail.com', 
            recipients=['tharmila@gmail.com']  # Admin email to receive notifications
        )
        msg.body = f'Toxic comment detected: {comment_text}'
        mail.send(msg)
        print("Email alert sent successfully!")
    except Exception as e:
        logging.error(f"Failed to send email: {e}")
        print(f"Error: {e}")
        
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
    
     # If the comment is toxic, send an email alert
    if is_toxic:
        send_email_alert(comment_text)
        
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


# Function to send email alert
def send_email_alert(comment_text):
    msg = Message('Toxic Comment Alert', sender='tharmila9746@gmail.com', recipients=['tharmila9746@gmail.com'])
    msg.body = f'Toxic comment detected: {comment_text}'
    mail.send(msg)
# Mock database query (replace this with a real database call)
toxic_comments = [
    {"id": 1, "comment": "This is a toxic comment!", "timestamp": "2024-09-15 12:45"},
    {"id": 2, "comment": "Another bad comment.", "timestamp": "2024-09-15 13:00"}
]

@app.route('/get_toxic_comments', methods=['GET'])
def get_toxic_comments():
    toxic_comments = Comment.query.filter_by(toxic=True).all()  # Assuming you have a 'Comment' model
    result = [
        {"comment": comment.text, "timestamp": comment.timestamp}
        for comment in toxic_comments
    ]
    return jsonify(result)


@app.route('/notifications')
def notifications():
    return render_template('notifications.html', toxic_comments=toxic_comments)

if __name__ == '__main__':
    app.run(debug=True)
