from flask import Flask, render_template, request, redirect, session, url_for
from database import login_validation, teacher_info, submit_new_admission, get_data, insert_data
from email_report import report_make
app = Flask(__name__)
app.secret_key = "Hind"


@app.route("/")
def welcome():
  return render_template("home.html")


@app.route("/login")
def login():
  username = session.get('username_teacher')
  if username:
    # User is already logged in, redirect to teacher_profile
    return redirect("/teacher_profile")
  else:
    return render_template("index.html")


@app.route("/submit_parent", methods=['POST'])
def submit_parent():
  Username = request.form.get("Username")
  Password = request.form.get("Password")
  if Username == 'check' and Password == '1234':
    session['username_parent'] = Username
    return "SUccessful login parent "
  else:
    return redirect("/login")
  '''
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

  if login_validation(Username, Password):
    session['username_teacher'] = Username
    return render_template("teacherlogin.html", name=name1)
  else:
    return redirect("/login")


@app.route("/teacher_profile", methods=['GET', 'POST'])
def teacher_information():
  username = session.get(
    'username_teacher')  # Retrieve the username from the session
  username = username.upper()
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


@app.route("/class_data/<class_number>")
def class_data(class_number):
  a = "Class_" + str(class_number)
  data = get_data(a)
  #return render_template("index.html", data=data)
  return render_template("class_data.html", data=data, Class=a)


@app.route("/update_scores/<Class>", methods=["POST"])
def update_scores(Class):
    for key, value in request.form.items():
        if key.startswith("math_"):
            # Extract the index and full_name from the input name
            parts = key.split("_")
            index = parts[1]
            full_name = "_".join(parts[2:])
           # print(index,full_name)
            if value.isdigit():  # Check if value is a valid integer
                math = int(value)
            else:
                math = 0  # Assign a default value if the input is not a valid integer
            
            # Perform similar validation for other subjects
            english = int(request.form[f"english_{index}_{full_name}"]) if request.form[f"english_{index}_{full_name}"].isdigit() else 0
            social_science = int(request.form[f"social_science_{index}_{full_name}"]) if request.form[f"social_science_{index}_{full_name}"].isdigit() else 0
            science = int(request.form[f"science_{index}_{full_name}"]) if request.form[f"science_{index}_{full_name}"].isdigit() else 0
            hindi = int(request.form[f"hindi_{index}_{full_name}"]) if request.form[f"hindi_{index}_{full_name}"].isdigit() else 0
            
            # Now you have the full_name, index, and scores, you can update the database
            insert_data(Class, full_name, math, english, social_science, science, hindi)
           # print(Class, full_name, math, english, social_science, science, hindi)
    return redirect(url_for("class_data", class_number=int(Class.split("_")[1])))



@app.route("/action_task/<full_name>/<Class>>", methods=["GET"])
def action_task(full_name,Class):
    # Perform the action here based on the 'full_name' parameter
    # For example, you can use 'full_name' to retrieve data from the database or perform some other task.
    
    # For demonstration purposes, let's just print the full_name
    print("Action performed for:", full_name)
    report_make(full_name,Class)
    # You can redirect to another page or return a response here if needed.
    # For example, to redirect to the class_data page:
    return redirect(url_for("class_data", class_number=int(Class.split("_")[1])))

if __name__ == "__main__":
  app.run(debug=True, host='0.0.0.0')
