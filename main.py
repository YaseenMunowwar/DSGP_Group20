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

def course_recommender(course_list):
    'Function to suggest relevant courses'
    # Add a subheading for the course recommendations
    st.subheader("*Courses & Certificates🎓 Recommendations*")

    # Initialize a counter and an empty list for the recommended courses
    c = 0
    rec_course = []

    # Display a slider for the user to choose the number of course recommendations
    no_of_reco = st.slider('Choose Number of Course Recommendations:', 1, 10, 4)

    # Shuffle the list of courses randomly
    random.shuffle(course_list)

    # Iterate over the list of courses and display the recommended courses
    for c_name, c_link in course_list:
        c += 1
        # Display the name and link for each course
        st.markdown(f"({c}) [{c_name}]({c_link})")

        # Add the name of the recommended course to the list of recommended courses
        rec_course.append(c_name)

        # Break the loop when the desired number of recommendations has been displayed
        if c == no_of_reco:
            break

    # Return the list of recommended courses
    return rec_course

def course_reco(course_df):
    #Function to suggest relevant courses
    # Add a subheading for the course recommendations
    st.subheader("*Courses & Certificates🎓 Recommendations*")

    # Initialize a counter and an empty list for the recommended courses
    c = 0
    rec_course = []

    # Add filters to the course dataframe
    category = st.multiselect('Select categories:', course_df['category'].unique())
    course_df = course_df[course_df['category'].isin(category)]
    difficulty = st.multiselect('Select difficulty levels:', course_df['difficulty'].unique())
    course_df = course_df[course_df['difficulty'].isin(difficulty)]
    # You can add more filters as per your requirement.

    # Display a slider for the user to choose the number of course recommendations
    no_of_reco = st.slider('Choose Number of Course Recommendations:', 1, 10, 4)

    # Shuffle the filtered dataframe randomly
    course_df = course_df.sample(frac=1).reset_index(drop=True)

    # Iterate over the filtered dataframe and display the recommended courses
    for i in range(no_of_reco):
        # Display the name and link for each course
        c_name = course_df['name'][i]
        c_link = course_df['link'][i]
        st.markdown(f"({i+1}) [{c_name}]({c_link})")

        # Add the name of the recommended course to the list of recommended courses
        rec_course.append(c_name)

    # Return the list of recommended courses
    return rec_course
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
    
def skill_percentage(required_skills,all_skills):
    'Function to generate a percentage of the candidates skills'
    num_skills = 0
    for skill in required_skills:
        skill = skill.lower()
        if skill in all_skills:
            num_skills += 1
    percentage = num_skills / len(required_skills) * 100
    print(f"The candidate has {percentage:.2f}% of the required skills.")
    st.write(f"The candidate has {percentage:.2f}% of the required skills.")
    return percentage;

def skill_recommender(required_skills,all_skills):
    'Function to recommend skills analyzing the available skills'
    recommended_skills = []
    for skill in required_skills:
        skill = skill.lower()
        if skill in all_skills:
            pass
        else:
            recommended_skills.append(skill)
    return recommended_skills

def score_visualizer(resume_score):
    'Function to visualize the score bar'
    resume_score = int(resume_score)
    my_bar = st.progress(0)
    score = 0
    for percent_complete in range(resume_score):
        score += 1
        time.sleep(0.1)
        my_bar.progress(percent_complete + 1)


def normal_user():
    # Function to create the functionality of the applicant

    'Function to create a dropdown to select the user job role'
    # Define the job roles and user option
    job_roles = ["Choose your job role", "Data Scientist", "Software Engineer", "Web Developer",
                 "Mobile App Developer", "UI/UX Engineer"]
    # Add a dropdown to select a job role
    selected_job_role = st.selectbox("Select your job role", job_roles, index=0, key='job_role_selection')

    # Upload user's resume
    user_resume = st.file_uploader("Choose your Resume", type=["pdf"])
    # If user's resume is uploaded
    if user_resume is not None:
        # Save the uploaded resume
        with st.spinner('Uploading your Resume....'):
            time.sleep(2)
        save_image_path = './Uploaded_Resumes/' + user_resume.name
        with open(save_image_path, "wb") as f:
            f.write(user_resume.getbuffer())

        # Show the uploaded resume
        show_pdf(save_image_path)

        # Extract resume data and skills from the first resume
        resume_data = ResumeParser(save_image_path).get_extracted_data()
        if resume_data:
            resume_text = pdf_reader(save_image_path)
            resume_data_1_skills = resume_data['skills']

    # Upload user's LinkedIn CV
    Linkedin_cv = st.file_uploader("Choose Your LinkedIn CV", type=["pdf"])
    cover_letter = st.text_area("Please enter you Cover Letter", height=200)
    if Linkedin_cv is not None and cover_letter.strip() != "":
        # Save the uploaded LinkedIn CV
        save_image_path_2 = './Uploaded_Resumes/' + Linkedin_cv.name
        with open(save_image_path_2, "wb") as f:
            f.write(Linkedin_cv.getbuffer())

        # Show the uploaded LinkedIn CV
        show_pdf(save_image_path_2)


    # Extract skills from the second resume
        resume_data_2 = ResumeParser(save_image_path_2).get_extracted_data()
        if resume_data_2:
            resume_data_2_skills = resume_data_2['skills']

            # Combine the skills from both resumes into a single list
            all_skills = resume_data_1_skills + resume_data_2_skills

            # Remove the duplicates in the combined skill list
            all_skills = list(set(all_skills))

            # Convert all skills to lowercase
            all_skills = [skill.lower() for skill in all_skills]

            # Remove the duplicates in the combined skill list
            all_skills = list(set(all_skills))


            # Display resume analysis
            st.header("**Resume Analysis**")
            st.success("Hello " + resume_data['name'])
            st.subheader("**Your Basic info**")
            try:
                st.text('Name: ' + resume_data['name'])
                st.text('Email: ' + resume_data['email'])
                st.text('Resume pages: ' + str(resume_data['no_of_pages']))
            except:
                st.text("Same CV uploaded")
                normal_user()  # recursively call the function if the same CV is uploaded again

            #Use the candidate level to get the suitability percentage
            cand_level = ''
            if resume_data['no_of_pages'] == 1:
                cand_level = "Fresher"
                st.markdown('''<h4 style='text-align: left; color: #d73b5c;'>You are looking Fresher.</h4>''',
                            unsafe_allow_html=True)
            elif resume_data['no_of_pages'] == 2:
                cand_level = "Intermediate"
                st.markdown('''<h4 style='text-align: left; color: #1ed760;'>You are at intermediate level!</h4>''',
                            unsafe_allow_html=True)
            elif resume_data['no_of_pages'] >= 3:
                cand_level = "Experienced"
                st.markdown('''<h4 style='text-align: left; color: #fba171;'>You are at experience level!''',
                            unsafe_allow_html=True)

            # Display the combined list of skills in the st_tags widget
            keywords = st_tags(label='### Skills that you have',
                               text='See our skills recommendation',
                               value=all_skills, key='1')

            cover_letter = st.text_area("Cover Letter", height=200)
            if (selected_job_role == "Data Scientist"):
                # Data science recommendations
                data_scientist_required_skills = ['r', 'python', 'machine learning', 'deep learning', 'sql', 'nosql',
                                                  'statistics', 'big data analytics', 'artificial intelligence', 'java',
                                                  'rstudio',
                                                  'mathematics', 'hadoop', 'aws', 'cloud computing', 'data pipelines',
                                                  'sas',
                                                  'apache spark', 'pig', 'hive', 'google cloud platform ', 'html',
                                                  'css', 'javascript',
                                                  'data mining', 'data wrangling', 'data visualization',
                                                  'data analysis', 'data management',
                                                  'data mining', 'data processing', 'software development',
                                                  'algorithms',
                                                  'natural language processing', 'etl', 'perl', 'scala', 'mongodb',
                                                  'probability', 'tableau', 'power bi', 'qlikview', 'd3.js', 'git',
                                                  'knime', 'business', 'matlab', 'critical thinking', 'decision making',
                                                  'teamwork', 'leadership', 'problem solving', 'communication',
                                                  'adaptability']
                resume_score = skill_percentage(data_scientist_required_skills,all_skills)
                score_visualizer(resume_score)
                recommended_skills = skill_recommender(data_scientist_required_skills, all_skills)
                recommended_keywords = st_tags(label='### Recommended skills for you.',
                                               text='Recommended skills generated from System',
                                               value=recommended_skills, key='2')
                st.write(f"Selected job role: {selected_job_role}")
                rec_course = course_recommender(ds_course)

            elif (selected_job_role == "Software Engineer"):
                # Software Engineer recommendations
                software_engineer_required_skills = ['oop', 'python', 'java', 'c++', 'csharp', 'ood', 'flask', 'html',
                                                     'css', 'javascript', 'flutter', 'javafx', 'machine learning',
                                                     'ruby',
                                                     'c', 'communication', 'leadership', 'scala', 'powershell', 'php',
                                                     'xml', 'react', 'angular', 'mongodb', 'mysql', 'nosql', 'git',
                                                     'junit', 'aws',
                                                     'google cloud platform', 'slack', 'trello', 'asana', 'jenkins',
                                                     'circlecl',
                                                     'visual studio code', 'maven', 'decision making',
                                                     'critical thinking',
                                                     'problem solving', 'gitlab', 'docker', 'kafka', 'postgresql',
                                                     'elasticsearch']

                resume_score = skill_percentage(software_engineer_required_skills, all_skills)
                score_visualizer(resume_score)
                recommended_skills = skill_recommender(software_engineer_required_skills, all_skills)
                recommended_keywords = st_tags(label='### Recommended skills for you.',
                                               text='Recommended skills generated from System',
                                               value=recommended_skills, key='3')
                st.write(f"Selected job role: {selected_job_role}")
                #rec_course = course_recommender(software_course)

            elif (selected_job_role == "Web Developer"):
                # Web Developer recommendations
                web_developer_required_skills = ['react', 'django', 'node jS', 'react js', 'php', 'laravel', 'magento',
                                                 'wordpress', 'javascript', 'angular js', 'c#', 'flask']
                resume_score = skill_percentage(web_developer_required_skills, all_skills)
                score_visualizer(resume_score)
                recommended_skills = skill_recommender(web_developer_required_skills, all_skills)
                recommended_keywords = st_tags(label='### Recommended skills for you.',
                                               text='Recommended skills generated from System',
                                               value=recommended_skills, key='3')
                st.write(f"Selected job role: {selected_job_role}")
                rec_course = course_recommender(web_course)

            elif (selected_job_role == "Mobile App Developer"):
                # Mobile App Developer recommendations
                mobile_app_developer_required_skills = ['android', 'android development', 'flutter', 'kotlin', 'xml',
                                                        'kivy', 'ios', 'ios development', 'swift', 'cocoa',
                                                        'cocoa touch', 'xcode']
                resume_score = skill_percentage(mobile_app_developer_required_skills, all_skills)
                score_visualizer(resume_score)
                recommended_skills = skill_recommender(mobile_app_developer_required_skills, all_skills)
                recommended_keywords = st_tags(label='### Recommended skills for you.',
                                               text='Recommended skills generated from System',
                                               value=recommended_skills, key='3')
                st.write(f"Selected job role: {selected_job_role}")
                rec_course = course_recommender(android_course)

            elif (selected_job_role == "UI/UX Engineer"):
                # UI/UX Engineer recommendations

                uiux_developer_required_skills = ['ux', 'adobe xd', 'figma', 'zeplin', 'balsamiq', 'ui', 'prototyping',
                                                  'wireframes', 'storyframes', 'adobe photoshop', 'photoshop',
                                                  'editing', 'adobe illustrator', 'illustrator', 'adobe after effects',
                                                  'after effects', 'adobe premier pro', 'adobe indesign',
                                                  'indesign', 'wireframe', 'solid', 'grasp', 'user research', 'css',
                                                  'html',
                                                  'javascript', 'sketch', 'adobe xd', 'slack', 'asana', 'jira',
                                                  'hotjar',
                                                  'user experience']

                resume_score = skill_percentage(uiux_developer_required_skills, all_skills)
                score_visualizer(resume_score)
                recommended_skills = skill_recommender(uiux_developer_required_skills, all_skills)
                recommended_keywords = st_tags(label='### Recommended skills for you.',
                                               text='Recommended skills generated from System',
                                               value=recommended_skills, key='3')
                st.write(f"Selected job role: {selected_job_role}")
                rec_course = course_recommender(uiux_course)

            ## Insert into table
            ts = time.time()
            cur_date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
            cur_time = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
            timestamp = str(cur_date + '_' + cur_time)

            ### Resume writing recommendation
            st.subheader("**Resume Tips & Ideas💡**")

            st.subheader("**Resume Score📝**")
            st.markdown(
                """
                <style>
                    .stProgress > div > div > div > div {
                        background-color: #d73b5c;
                    }
                </style>""",
                unsafe_allow_html=True,
            )

            data = pd.read_csv("mbti_1.csv")
            data = data.join(data.apply(lambda row: get_types(row), axis=1))

            list_personality_bin = np.array([translate_personality(p) for p in data.type])

            list_posts, list_personality = pre_process_text(data, remove_stop_words=True, remove_mbti_profiles=True)

            cntizer = CountVectorizer(analyzer="word",
                                      max_features=1000,
                                      max_df=0.7,
                                      min_df=0.1)
            # the feature should be made of word n-gram
            # Learn the vocabulary dictionary and return term-document matrix
            X_cnt = cntizer.fit_transform(list_posts)

            # The enumerate object yields pairs containing a count and a value (useful for obtaining an indexed list)
            feature_names = list(enumerate(cntizer.get_feature_names()))

            # For the Standardization or Feature Scaling Stage :-
            # Transform the count matrix to a normalized tf or tf-idf representation
            tfizer = TfidfTransformer()

            # Learn the idf vector (fit) and transform a count matrix to a tf-idf representation

            X_tfidf = tfizer.fit_transform(X_cnt).toarray()
            print(X_tfidf.shape)

            personality_type = ["IE: Introversion (I) / Extroversion (E)", "NS: Intuition (N) / Sensing (S)",
                                "FT: Feeling (F) / Thinking (T)", "JP: Judging (J) / Perceiving (P)"]

            for l in range(len(personality_type)):
                print(personality_type[l])

            # Posts in tf-idf representation
            X = X_tfidf
            my_posts = """Highly motivated and detail-oriented data science student with a strong academic
                        background in mathematics and computer science. Proficient in Python, R, SQL, Azure and
                        always keen to learn new technologies and tools from the latest tech stacks. Seeking an
                        internship in the data science field to apply skills and knowledge gained from coursework and
                        projects."""
            # The type is just a dummy so that the data prep function can be reused
            mydata = pd.DataFrame(data={'type': ['INFJ'], 'posts': [my_posts]})

            my_posts, dummy = pre_process_text(mydata, remove_stop_words=True, remove_mbti_profiles=True)

            my_X_cnt = cntizer.transform(my_posts)
            my_X_tfidf = tfizer.transform(my_X_cnt).toarray()


            import pickle

            # load the saved model from a file
            filename = 'xgb_model1.pkl'
            with open(filename, 'rb') as file:
                model = pickle.load(file)

            my_posts = str (cover_letter)

            # The type is just a dummy so that the data prep function can be reused
            mydata = pd.DataFrame(data={'type': ['INFJ'], 'posts': [my_posts]})

            my_posts, dummy = pre_process_text(mydata, remove_stop_words=True, remove_mbti_profiles=True)

            my_X_cnt = cntizer.transform(my_posts)
            my_X_tfidf = tfizer.transform(my_X_cnt).toarray()

            final_result = []
            # Individually training each mbti personlity type
            for l in range(len(personality_type)):
                print("%s classifier trained" % (personality_type[l]))
                # make predictions on the new data using the loaded model
                predictions = model.predict(my_X_tfidf)
                final_result.append(predictions[0])

            print("The result is: ", translate_back(final_result))

            # Add a text box for the user to enter the cover letter
            personality = (translate_back(final_result))
            st.write(f"Predicted Personality: {personality}")

        insert_data(resume_data['name'], resume_data['email'], str(resume_score), timestamp,
                str(resume_data['no_of_pages']), selected_job_role, cand_level, str(resume_data['skills']),
                str(recommended_skills), str(rec_course),str(personality))
        print(resume_data['name'])
        print(resume_data['email'])
        print(resume_score)
        print(timestamp)
        connection.commit()
        st.write ('Commited to database successfully!')


def run():
    # Set the page background color and style
    page_bg_img = '''
    <style>
    body {
    background-image: url("Logo/cv zone.png");
    background-size: cover;
    }
    </style>
    '''

    st.markdown(page_bg_img, unsafe_allow_html=True)
    st.title("CV ZONE")
    st.sidebar.markdown("# Choose User")
    activities = ["Normal User", "Admin"]
    choice = st.sidebar.selectbox("Choose among the given options:", activities)

    # job_role_selection()

    # Create the DB
    db_sql = """CREATE DATABASE IF NOT EXISTS SRA;"""
    cursor.execute(db_sql)

    # Create table
    DB_table_name = 'user_info'
    table_sql = "CREATE TABLE IF NOT EXISTS " + DB_table_name + """
                    (ID INT NOT NULL AUTO_INCREMENT,
                     Name varchar(100) NOT NULL,
                     Email_ID VARCHAR(50) NOT NULL,
                     resume_score VARCHAR(8) NOT NULL,
                     Timestamp VARCHAR(50) NOT NULL,
                     Page_no VARCHAR(5) NOT NULL,
                     Predicted_Field VARCHAR(25) NOT NULL,
                     User_level VARCHAR(30) NOT NULL,
                     Actual_skills VARCHAR(300) NOT NULL,
                     Recommended_skills VARCHAR(300) NOT NULL,
                     Recommended_courses VARCHAR(600) NOT NULL,
                     Predicted_Personality VARCHAR(20) NOT NULL,
                     PRIMARY KEY (ID));
                    """
    cursor.execute(table_sql)
    if choice == 'Normal User':
        normal_user()

    else:
        ## Admin Side
        st.success('Welcome back Admin')

        ad_user = st.text_input("Username").lower()
        ad_password = st.text_input("Password", type='password')
        if st.button('Login'):
            if ad_user == 'cvzone' and ad_password == 'cvzone123':
                st.success("Welcome Admin")
                # Display Data

                cursor.execute('''SELECT*FROM user_info''')
                data = cursor.fetchall()
                st.header("**User's👨‍💻 Data**")
                df = pd.DataFrame(data, columns=['ID', 'Name', 'Email', 'Resume Score', 'Timestamp', 'Total Page',
                                                 'Predicted Field', 'User Level', 'Actual Skills', 'Recommended Skills',
                                                 'Recommended Course','Predicted_Personality'])
                st.dataframe(df)
                st.markdown(get_table_download_link(df,'User_Info.csv','Download Report'), unsafe_allow_html=True)
                ## Admin Side Data
                query = 'select * from user_info;'#Change the order of columns resume score and personality
                plot_data = pd.read_sql(query, connection) #Filter the columns based on the highest resume score - Top 10 - Top 3

                ## Pie chart for predicted field recommendations
                labels = plot_data.Predicted_Field.unique()
                print(labels)
                values = plot_data.Predicted_Field.value_counts()
                print(values)
                st.subheader("📈 **Pie-Chart for Predicted Field Recommendations**")
                fig = px.pie(df, values=values, names=labels, title='Predicted Field according to the Skills')
                st.plotly_chart(fig)

                ### Pie chart for User's👨‍💻 Experienced Level
                labels = plot_data.User_level.unique()
                values = plot_data.User_level.value_counts()
                st.subheader("📈 ** Pie-Chart for User's👨‍💻 Experienced Level**")
                fig = px.pie(df, values=values, names=labels, title="Pie-Chart📈 for User's👨‍💻 Experienced Level")
                st.plotly_chart(fig)


            else:
                st.error("Wrong ID & Password Provided")

#Establishing mysql database connection
connection = pymysql.connect(host='localhost',user='root',password='',db='sra')
cursor = connection.cursor()
run()

#Run the program using py --m streamlit run main.py