import mysql.connector

try:
  mydb = mysql.connector.connect(
    host="aws.connect.psdb.cloud",
    user="nth8yfh32jqrgzpfei1m",
    password="pscale_pw_DWPpEEW0u9dvuH5V8wJlZmos1pqfOeFIoAurrlijNaS")
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
  query="insert into Student_info(S_Name,F_Name,Class,Course,P_Username,Password) values (%s,%s,%s,%s,%s,%s)"

  cursor.execute(query,t)
  mydb.commit()


