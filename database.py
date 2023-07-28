import mysql.connector
import os

db_host = os.environ['DB_HOST']
db_user = os.environ['DB_USER']
db_password = os.environ['DB_PASSWORD']

try:
  mydb = mysql.connector.connect(host=db_host,
                                 user=db_user,
                                 password=db_password)
  cursor = mydb.cursor()
except Exception as e:
  print(e)


def login_validation(Username, Password):

  query = "select * from project_database.login_detail where Username like '{}' and Password like '{}'".format(
    Username, Password)
  cursor.execute(query)
  myresult = cursor.fetchall()
  if (len(myresult) > 0):
    return True
  else:
    return False


def teacher_info(teacher):

  query = "select * from project_database.teacher_info where Name='{}'".format(
    teacher)
  cursor.execute(query)
  result = cursor.fetchone()
  print("result", result)
  return result


def submit_new_admission(t):

  Class_Admission(t)

  query = "insert into project_database.student_info(full_name,Father_name,Class,P_Username,Password,Email,AdmittedBy) values (%s,%s,%s,%s,%s,%s,%s)"

  cursor.execute(query, t)
  mydb.commit()


def Class_Admission(t):
  a = "Class_" + t[2]
  query = "insert into {} (full_name, math, english, social_science, science, hindi) values ('{}','{}','{}','{}','{}','{}')".format(
    a, t[0], 0, 0, 0, 0, 0)
  cursor.execute(query)
  mydb.commit()
  
def insert_data(a,full_name, math, english, social_science, science, hindi):
  query ="UPDATE {} SET math={}, english={}, social_science={}, science={}, hindi={} WHERE full_name='{}'".format(a,math, english, social_science, science, hindi, full_name)
  cursor.execute(query)
  mydb.commit()
  

def get_data(a):
  #a = "Class_" + str(9)
  query = "select * from project_database.{}".format(a)
  cursor.execute(query)
  result = cursor.fetchall()
  return result
