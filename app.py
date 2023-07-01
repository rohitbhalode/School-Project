from flask import Flask, render_template, request, redirect, session
from database import login_validation, teacher_info, new_Admission,submit_new_admission

app = Flask(__name__)


@app.route("/")
def welcome():
  return render_template("home.html")


@app.route("/dummy")
def dummy():
  return render_template("dummy.html")


@app.route("/login")
def login():
  return render_template("index.html")


Username = None


@app.route("/submit", methods=['POST'])
def result():
  Username = request.form.get("Username")
  Password = request.form.get("Password")
  name1 = Username.upper()
  if (login_validation(Username, Password)):
    return render_template("teacherlogin.html", name=name1)
  else:
    return redirect("/login")


@app.route("/teacher_profile")
def teacher_information():
  print("here is new admission detail i am printing")
  new_Admission()
  d = teacher_info("Umesh kumbhar")
  return render_template("teacherlogin.html", name=Username, detail=d)


@app.route("/new_Admission")
def new_Admission():
  return render_template("new_Admission.html")


@app.route("/submit_admission", methods=['POST'])
def submit_admission():
  l=[]
  l.append(request.form.get("name"))
  l.appned(request.form.get("Fname"))
  l.appned(request.form.get("std"))
  l.append(request.form.get("age"))
  l.append(request.form.get("email"))
  l.append(request.form.get("course"))
  
  return redirect("/teacher_profile")

if __name__ == "__main__":
  app.run(debug=True, host='0.0.0.0')
