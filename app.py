import random
from flask import jsonify
import secrets
from flask import Flask, render_template, flash, redirect, url_for, session, logging, request, session
from flask_sqlalchemy import SQLAlchemy
import os
from difflib import get_close_matches
from joblib import load
from duckduckgo_search import DDGS
mlb = load("model/mlb.joblib")
clf = load("model/random_forest.joblib")

ALLOWED_EXTENSIONS = ['png', 'jpg', 'jpeg']
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
app.secret_key = "9gN}fWZhE.ab9y."


def make_token():
    """
    Creates a cryptographically-secure, URL-safe string
    """
    return secrets.token_urlsafe(16) 
 
class user(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80))
    email = db.Column(db.String(120))
    password = db.Column(db.String(80))


@app.route("/")
def index():
    return render_template("index.html")


userSession = {}

@app.route("/user")
def index_auth():
    my_id = make_token()
    userSession[my_id] = -1
    return render_template("index_auth.html",sessionId=my_id)


@app.route("/instruct")
def instruct():
    return render_template("instructions.html")

@app.route("/upload")
def bmi():
    return render_template("bmi.html")

@app.route("/diseases")
def diseases():
    return render_template("diseases.html")

@app.route("/get_symptoms")
def get_symptoms_list():
    symptoms = set()
    for s in df['Symptoms']:
        for sym in str(s).split(','):
            symptoms.add(sym.strip())
    return jsonify(sorted(list(symptoms)))


@app.route('/pred_page')
def pred_page():
    pred = session.get('pred_label', None)
    f_name = session.get('filename', None)
    return render_template('pred.html', pred=pred, f_name=f_name)



@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        uname = request.form["uname"]
        passw = request.form["passw"]

        login = user.query.filter_by(username=uname, password=passw).first()
        if login is not None:
            return redirect(url_for("index_auth"))
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        uname = request.form['uname']
        mail = request.form['mail']
        passw = request.form['passw']

        register = user(username=uname, email=mail, password=passw)
        db.session.add(register)
        db.session.commit()

        return redirect(url_for("login"))
    return render_template("register.html")


import msgConstant as msgCons
import re

all_result = {
    'name':'',
    'age':0,
    'gender':'',
    'symptoms':[]
}


# Import Dependencies
# import gradio as gr
import pandas as pd
import numpy as np
from joblib import load
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

def predict_symptom(user_input, symptom_list):
    user_input = user_input.lower().strip()

    # Try direct matching first
    if user_input in symptom_list:
        return user_input

    # Fuzzy match for close symptoms
    matches = get_close_matches(user_input, symptom_list, n=1, cutoff=0.4)

    if matches:
        return matches[0]

    # If no match found, return None
    return None


import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Load the dataset into a pandas dataframe
dataset_path = os.path.join(os.path.dirname(__file__), 'expanded_dataset_v3.xlsx')
df = pd.read_excel(dataset_path)

symptoms_dict = {}

for s in df['Symptoms']:
    for symptom in str(s).split(','):
        symptoms_dict[symptom.strip()] = 0



def predict_disease_from_symptom(symptom_list):

    user_symptoms = symptom_list

    vectorizer = CountVectorizer()
    X = vectorizer.fit_transform(df['Symptoms'])
    user_X = vectorizer.transform([', '.join(user_symptoms)])

    similarity_scores = cosine_similarity(X, user_X)

    max_score = similarity_scores.max()
    max_indices = similarity_scores.argmax(axis=0)
    diseases = set()

    for i in max_indices:
        if similarity_scores[i] == max_score:
            diseases.add(df.iloc[i]['Disease'])

    if len(diseases) == 0:
        return "<b>No matching diseases found</b>", ""

    # Dynamic symptom handling
    symptoms = symptoms_dict.copy()

    for s in symptom_list:
        index = predict_symptom(s, list(symptoms.keys()))
        if index:
            symptoms[index] = 1

    # ML Prediction
    input_vector = mlb.transform([symptom_list])
    result = clf.predict(input_vector)

    disease_details = getDiseaseInfo(result[0])

    return f"<b>{result[0]}</b><br>{disease_details}", result[0]

    



import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# Get all unique diseases
diseases = set(df['Disease'])

def get_symtoms(user_disease):
    # Vectorize diseases using CountVectorizer
    vectorizer = CountVectorizer()
    X = vectorizer.fit_transform(df['Disease'])
    user_X = vectorizer.transform([user_disease])

    # Compute cosine similarity between user disease and dataset diseases
    similarity_scores = cosine_similarity(X, user_X)

    # Find the most similar disease(s)
    max_score = similarity_scores.max()
    print(max_score)
    if max_score < 0.7:
        print("No matching diseases found")
        return False,"No matching diseases found"
    else:
        max_indices = similarity_scores.argmax(axis=0)
        symptoms = set()
        for i in max_indices:
            if similarity_scores[i] == max_score:
                symptoms.update(set(df.iloc[i]['Symptoms'].split(',')))
        # Output results

        print("The symptoms of", user_disease, "are:")
        for sym in symptoms:
            print(str(sym).capitalize())

        return True,symptoms


from duckduckgo_search import DDGS

def getDiseaseInfo(keywords):
    try:
        results = DDGS().text(keywords, max_results=5)

        if results and len(results) > 0:
            return results[0]['body']
        else:
            return "No detailed description found. Please consult a medical professional."

    except Exception as e:
        print("Search Error:", e)
        return "Unable to fetch disease information at the moment."


@app.route('/ask',methods=['GET','POST'])
def chat_msg():

    user_message = request.args["message"].lower()
    sessionId = request.args["sessionId"]

    rand_num = random.randint(0,4)
    response = []
    if request.args["message"]=="undefined":

        response.append(msgCons.WELCOME_GREET[rand_num])
        response.append("What is your good name?")
        return jsonify({'status': 'OK', 'answer': response})
    else:


        currentState = userSession.get(sessionId)

        if currentState ==-1:
            response.append("Hi "+user_message+", To predict your disease based on symptopms, we need some information about you. Please provide accordingly.")
            userSession[sessionId] = userSession.get(sessionId) +1
            all_result['name'] = user_message            

        if currentState==0:
            username = all_result['name']
            response.append(username+", what is you age?")
            userSession[sessionId] = userSession.get(sessionId) +1

        if currentState==1:
            pattern = r'\d+'
            result = re.findall(pattern, user_message)
            if len(result)==0:
                response.append("Invalid input please provide valid age.")
            else:                
                if float(result[0])<=0 or float(result[0])>=130:
                    response.append("Invalid input please provide valid age.")
                else:
                    all_result['age'] = float(result[0])
                    username = all_result['name']
                    response.append(username+", Choose Option ?")            
                    response.append("1. Predict Disease")
                    response.append("2. Check Disease Symtoms")
                    userSession[sessionId] = userSession.get(sessionId) +1

        if currentState==2:

            if '2' in user_message.lower() or 'check' in user_message.lower():
                username = all_result['name']
                response.append(username+", What's Disease Name?")
                userSession[sessionId] = 20
            else:

                username = all_result['name']
                response.append(username+", What symptoms are you experiencing?")         
                response.append('<a href="/diseases" target="_blank">Symptoms List</a>')   
                userSession[sessionId] = userSession.get(sessionId) +1

        if currentState==3:

            
            all_result['symptoms'].extend(user_message.split(","))
            username = all_result['name']
            response.append(username+", What kind of symptoms are you currently experiencing?")            
            response.append("1. Check Disease")   
            response.append('<a href="/diseases" target="_blank">Symptoms List</a>')   
            userSession[sessionId] = userSession.get(sessionId) +1


        if currentState==4:

            if '1' in user_message or 'disease' in user_message:
                disease,type = predict_disease_from_symptom(all_result['symptoms'])  
                response.append("<b>The following disease may be causing your discomfort</b>")
                response.append(disease)
                response.append(f'<a href="https://www.google.com/search?q={type} disease hospital near me" target="_blank">Search Near By Hospitals</a>')   
                userSession[sessionId] = 10

            else:

                all_result['symptoms'].extend(user_message.split(","))
                username = all_result['name']
                response.append(username+", Could you describe the symptoms you're suffering from?")            
                response.append("1. Check Disease")   
                response.append('<a href="/diseases" target="_blank">Symptoms List</a>')   
                userSession[sessionId] = userSession.get(sessionId) +1

    
        if currentState==5:
            if '1' in user_message or 'disease' in user_message:
                disease,type = predict_disease_from_symptom(all_result['symptoms'])  
                response.append("<b>The following disease may be causing your discomfort</b>")
                response.append(disease)
                response.append(f'<a href="https://www.google.com/search?q={type} disease hospital near me" target="_blank">Search Near By Hospitals</a>')   

                userSession[sessionId] = 10

            else:

                all_result['symptoms'].extend(user_message.split(","))
                username = all_result['name']
                response.append(username+", What are the symptoms that you're currently dealing with?")            
                response.append("1. Check Disease")   
                response.append('<a href="/diseases" target="_blank">Symptoms List</a>')   
                userSession[sessionId] = userSession.get(sessionId) +1

        if currentState==6:    

            if '1' in user_message or 'disease' in user_message:
                disease,type = predict_disease_from_symptom(all_result['symptoms'])  
                response.append("The following disease may be causing your discomfort")
                response.append(disease)
                response.append(f'<a href="https://www.google.com/search?q={type} disease hospital near me" target="_blank">Search Near By Hospitals</a>')   
                userSession[sessionId] = 10
            else:
                all_result['symptoms'].extend(user_message.split(","))
                username = all_result['name']
                response.append(username+", What symptoms have you been experiencing lately?")            
                response.append("1. Check Disease")   
                response.append('<a href="/diseases" target="_blank">Symptoms List</a>')   
                userSession[sessionId] = userSession.get(sessionId) +1

        if currentState==7:
            if '1' in user_message or 'disease' in user_message:
                disease,type = predict_disease_from_symptom(all_result['symptoms'])  
                response.append("<b>The following disease may be causing your discomfort</b>")
                response.append(disease)
                response.append(f'<a href="https://www.google.com/search?q={type} disease hospital near me" target="_blank">Search Near By Hospitals</a>')   
                userSession[sessionId] = 10
            else:
                all_result['symptoms'].extend(user_message.split(","))
                username = all_result['name']
                response.append(username+", What are the symptoms that you're currently dealing with?")            
                response.append("1. Check Disease")   
                response.append('<a href="/diseases" target="_blank">Symptoms List</a>')   
                userSession[sessionId] = userSession.get(sessionId) +1


        if currentState==8:    

            if '1' in user_message or 'disease' in user_message:
                disease,type = predict_disease_from_symptom(all_result['symptoms'])  
                response.append("The following disease may be causing your discomfort")
                response.append(disease)
                response.append(f'<a href="https://www.google.com/search?q={type} disease hospital near me" target="_blank">Search Near By Hospitals</a>')   
                userSession[sessionId] = 10
            else:
                all_result['symptoms'].extend(user_message.split(","))
                username = all_result['name']
                response.append(username+", What symptoms have you been experiencing lately?")            
                response.append("1. Check Disease")   
                response.append('<a href="/diseases" target="_blank">Symptoms List</a>')   
                userSession[sessionId] = userSession.get(sessionId) +1

        if currentState==10:
            response.append('<a href="/user" target="_blank">Predict Again</a>')   

        
        if currentState==20:

            result,data = get_symtoms(user_message)
            if result:
                response.append(f"The symptoms of {user_message} are")
                for sym in data:
                    response.append(sym.capitalize())

            else:response.append(data)

            userSession[sessionId] = 2
            response.append("")
            response.append("Choose Option ?")            
            response.append("1. Predict Disease")
            response.append("2. Check Disease Symtoms")




                

        return jsonify({'status': 'OK', 'answer': response})




if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=False, port=3000)



@app.route("/get_symptoms")
def get_symptoms_list():
    symptoms = set()
    for s in df['Symptoms']:
        for sym in str(s).split(','):
            symptoms.add(sym.strip())
    return jsonify(sorted(list(symptoms)))