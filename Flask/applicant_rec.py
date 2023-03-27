from flask import Flask, request, render_template
import pandas as pd
import joblib
import PyPDF2
from sklearn.preprocessing import LabelEncoder
from sklearn.feature_extraction.text import CountVectorizer

# Declare a Flask app
app = Flask(__name__)

# Unpickle classifier
clf = joblib.load("clf.pkl")
cv = joblib.load("cv.pkl")
le = joblib.load("le.pkl")


# Main function here
@app.route('/applicant', methods=['GET','POST'])
def main():
    
    outputstr = ""
    print("dbg")
    # If a form is submitted
    if (request.method == "POST"):
        print("dbg")


        name = request.form.get('name')
        workexp = request.form.get('expYear')
        # reading the pdf
        print("starting to read!")

        file = request.files['file']
        pdf_reader = PyPDF2.PdfReader(file)
        num_pages = len(pdf_reader.pages)
        text = ''
        
        print(text)
        for page_num in range(num_pages):
            page = pdf_reader.pages[page_num]
            text += page.extract_text()
        
        text = text.replace('\n', ' ')

        print(text)

        print("read pdf")
        # reading the inputs

        
        pref1 = request.form.get("pref1")
        pref2 = request.form.get("pref2")
        pref3 = request.form.get("pref3")


        print(name)
        print(workexp)
        print(pref1)
        print(pref2)
        print(pref3)

        
        # Put inputs to dataframe
        X = pd.DataFrame([[name,pref1,pref2,pref3,workexp,text]], columns = ["name","pref1","pref2","pref3","workexp","resume"])


        X['resume'] = X['resume'].str.replace("    ", " ")
        X['resume'] = X['resume'].str.replace('"', '')
        X['resume'] = X['resume'].apply(lambda x: x.replace('\t', ' '))
        X['resume'] = X['resume'].str.replace("'s", "")
        X['resume'] = X['resume'].apply(lambda x: x.replace('\n', ' '))

        c = cv.transform(X['resume'])
        # c = cv.transform(text)
        var = clf.predict(c)
        last = le.inverse_transform(var)
        # Get prediction
        # prediction = clf.predict(X)[0]
        print(last[0])

        print(X)
        
        applicants = pd.read_csv("applicants.csv",header = 0,index_col = False)
        print(applicants.tail())
        # applicants.append({"name":name,"pref1":pref1,"pref2":pref2,"pref3":pref3,"workexp":workexp,"resume":X['Resume']},ignore_index = True)
        applicants = pd.concat([applicants,X],ignore_index = True)
        applicants.to_csv("applicants.csv",index = False)
        outputstr = last[0]
        
        
    else:
        prediction = ""
        
        
    return render_template("studentout.html",output = outputstr)
    # retrun NULL


@app.route("/")  # this sets the route to this page
def home():	
	return render_template("index.html")

# Running the app
if __name__ == '__main__':
    app.run(debug = True)
