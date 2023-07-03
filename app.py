from flask import Flask, render_template, request, redirect, session, url_for
from database import login_validation, teacher_info, submit_new_admission, Class_select

app = Flask(__name__)
app.secret_key = "your_secret_key"


@app.route("/")
def welcome():
  return render_template("home.html")


@app.route("/login")
def login():
  username = session.get('username')
  if username:
    # User is already logged in, redirect to teacher_profile
    return redirect("/teacher_profile")
  else:
    return render_template("index.html")


@app.route("/submit", methods=['POST'])
def result():
  Username = request.form.get("Username")
  Password = request.form.get("Password")
  name1 = Username.upper()

  if login_validation(Username, Password):
    session['username'] = Username
    return render_template("teacherlogin.html", name=name1)
  else:
    return redirect("/login")


'''
@app.route("/submit", methods=['POST'])
def result():
  Username = request.form.get("Username")
  Password = request.form.get("Password")
  name1 = Username.upper()
  if (login_validation(Username, Password)):
    session['username'] = Username
    return render_template("teacherlogin.html", name=name1)
  else:
    return redirect("/login")

'''


@app.route("/teacher_profile", methods=['GET', 'POST'])
def teacher_information():
  username = session.get('username')  # Retrieve the username from the session
  if username:
    d = teacher_info("Umesh kumbhar")
    return render_template("teacherlogin.html", name=username, detail=d)
  else:
    return redirect("/login")


@app.route("/logout")
def logout():
  session.clear()
  return redirect("/login")


@app.route("/new_Admission")
def new_Admission():
  return render_template("new_Admission.html")


@app.route("/submit_admission", methods=['POST'])
def submit_admission():
  form_elements = list(request.form.values())
  submit_new_admission(form_elements)
  return redirect("/teacher_profile")


@app.route("/class_data/<int:class_number>")
def class_data(class_number):
  print(class_number)
  a = "Class_" + str(class_number)
  result = Class_select(a)
  return render_template("class_data.html", data=result)


if __name__ == "__main__":
  app.run(debug=True, host='0.0.0.0')
