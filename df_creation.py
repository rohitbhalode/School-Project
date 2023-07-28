import pandas as pd
import os
import mysql.connector

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

def create_df(Class_name):
    query="select * from project_database.{}".format(Class_name)
    
    df=pd.read_sql(query,mydb)
  
    df['Total'] = df.iloc[:, 1:].sum(axis=1)
    df["Average"]=df['Total']/5
    df['Average']=df['Average'].round(2)
    df['Pass/Fail'] = df['Average'].apply(lambda x: 'Pass' if x >= 40 else 'Fail')
    df['DateOfBirth']='01/01/2001'
    def get_category(average_marks):
        if average_marks >= 80:
            return 'A'
        elif average_marks >= 65:
            return 'B'
        elif average_marks >= 40:
            return 'C'
        else:
            return 'Fail'

    df['Category'] = df['Average'].apply(get_category)
    df['Rank'] = df['Total'].rank(ascending=False, method='min')
    df['Highest'] = df.iloc[:, 1:6].max(axis=1)
    df['Lowest'] = df.iloc[:, 1:6].min(axis=1)
    return df

