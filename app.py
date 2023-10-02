from flask import Flask, request, render_template, jsonify
import spacy
from pymongo import MongoClient
from gridfs import GridFS
from flask import send_file
from bson import ObjectId
from flask import Flask, render_template, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Email

app = Flask(__name__)

login_manager = LoginManager(app)
login_manager.login_view = 'login'
app.config['SECRET_KEY'] = 'random_key'

class User(UserMixin):
    def __init__(self, email, user_type):
        self.id = email
        self.user_type = user_type

@login_manager.user_loader
def load_user(email):
    client = MongoClient("MongDBURL") # Replace this with your own MongoDB url
    db = client["login"]
    user_data = db.users.find_one({"email": email})
    if user_data:
        return User(email=user_data["email"], user_type=user_data["user_type"])

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        client = MongoClient("MongDBURL")
        db = client["login"]
        user = db.users.find_one({"email": form.email.data})
        matched = check_password_hash(user['password'], form.password.data)
        
        if user and matched:
            user_obj = User(email=user["email"], user_type=user["user_type"])
            login_user(user_obj)  # This sets the current_user
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)




class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    user_type = StringField('User Type (candidate or company)', validators=[DataRequired()])
    submit = SubmitField('Register')

@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        new_user = {
            "email": form.email.data,
            "password": hashed_password,
            "user_type": form.user_type.data.lower()
        }

        # Insert the new user data into your database
        client = MongoClient("MongDBURL")
        db = client["login"]
        db.users.insert_one(new_user)

        print("CREATED")
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route("/logout")
@login_required
def logout():
    logout_user()  # This logs the user out
    return redirect(url_for('home'))  # You can redirect to 'login' or another page if you prefer


@app.route('/upload_form')
@login_required
def upload_form():
    if current_user.user_type != 'candidate':
        flash('You do not have access to this page', 'danger')
        return redirect(render_template('job_request.html'))
    return render_template('upload.html')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/dashboard')
@login_required
def dashboard():
    if not current_user.is_authenticated:
        flash('Please log in to access this page.')
    
    if current_user.user_type == 'candidate':
        return redirect(url_for('upload_form'))
    elif current_user.user_type == 'company':
        return render_template('job_request.html')
    else:
        flash('Unauthorized user type', 'danger')
        return redirect(url_for('logout'))

    
@app.route('/match', methods=['POST'])
def match_resumes():
    user_input = request.form.get('job_description')
    #user_skills = set(user_input.lower().split())
    nlp = spacy.load("model_upgrade")
    doc = nlp(user_input)
    technology_names = []

    for ent in doc.ents:
        if ent.label_ in ["ORG", "TECHNOLOGY", "TECH"]:
            technology_names.append(ent.text)

    #print(technology_names)

    bef_technology_names = technology_names

    technology_names = list(set(technology_names))

    technology_names = [ele.lower() for ele in technology_names]

    #print(technology_names)


    client = MongoClient("MongDBURL")
    db = client["candidates"]
    users = db["candidates"]

    user_data = list(users.aggregate([
    {
        "$match": {
            "skills": {
                "$in": technology_names
            }
        }
    },
    {
        "$addFields": {
            "matchedSkills": {
                "$size": {
                    "$setIntersection": ["$skills", technology_names]
                }
            }
        }
    },
    {
        "$sort": {
            "matchedSkills": -1,  # Sort by the number of matched skills (descending)
        }
    }
    ]))


    return render_template('view_resumes.html', user_data=user_data, technology_names=bef_technology_names)

@app.route("/upload", methods=["POST"])
def upload():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        skills = request.form["skills"]
        resume_file = request.files["resume"]

        client = MongoClient("MongDBURL")
        
        # Create or access the GridFS
        db = client["candidates"]
        fs = GridFS(db)
        
        skills = [skill.strip().lower() for skill in skills.split(',') if skill.strip()]
        skills = list(set(skills))


        # Store the resume file in MongoDB GridFS
        if resume_file:
            resume_id = fs.put(resume_file, filename=resume_file.filename)

            # Store user details in a MongoDB collection
            users = db["candidates"]
            user_data = {
                "name": name,
                "email": email,
                "skills":skills,
                "resume_id": resume_id
            }
            users.insert_one(user_data)
            flash('Resume Uploaded Successfully', 'success')
            return render_template('upload.html')

    return render_template('index.html')



@app.route('/fetch_resume/<resume_id>')
def fetch_resume(resume_id):
    client = MongoClient("MongDBURL")
    db = client["candidates"]
    fs = GridFS(db)

    #print(fs)

    # Fetching the file from GridFS
    resume_file = fs.get(ObjectId(resume_id))

    # Creating a response with the file data
    response = send_file(resume_file, mimetype='application/pdf', as_attachment=True, download_name=f"{resume_id}.pdf")

    

    return response


if __name__ == '__main__':
    app.run(debug=True)
