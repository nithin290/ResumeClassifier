from flask import Flask, request, render_template
import pandas as pd
import joblib
import PyPDF2
from sklearn.preprocessing import LabelEncoder
from sklearn.feature_extraction.text import CountVectorizer


# Declare a Flask app
app = Flask(__name__)

# Unpickle classifier
clf = joblib.load("pickled_files/clf.pkl")
cv = joblib.load("pickled_files/cv.pkl")
le = joblib.load("pickled_files/le.pkl")
applicants = pd.read_csv("applicants.csv", header=0, index_col=False)
username = None


@app.route('/recruiterout', methods=['GET', 'POST'])
def recruiterout():
    names = None
    appl_data = pd.read_csv("applicants.csv")
    if (request.method == "POST"):

        job_category_encoded = request.form.get("recSel")
        print(type(job_category_encoded))

        jc_string = int(job_category_encoded)
        print(jc_string)
        print(type(jc_string))
        jc_list = [jc_string]
        # jc_list = column_or_1d(jc_list,warn = True)

        print(jc_list)
        print(type(jc_list))
        job_category = le.inverse_transform([jc_list])
        print(job_category)
        recruiter = pd.read_csv("applicants.csv", header=0, index_col=False)

        # for i in range(len(recruiter)):
        #     if(recruiter.loc[i,"model_category"] == job_category[0]):
        #         # print(recruiter.loc[i,"name"])
        #         names += (recruiter.loc[i,"name"])
        #         names += '\n'

        # print(names)
        names = appl_data.loc[appl_data["model_category"] == job_category[0]]

        # print(type(link_list))

        names = names.values.tolist()
        for i in range(len(names)):
            for j in range(len(names[i])):
                # if 1<=j<=3:
                # temp_list = le.inverse_transform([names[i][j]])
                # names[i][j] = temp_list[0]
                names[i][j] = (j, names[i][j])
        print(names)

    # if names is None:
    #     names = "No applicant has been found"
    return render_template("recruiterout.html", output=names)

    # Main function here


@app.route('/applicantout', methods=['GET', 'POST'])
def main():

    global username
    print(username)
    outputstr = ""
    print("dbg")
    links = pd.read_csv("links.csv")
    link_list = None
    # If a form is submitted
    if (request.method == "POST"):

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

        temp_list1 = le.inverse_transform([int(pref1)])
        temp_list2 = le.inverse_transform([int(pref2)])
        temp_list3 = le.inverse_transform([int(pref3)])

        print(temp_list1[0])
        print(temp_list2[0])
        print(temp_list3[0])

        # Put inputs to dataframe
        X = pd.DataFrame([[name, temp_list1[0], temp_list2[0], temp_list3[0], workexp, text, ""]], columns=[
                         "name", "pref1", "pref2", "pref3", "workexp", "resume", "model_category"])

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

        X["model_category"] = last[0]

        print(applicants.tail())
        # applicants.append({"name":name,"pref1":pref1,"pref2":pref2,"pref3":pref3,"workexp":workexp,"resume":X['Resume']},ignore_index = True)
        # applicants = pd.concat([applicants,X],ignore_index = True)

        applicants.loc[applicants["username"] == username, ["name", "pref1", "pref2", "pref3", "workexp", "resume",
                                                            "model_category"]] = [name, temp_list1[0], temp_list2[0], temp_list3[0], workexp, text, last[0]]
        print(applicants.tail())
        print(applicants["username"])
        print(username)
        applicants.to_csv("applicants.csv", index=False)
        outputstr = last[0]

        link_list = links.loc[links["Job_Title"] == outputstr]

        # print(type(link_list))

        link_list = link_list.values.tolist()
        for i in range(len(link_list)):
            for j in range(len(link_list[i])):
                link_list[i][j] = (j, link_list[i][j])
        # print(link_list)

    else:
        prediction = ""

    return render_template("studentout.html", output=link_list)
    # retrun NULL


@app.route("/applicant", methods=['GET', 'POST'])
def applicant():
    global username
    print(username)
    return render_template("student.html")


@app.route("/recruiter", methods=['GET', 'POST'])
def recruiter():
    return render_template("recruiter.html")


# this sets the route to this page
@app.route("/indexout", methods=['GET', 'POST'])
def indexout():
    global username
    print(username)
    email = request.form.get("email")
    password = request.form.get("password")
    usernames = applicants["username"].values.tolist()
    passwords = applicants["password"].values.tolist()
    if email in usernames and password in passwords:
        username = email
        print(username)
        return render_template("indexout.html", output="Logged In")
    elif email in usernames and password not in passwords:
        # username = None
        return render_template("indexout.html", output="Incorrect Password")
    elif email not in usernames:
        # username = None
        return render_template("indexout.html", output="Invalid Email ID")
    else:
        # username = None
        raise Exception("Error!")


# this sets the route to this page
@app.route("/registerout", methods=['GET', 'POST'])
def registerout():
    global applicants
    email = request.form.get("email")
    password = request.form.get("password")
    usernames = None
    passwords = None
    if not applicants.empty:
        usernames = applicants["username"].values.tolist()
        passwords = applicants["password"].values.tolist()

    if not usernames is None and email in usernames:
        return render_template("registerout.html", output="Email taken")
    elif not passwords is None and len(password) <= 4:
        return render_template("registerout.html", output="Password should have atleast 5 characters")
    else:
        username = email
        X = pd.DataFrame([[None, None, None, None, None, None, None, username, password]], columns=[
                         "name", "pref1", "pref2", "pref3", "workexp", "resume", "model_category", "username", "password"])

        applicants = pd.concat([applicants, X], ignore_index=True)

        applicants.to_csv("applicants.csv", index=False)
        print(applicants.head())
        return render_template("indexout.html", output="Account created")


# this sets the route to this page
@app.route("/register", methods=['GET', 'POST'])
def register():
    return render_template("register.html")


@app.route("/", methods=['GET', 'POST'])  # this sets the route to this page
def home():
    return render_template("index.html")


# Running the app
if __name__ == '__main__':
    app.run(debug=True)
