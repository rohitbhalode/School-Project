
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
import mysql.connector
import os
from matplotlib.backends.backend_pdf import PdfPages
from df_creation import create_df
import pandas as pd
import io
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
    df=create_df(Class_name)
    def prepare_report(student_name):
        student_data = df[df['full_name'] == student_name].squeeze()
        average_marks_rounded = round(student_data['Average'], 2)
        has_passed_subjects = all(student_data[subject] >= 40 for subject in ['math', 'english', 'social_science', 'science', 'hindi'])

    # Determine pass/fail status and set the style for pass/fail text
        pass_fail_status = 'Pass' if (student_data['Average'] >= 40 and has_passed_subjects) else 'Fail'
       
        report_content = f"Student Name: {student_data['full_name']}\n" \
                         f"Date of Birth: {student_data['DateOfBirth']}\n" \
                         f"Total Marks: {student_data['Total']}\n" \
                         f"Percentage Marks: {average_marks_rounded}\n" \
                         f"Highest Marks: {student_data['Highest']}\n" \
                         f"Lowest Marks: {student_data['Lowest']}\n" \
                         f"Pass/Fail: {pass_fail_status}\n" \
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
        class_avg_marks = df[subject_names].mean().round(2)

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
    sender_password = os.environ['Email_pwd']
    #recipient_email = 'rohitbhalode@gmail.com'
    query="select * from student_info where full_name='{}'".format(full_name)
    cursor.execute(query)
    r=cursor.fetchall()[0][4]
    generate_student_report(sender_email, sender_password, r, full_name, Class_name)

        
def create_report_pdf(df):
    # Sort the DataFrame by Total in descending order to get the top three students
    top_three_students = df.nlargest(3, 'Total')

    # Calculate pass/fail counts
    pass_fail_counts = df['Pass/Fail'].value_counts().to_dict()

    # Create a BytesIO object to hold the PDF data
    pdf_io = io.BytesIO()

    # Create the PDF using PdfPages and save it to the BytesIO object
    with PdfPages(pdf_io) as pdf_pages:
        # Plot 1: Average Marks of Students
        plt.figure(figsize=(10, 5))
        plt.bar(df['full_name'], df['Average'])
        plt.xlabel('Student Name')
        plt.ylabel('Average Marks')
        plt.title('Average Marks of Students')
        plt.xticks(rotation=45)
        plt.tight_layout()
        pdf_pages.savefig()
        plt.close()

        # Plot 2: Top Three Students - Total Marks
        top_three_colors = ['#ff4757', '#ffa801', '#2ed573']
        plt.figure(figsize=(5, 5))
        plt.bar(top_three_students['full_name'], top_three_students['Total'], color=top_three_colors)
        plt.xlabel('Student Name')
        plt.ylabel('Total Marks')
        plt.title('Top Three Students - Total Marks')
        plt.xticks(rotation=45)
        plt.tight_layout()
        pdf_pages.savefig()
        plt.close()

        # Plot 3: Subject-wise Total Marks Distribution
        subject_totals = df.iloc[:, 1:6].sum()
        subject_wise_total_df = pd.DataFrame(subject_totals, columns=['Total Marks'])
        subject_wise_total_df.reset_index(inplace=True)
        subject_wise_total_df.rename(columns={'index': 'Subject'}, inplace=True)

        plt.figure(figsize=(8, 8))
        plt.pie(subject_wise_total_df['Total Marks'], labels=subject_wise_total_df['Subject'], autopct='%1.1f%%', startangle=140)
        plt.title('Subject-wise Total Marks Distribution')
        plt.axis('equal')  # Equal aspect ratio ensures the pie chart is circular.
        plt.tight_layout()
        pdf_pages.savefig()
        plt.close()

        # Plot 4: Pass/Fail Bar Graph
        plt.figure(figsize=(6, 4))
        plt.bar(pass_fail_counts.keys(), pass_fail_counts.values())
        plt.xlabel('Status')
        plt.ylabel('Count')
        plt.title('Pass/Fail Counts')
        plt.tight_layout()
        pdf_pages.savefig()
        plt.close()

    # Reset the BytesIO object's position to the beginning
    pdf_io.seek(0)

    # Return the PDF data as bytes
    return pdf_io.read()