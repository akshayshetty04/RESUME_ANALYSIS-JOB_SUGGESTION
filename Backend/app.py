# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import PyPDF2
import docx
import re
import io
import json
from werkzeug.security import generate_password_hash, check_password_hash
import requests
from sklearn.feature_extraction.text import CountVectorizer

app = Flask(__name__)
CORS(app)

# SERP API Configuration
SERP_API_KEY = "8798a856414a63b9598ff259100140996a941820a46105dc01888c75e02c6631"
LOCATION = "India"

# Existing data models for demonstration
KNOWN_SKILLS = ['python', 'javascript', 'react', 'node.js', 'sql', 'mongodb', 'data analysis', 'machine learning', 'aws', 'docker', 'communication', 'cloud computing', 'java', 'backend development', 'agile']
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
    'java': 'Java Programming and Software Engineering Fundamentals (Coursera)',
    'backend development': 'The Complete 2024 Backend Developer Roadmap (Udemy)',
    'agile': 'Agile with Atlassian Jira (Coursera)',
}

# User authentication setup
USERS_DB_FILE = 'users.json'
users = {}
def load_users():
    global users
    try:
        with open(USERS_DB_FILE, 'r') as f:
            users = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        users = {}
def save_users():
    with open(USERS_DB_FILE, 'w') as f:
        json.dump(users, f, indent=4)
load_users()

# --- Web Scraping Function ---
def scrape_google_jobs(query, location):
    params = {
        "engine": "google_jobs",
        "q": query,
        "location": location,
        "hl": "en",
        "api_key": SERP_API_KEY
    }
    try:
        response = requests.get("https://serpapi.com/search", params=params)
        response.raise_for_status()
        data = response.json()
        jobs = data.get("jobs_results", [])
        return [{
            "title": job.get("title"),
            "company": job.get("company_name"),
            "location": job.get("location"),
            "posted_at": job.get("detected_extensions", {}).get("posted_at", "N/A"),
            "description": job.get("description"),
            "apply_link": job.get("via"),
        } for job in jobs]
    except requests.exceptions.RequestException as e:
        print(f"❌ Error scraping jobs: {e}")
        return []

# --- Machine Learning Analysis Function ---
def get_trending_skills(job_data):
    if not job_data:
        return []
    descriptions = [job['description'] for job in job_data if 'description' in job and job['description']]
    if not descriptions:
        return []

    vectorizer = CountVectorizer(stop_words='english', token_pattern=r'\b[a-zA-Z-]+\b', min_df=2)
    X = vectorizer.fit_transform(descriptions)
    feature_names = vectorizer.get_feature_names_out()
    counts = X.sum(axis=0).A1
    all_skill_counts = dict(zip(feature_names, counts))
    trending_skills_with_counts = {skill: all_skill_counts.get(skill.lower(), 0) for skill in KNOWN_SKILLS}
    sorted_skills = sorted(trending_skills_with_counts.items(), key=lambda item: item[1], reverse=True)
    return sorted_skills

# --- New function for trending course recommendations ---
def get_trending_course_recommendations(trending_skills):
    recommendations = []
    for skill, _ in trending_skills:
        if skill.lower() in COURSES:
            recommendations.append({
                'skill': skill,
                'course': COURSES[skill.lower()]
            })
    return recommendations

# --- API Routes ---
@app.route('/api/signup', methods=['POST'])
def signup():
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
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400
    user_data = users.get(username)
    if user_data and check_password_hash(user_data['password'], password):
        return jsonify({'message': 'Login successful'}), 200
    else:
        return jsonify({'error': 'Invalid username or password'}), 401

@app.route('/api/analyze-resume', methods=['POST'])
def analyze_resume():
    try:
        resume_file = request.files.get('resume')
        if not resume_file:
            return jsonify({'error': 'Resume file is required'}), 400

        resume_text = ''
        if resume_file.filename.endswith('.pdf'):
            resume_text = extract_pdf_text(resume_file)
        elif resume_file.filename.endswith('.docx'):
            resume_text = extract_docx_text(resume_file)
        
        if not resume_text:
            return jsonify({'error': 'Could not extract text from resume file.'}), 500

        resume_skills = extract_skills(resume_text)
        
        # Use resume skills to find relevant jobs
        query_string = ' '.join(resume_skills) if resume_skills else QUERY
        job_data = scrape_google_jobs(query_string, LOCATION)
        trending_skills_with_counts = get_trending_skills(job_data)
        
        # --- THE FIX IS HERE ---
        json_serializable_trending_skills = []
        for skill, count in trending_skills_with_counts:
            json_serializable_trending_skills.append([skill, int(count)])
        
        trending_course_recommendations = get_trending_course_recommendations(json_serializable_trending_skills)
        # --- END OF FIX ---
        
        return jsonify({
            'analysisType': 'resume',
            'skills': resume_skills,
            'jobMatches': find_job_matches(resume_skills),
            'skillGaps': analyze_skill_gaps(resume_skills),
            'recommendations': get_course_recommendations(get_skills_from_job_matches(find_job_matches(resume_skills))),
            'trendingSkills': json_serializable_trending_skills,
            'currentJobs': job_data[:5],
            'trendingCourses': trending_course_recommendations,
        })
    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({'error': 'An internal server error occurred.'}), 500

@app.route('/api/analyze-job-description', methods=['POST'])
def analyze_job_description():
    try:
        job_description_file = request.files.get('jobDescription')
        resume_file = request.files.get('resume')

        if not job_description_file:
            return jsonify({'error': 'Job description file is required'}), 400

        job_desc_text = ''
        if job_description_file.filename.endswith('.pdf'):
            job_desc_text = extract_pdf_text(job_description_file)
        elif job_description_file.filename.endswith('.docx'):
            job_desc_text = extract_docx_text(job_description_file)
        
        if not job_desc_text:
            return jsonify({'error': 'Could not extract text from job description file.'}), 500

        job_description_skills = extract_skills(job_desc_text)
        
        resume_skills = []
        if resume_file:
            resume_text = ''
            if resume_file.filename.endswith('.pdf'):
                resume_text = extract_pdf_text(resume_file)
            elif resume_file.filename.endswith('.docx'):
                resume_text = extract_docx_text(resume_file)
            resume_skills = extract_skills(resume_text)

        # Analyze skill gaps and recommendations
        user_skills_set = set(resume_skills)
        job_description_skills_set = set(job_description_skills)
        skill_gaps = list(job_description_skills_set.difference(user_skills_set))
        
        recommended_courses = get_course_recommendations(skill_gaps)

        # Return analysis specific to the job description
        return jsonify({
            'analysisType': 'jobDescription',
            'jobDescriptionSkills': job_description_skills,
            'mySkills': resume_skills,
            'skillGaps': skill_gaps,
            'recommendedCourses': recommended_courses,
        })
    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({'error': 'An internal server error occurred.'}), 500

# Helper functions for text extraction and analysis
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

def analyze_skill_gaps(skills):
    user_skills_set = set(skills)
    target_job_skills = set(JOBS.get('Software Engineer', []))
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
    
def get_skills_from_job_matches(job_matches):
    all_matching_skills = set()
    for match in job_matches:
        all_matching_skills.update(match['matchingSkills'])
    return list(all_matching_skills)

if __name__ == '__main__':
    app.run(debug=True, port=5000)