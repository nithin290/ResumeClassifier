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
@app.route('/', methods=['GET','POST'])
def main():
    

    print("dbg")
    # If a form is submitted
    if (request.method == "POST"):
        print("dbg")

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

        
        preference1 = request.form.get("Preference 1")
        preference2 = request.form.get("Preference 2")
        preference3 = request.form.get("Preference 3")
        
        # Put inputs to dataframe
        X = pd.DataFrame([[preference, text]], columns = ["Category", "Resume"])


        X['Resume'] = X['Resume'].str.replace("    ", " ")
        X['Resume'] = X['Resume'].str.replace('"', '')
        X['Resume'] = X['Resume'].apply(lambda x: x.replace('\t', ' '))
        X['Resume'] = X['Resume'].str.replace("'s", "")
        X['Resume'] = X['Resume'].apply(lambda x: x.replace('\n', ' '))

        # c = cv.transform(X['Resume'])
        c = cv.transform(text)
        var = clf.predict(c)
        last = le.inverse_transform(var)
        # Get prediction
        # prediction = clf.predict(X)[0]
        print(last[0])


        applicants = pd.read_csv("applicants.csv",header = 0,indx_col = false)
        print(applicants.tail())
        applicants.append({"pref1":preference,})
        
        
        
    else:
        prediction = ""
        
    return render_template("test_pdf_reader.html")
    # retrun NULL

# Running the app
if __name__ == '__main__':
    app.run(debug = True)
