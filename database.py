import mysql.connector

try:
  mydb = mysql.connector.connect(
    host="aws.connect.psdb.cloud",
    user="bbhh9tfvizntvohsl6qa",
    password="pscale_pw_W3NeI5EiDIyT4cpNu8wkV74e9uSktsev7k4rn9STRrQ")
  cursor = mydb.cursor()
  print("connection successfully", mydb)
except Exception as e:
  print(e)


def login_validation(Username, Password):

  query = "select * from login_detail where Username like '{}' and Password like '{}'".format(
    Username, Password)
  cursor.execute(query)
  myresult = cursor.fetchall()
  if (len(myresult) > 0):
    return True
  else:
    return False


def teacher_info(teacher):

  query = "select * from teacher_info where Name='{}'".format(teacher)
  cursor.execute(query)
  result = cursor.fetchone()
  print("result", result)
  return result


def submit_new_admission(t):

  Class_Admission(t)

  query = "insert into Student_info(S_Name,F_Name,Class,Course,P_Username,Password,Email,AdmittedBy) values (%s,%s,%s,%s,%s,%s,%s,%s)"

  cursor.execute(query, t)
  mydb.commit()


def Class_Admission(t):
  a = "Class_" + t[2]
  query = "insert into {} (S_Name,Fname, Course,AdmittedBy) values ('{}','{}','{}','{}')".format(
    a, t[0], t[1], t[-2], t[-1])
  cursor.execute(query)
  mydb.commit()


def Class_select(a):
  #a = "Class_" + str(9)
  query = "select * from {}".format(a)
  cursor.execute(query)
  result = cursor.fetchall()
  return result
