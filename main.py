#DSGP Group 20 - Personality and job suitability prediction through CV and LinkedIn profile analysis

#Importing the relvant packages and libraries
import streamlit as st
import pandas as pd
import base64,random
import time,datetime
from pyresparser import ResumeParser
from pdfminer3.layout import LAParams, LTTextBox
from pdfminer3.pdfpage import PDFPage
from pdfminer3.pdfinterp import PDFResourceManager
from pdfminer3.pdfinterp import PDFPageInterpreter
from pdfminer3.converter import TextConverter
import io,random
from streamlit_tags import st_tags
from PIL import Image
import pymysql
from courses import ds_course,web_course,android_course,ios_course,uiux_course,resume_videos,interview_videos
import plotly.express as px

######################################### CREATING AND DEFINING FUNCTIONS ########################################
def pdf_reader(file):
    # Create a PDF resource manager to store shared resources
    resource_manager = PDFResourceManager()

    # Create a StringIO object to hold the text content of the PDF
    fake_file_handle = io.StringIO()

    # Create a TextConverter object to convert PDF pages to text
    # Pass in the PDF resource manager, the StringIO object, and some layout parameters
    converter = TextConverter(resource_manager, fake_file_handle, laparams=LAParams())

    # Create a PDF page interpreter to interpret PDF pages
    # Pass in the PDF resource manager and the TextConverter object
    page_interpreter = PDFPageInterpreter(resource_manager, converter)

    # Open the PDF file in binary read mode and loop through each page
    with open(file, 'rb') as fh:
        # Loop through each page in the PDF
        for page in PDFPage.get_pages(fh, caching=True, check_extractable=True):
            # Process each PDF page with the page interpreter
            page_interpreter.process_page(page)

        # Retrieve the text content of the PDF from the StringIO object
        text = fake_file_handle.getvalue()

    # Close the converter and StringIO objects
    converter.close()
    fake_file_handle.close()

    # Return the text content of the PDF
    return text

def show_pdf(file_path):
    # Open the PDF file in binary read mode
    with open(file_path, "rb") as f:
        # Read the contents of the file and encode it as base64
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')

    # Embed the base64-encoded PDF in an HTML iframe element
    pdf_display = F'<iframe src="data:application/pdf;base64,{base64_pdf}" width="500" height="700" type="application/pdf"></iframe>'

    # Display the PDF in Streamlit using the HTML iframe element
    st.markdown(pdf_display, unsafe_allow_html=True)


def get_table_download_link(df, filename, text):
    """
    Generates a link allowing the data in a given pandas dataframe to be downloaded as a CSV file
    :param df: pandas dataframe to be downloaded
    :param filename: filename to be used for the downloaded file
    :param text: text to be used for the link
    :return: href string for downloading the CSV file
    """
    # Convert the pandas dataframe to a CSV string
    csv = df.to_csv(index=False)

    # Encode the CSV string as base64
    b64 = base64.b64encode(csv.encode()).decode()

    # Create an HTML link with the base64-encoded CSV string as the href
    # The link is given a filename and text to display on the page
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">{text}</a>'

    # Return the HTML link
    return href

def insert_data(name, email, res_score, timestamp, no_of_pages, reco_field, cand_level, skills, recommended_skills,courses):
    'Function to insert user data into the user_data database table'

    # Define the name of the database table where the data will be stored
    DB_table_name = 'user_data'

    # Define the SQL statement for inserting the data into the table
    insert_sql = "insert into " + DB_table_name + """ values (0,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""" #Make sure to add 2 new columns for score and personality

    # Create a tuple of values to be inserted into the table
    rec_values = (
    name, email, str(res_score), timestamp, str(no_of_pages), reco_field, cand_level, skills, recommended_skills,
    courses)

    # Execute the SQL statement and commit the changes to the database
    cursor.execute(insert_sql, rec_values)
    connection.commit()
    

### Resume score generation based on the Required skills and the skills the candidate has
st.subheader("**Resume Score💡**")

# The required skill sets for each job role
data_scientist_required_skills = ['r', 'python', 'machine learning', 'deep learning', 'sql', 'nosql',
                                  'statistics', 'big data analytics', 'artificial intelligence', 'java', 'rstudio',
                                  'mathematics', 'hadoop', 'aws', 'cloud computing', 'data pipelines', 'sas',
                                  'apache spark', 'pig', 'hive', 'google cloud platform ', 'html', 'css', 'javascript',
                                  'data mining', 'data wrangling', 'data visualization', 'data analysis', 'data management',
                                  'data mining', 'data processing', 'software development', 'algorithms',
                                  'natural language processing', 'etl', 'perl', 'scala', 'mongodb',
                                  'probability', 'tableau', 'power bi', 'qlikview', 'd3.js', 'git',
                                  'knime', 'business', 'matlab', 'critical thinking', 'decision making',
                                  'teamwork', 'leadership', 'problem solving', 'communication', 'adaptability']

software_engineer_required_skills = ['oop', 'python', 'java', 'c++', 'csharp', 'ood', 'flask', 'html',
                                     'css', 'javascript',  'flutter', 'javafx', 'machine learning', 'ruby',
                                     'c', 'communication', 'leadership', 'scala', 'powershell', 'php',
                                     'xml', 'react', 'angular', 'mongodb', 'mysql', 'nosql', 'git', 'junit', 'aws',
                                     'google cloud platform', 'slack', 'trello', 'asana', 'jenkins', 'circlecl',
                                     'visual studio code', 'maven', 'decision making', 'critical thinking',
                                     'problem solving', 'gitlab', 'docker', 'kafka', 'postgresql', 'elasticsearch']

uiux_developer_required_skills = ['ux', 'adobe xd', 'figma', 'zeplin', 'balsamiq', 'ui', 'prototyping',
                                  'wireframes', 'storyframes', 'adobe photoshop', 'photoshop',
                                  'editing', 'adobe illustrator', 'illustrator', 'adobe after effects',
                                  'after effects', 'adobe premier pro', 'adobe indesign',
                                  'indesign', 'wireframe', 'solid', 'grasp', 'user research', 'css', 'html',
                                  'javascript', 'sketch', 'adobe xd', 'slack', 'asana', 'jira', 'hotjar',
                                  'user experience']

web_developer_required_skills = ['react', 'django', 'node jS', 'react js', 'php', 'laravel', 'magento',
                                 'wordpress', 'javascript', 'angular js', 'c#', 'flask']

mobile_app_developer_required_skills = ['android', 'android development', 'flutter', 'kotlin', 'xml',
                                        'kivy', 'ios', 'ios development', 'swift', 'cocoa',
                                        'cocoa touch', 'xcode']
# Assigning the number of skills the candidate has and percentage resume score to zero initially
number_of_skills = 0
percentage_resume_score = 0
# Finding the number of skills in the skill lists for each job role and assigning them to variables
number_of_required_skills_data_scientist = len(data_scientist_required_skills)
number_of_required_skills_software_engineer = len(software_engineer_required_skills)
number_of_required_skills_uiux_developer = len(uiux_developer_required_skills)
number_of_required_skills_web_developer = len(web_developer_required_skills)
number_of_required_skills_mobile_app_developer = len(mobile_app_developer_required_skills)
# Calculating the resume score percentage for each job role based on the required skills
# data scientist job role score calculation
if selected_field == 'Data Science':
    # checking each skill extracted during the resume analysis
    for skills in resume_data['skills']:
        # checking whether the skill extracted from the resume is in the list of required skills for data science job role
        if skills.lower() in data_scientist_required_skills:
            # if so adding 1 to the number of skills
            number_of_skills = number_of_skills + 1

        else:
            # if the skill is not in the list of the required skills continue
            number_of_skills = number_of_skills
    # Calculating the percentage resume score
    percentage_resume_score = (number_of_skills / number_of_required_skills_data_scientist) * 100

# software engineer job role score calculation
elif selected_field == 'Software Engineer':
    # checking each skill extracted during the resume analysis
    for skills in resume_data['skills']:
        # checking whether the skill extracted from the resume is in the list of required skills for software engineer job role
        if skills.lower() in software_engineer_required_skills:
            # if so adding 1 to the number of skills
            number_of_skills = number_of_skills + 1
        else:
            # if the skill is not in the list of the required skills continue
            number_of_skills = number_of_skills
    # Calculating the percentage resume score
    percentage_resume_score = (number_of_skills / number_of_required_skills_software_engineer) * 100
# web developer job role score calculation
elif selected_field == 'Web Development':
    # checking each skill extracted during the resume analysis
    for skills in resume_data['skills']:
        # checking whether the skill extracted from the resume is in the list of required skills for web development job role
        if skills.lower() in web_developer_required_skills:
            # if so adding 1 to the number of skills
            number_of_skills = number_of_skills + 1
        else:
            # if the skill is not in the list of the required skills continue
            number_of_skills = number_of_skills
    # Calculating the percentage resume score
    percentage_resume_score = (number_of_skills / number_of_required_skills_web_developer) * 100

#  UI-UX Development job role score calculation
elif selected_field == 'UI-UX Development':
    # checking each skill extracted during the resume analysis
    for skills in resume_data['skills']:
        # checking whether the skill extracted from the resume is in the list of required skills for ui/ux development job role
        if skills.lower() in uiux_developer_required_skills:
            # if so adding 1 to the number of skills
            number_of_skills = number_of_skills
        else:
            # if the skill is not in the list of the required skills continue
            number_of_skills = number_of_skills
    # Calculating the percentage resume score
    percentage_resume_score = (number_of_skills / number_of_required_skills_uiux_developer) * 100
#  mobile app developer job role score calculation
elif selected_field == 'Mobile-App Development':
    # checking each skill extracted during the resume analysis
    for j in resume_data['skills']:
        # checking whether the skill extracted from the resume is in the list of required skills for mobile app development job role
        if j.lower() in mobile_app_developer_required_skills:
            # if so adding 1 to the number of skills
            number_of_skills = number_of_skills + 1
        else:
            # if the skill is not in the list of the required skills continue
            number_of_skills = number_of_skills
    # Calculating the percentage resume score
    percentage_resume_score = (number_of_skills / number_of_required_skills_mobile_app_developer) * 100
