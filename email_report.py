import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase  
from email import encoders 
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
def generate_student_report(sender_email, sender_password, recipient_email, student_name,Class_name):
    # Sample data as a DataFrame (Already provided in the 'df' variable)
    # Assuming you have the DataFrame 'df' containing the data as shown below:
    # df = pd.DataFrame({...})

    # Your code to retrieve the data from the database and perform necessary calculations goes here...
    # For simplicity, I'm just initializing a DataFrame with some sample data.
    
   
    query="select * from project_database.{}".format(Class_name)
    print("coming to you *****")
    df=pd.read_sql(query,mydb)
    print("Readed ******")
    df['Total'] = df.iloc[:, 1:].sum(axis=1)
    df["Average"]=df['Total']/5
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
    # Function to prepare the report content
    def prepare_report(student_name):
        student_data = df[df['full_name'] == student_name].squeeze()

        report_content = f"Student Name: {student_data['full_name']}\n" \
                         f"Date of Birth: {student_data['DateOfBirth']}\n" \
                         f"Total Marks: {student_data['Total']}\n" \
                         f"Average Marks: {student_data['Average']}\n" \
                         f"Highest Marks: {student_data['Highest']}\n" \
                         f"Lowest Marks: {student_data['Lowest']}\n" \
                         f"Pass/Fail: {student_data['Pass/Fail']}\n" \
                         f"Category: {student_data['Category']}\n" \
                         f"Rank: {int(student_data['Rank'])}\n"

        return report_content

    # Function to create the comparison graph for a student's marks with class average marks in each subject
    def create_comparison_graph(student_name):
        fig, ax = plt.subplots(figsize=(8, 5))
        subject_names = ['math', 'english', 'social_science', 'science', 'hindi']

        # Get the student's marks in each subject
        student_marks = df[df['full_name'] == student_name][subject_names].squeeze()

        # Calculate the class average marks in each subject
        class_avg_marks = df[subject_names].mean()

        # Plot the comparison bar graph
        bar_width = 0.35
        bar_positions = range(len(subject_names))
        ax.bar(bar_positions, student_marks, width=bar_width, color='skyblue', label='Student Marks')
        ax.bar([pos + bar_width for pos in bar_positions], class_avg_marks, width=bar_width, color='lightcoral', label='Class Average')

        # Add numeric values on top of the bars
        for i, (student_mark, class_avg_mark) in enumerate(zip(student_marks, class_avg_marks)):
            ax.text(i, student_mark + 5, str(student_mark), ha='center', va='bottom', fontweight='bold', color='black')
            ax.text(i + bar_width, class_avg_mark + 5, str(class_avg_mark), ha='center', va='bottom', fontweight='bold', color='black')

        ax.set_xticks([pos + bar_width / 2 for pos in bar_positions])
        ax.set_xticklabels([subject.upper() for subject in subject_names])  # Convert subject names to uppercase
        ax.set_xlabel('Subjects')
        ax.set_ylabel('Marks')
        ax.set_title('Student Marks vs Class Average', fontweight='bold')  # Set title in bold
        ax.legend()
        plt.tight_layout()

        return fig

    # Function to create the PDF report
    def create_pdf_report(student_name):
        report_content = prepare_report(student_name)

        # Create a BytesIO buffer to hold the PDF
        buffer = BytesIO()

        c = canvas.Canvas(buffer, pagesize=letter)

        c.setFont("Helvetica", 12)
        c.drawString(100, 700, "Student Report")

        # Split the report_content into separate lines and draw each line separately
        lines = report_content.split('\n')
        y_position = 670
        for line in lines:
            c.setFont("Helvetica", 10)
            c.drawString(100, y_position, line)
            y_position -= 20  # Adjust the y-position for the next line

        # Draw the student's marks comparison graph directly on the PDF
        fig = create_comparison_graph(student_name)

        # Save the figure as an image in-memory
        img_buffer = BytesIO()
        fig.savefig(img_buffer, format='png')
        img_buffer.seek(0)

        # Draw the image on the PDF
        img = ImageReader(img_buffer)
        c.drawImage(img, 100, 250, width=400, height=250)

        c.save()

        # Move the buffer pointer to the beginning of the buffer
        buffer.seek(0)
        return buffer

    # Function to send the email with the report as an attachment
    def send_report_email(sender_email, sender_password, recipient_email, subject, message, student_name, pdf_buffer):
        # Create a multipart message object
        msg = MIMEMultipart()

        # Set the sender, recipient, and subject
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject

        # Add the message body
        msg.attach(MIMEText(message, 'plain'))

        # Create a MIMEBase object with 'application/pdf' as the content type
        pdf_attachment = MIMEBase('application', 'pdf')
        pdf_attachment.set_payload(pdf_buffer.getvalue())

        # Encode the PDF content using Base64
        encoders.encode_base64(pdf_attachment)

        # Add necessary headers for the attachment
        pdf_attachment.add_header('Content-Disposition', f'attachment; filename={student_name}_report.pdf')
        msg.attach(pdf_attachment)

        # Create an SMTP connection
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            # Start the TLS encryption
            server.starttls()

            # Login to the email account
            server.login(sender_email, sender_password)

            # Send the email
            server.send_message(msg)

    # Generate the report content
    #report_content = prepare_report(student_name)

    # Generate the PDF report
    pdf_buffer = create_pdf_report(student_name)

    # Send the email with the report as an attachment
    subject = 'Student Report'
    message = f'Dear Parent,\n\nPlease find attached the report of {student_name}.\n\nThank you.\nSchool Administration'
    send_report_email(sender_email, sender_password, recipient_email, subject, message, student_name, pdf_buffer)

# Call the function to send the email with the report for "Rohit Vilas"


def report_make(full_name,Class_name):
    sender_email = 'rohitbhalode@gmail.com'
    sender_password = 'tzdfsoqlvyuvwvcm'
    recipient_email = 'rohitbhalode@gmail.com'
    generate_student_report(sender_email, sender_password, recipient_email, full_name,Class_name)
    