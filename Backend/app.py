# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import PyPDF2
import docx
import re
import io
import json
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
CORS(app)

# A sample database of skills and jobs for demonstration purposes (existing code)
KNOWN_SKILLS = ['python', 'javascript', 'react', 'node.js', 'sql', 'mongodb', 'data analysis', 'machine learning', 'aws', 'docker', 'communication', 'cloud computing']
JOBS = {
    'Software Engineer': ['python', 'javascript', 'react', 'node.js', 'sql'],
    'Data Scientist': ['python', 'data analysis', 'machine learning', 'sql'],
    'DevOps Engineer': ['aws', 'docker', 'python', 'node.js'],
}
COURSES = {
    'sql': 'SQL for Data Science (Coursera)',
    'cloud computing': 'AWS Certified Solutions Architect (Udemy)',
    'communication': 'Effective Communication (LinkedIn Learning)',
    'python': 'Complete Python Bootcamp (Udemy)',
    'react': 'Modern React with Redux (Udemy)',
}

# Simple in-memory user store for demonstration.
# In a real app, you would use a database.
USERS_DB_FILE = 'users.json'
users = {}

def load_users():
    """Load users from a JSON file."""
    global users
    try:
        with open(USERS_DB_FILE, 'r') as f:
            users = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        users = {}

def save_users():
    """Save users to a JSON file."""
    with open(USERS_DB_FILE, 'w') as f:
        json.dump(users, f, indent=4)

load_users()

@app.route('/api/signup', methods=['POST'])
def signup():
    """Handle new user registration."""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400

    if username in users:
        return jsonify({'error': 'Username already exists'}), 409

    hashed_password = generate_password_hash(password)
    users[username] = {'password': hashed_password}
    save_users()

    return jsonify({'message': 'User registered successfully'}), 201

@app.route('/api/login', methods=['POST'])
def login():
    """Handle user login."""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400

    user_data = users.get(username)
    if user_data and check_password_hash(user_data['password'], password):
        # In a real app, you would return a JWT or session token here
        return jsonify({'message': 'Login successful'}), 200
    else:
        return jsonify({'error': 'Invalid username or password'}), 401

# The existing analyze-resume route remains the same
@app.route('/api/analyze-resume', methods=['POST'])
def analyze_resume():
    try:
        file = request.files.get('resume')
        if not file:
            return jsonify({'error': 'No resume file provided'}), 400

        text = ''
        if file.filename.endswith('.pdf'):
            text = extract_pdf_text(file)
        elif file.filename.endswith('.docx'):
            text = extract_docx_text(file)
        
        if not text:
            return jsonify({'error': 'Could not extract text from file. Please check the file format.'}), 500

        skills = extract_skills(text)
        job_matches = find_job_matches(skills)
        target_job_title = request.form.get('targetJob', 'Software Engineer')
        skill_gaps = analyze_skill_gaps(skills, target_job_title)
        
        return jsonify({
            'skills': skills,
            'jobMatches': job_matches,
            'skillGaps': skill_gaps,
            'recommendations': get_course_recommendations(skill_gaps)
        })
        
    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({'error': 'An internal server error occurred.'}), 500

def extract_pdf_text(file):
    try:
        reader = PyPDF2.PdfReader(io.BytesIO(file.read()))
        text = ''
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + ' '
        return text
    except Exception as e:
        print(f"Error extracting PDF text: {e}")
        return ''

def extract_docx_text(file):
    try:
        doc = docx.Document(io.BytesIO(file.read()))
        text = ''
        for paragraph in doc.paragraphs:
            text += paragraph.text + ' '
        return text
    except Exception as e:
        print(f"Error extracting DOCX text: {e}")
        return ''

def extract_skills(text):
    found_skills = set()
    normalized_text = text.lower()
    for skill in KNOWN_SKILLS:
        if re.search(r'\b' + re.escape(skill) + r'\b', normalized_text):
            found_skills.add(skill)
    return list(found_skills)

def find_job_matches(skills):
    matches = []
    resume_skills_set = set(skills)
    for job_title, required_skills in JOBS.items():
        required_skills_set = set(required_skills)
        matching_skills = resume_skills_set.intersection(required_skills_set)
        if not required_skills_set:
            continue
        match_percentage = (len(matching_skills) / len(required_skills_set)) * 100
        matches.append({
            'title': job_title,
            'matchPercentage': round(match_percentage, 2),
            'matchingSkills': list(matching_skills)
        })
    matches.sort(key=lambda x: x['matchPercentage'], reverse=True)
    return matches

def analyze_skill_gaps(skills, target_job_title):
    user_skills_set = set(skills)
    target_job_skills = set(JOBS.get(target_job_title, []))
    missing_skills = list(target_job_skills.difference(user_skills_set))
    return missing_skills

def get_course_recommendations(skill_gaps):
    recommendations = []
    for skill in skill_gaps:
        if skill in COURSES:
            recommendations.append({
                'skill': skill,
                'course': COURSES[skill]
            })
    return recommendations

if __name__ == '__main__':
    app.run(debug=True, port=5000)