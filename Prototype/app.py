from flask import Flask, request, jsonify, render_template
from flask_restful import Api
from huggingface_integration import process_query_with_ollama
from db_interaction import get_course_recommendations, fetch_remaining_courses, fetch_course_id, get_remaining_courses
import fitz
import re
import os
from collections import defaultdict

app = Flask(__name__, template_folder='templates', static_folder='static')
api = Api(app)

@app.route('/')
def home():
    return render_template('index.html')

def format_semesters_for_ui(semesters_dict):
    formatted_semesters = []
    for semester, courses in semesters_dict.items():
        formatted_courses = [{"course_code": course.split(".")[0], "course_title": course.split(".")[1].strip()} for course in courses]
        formatted_semesters.append({"semester": semester, "courses": formatted_courses})
    return formatted_semesters

# Helper function to extract integer credits from the formatted string
def extract_credits(credit_str):
    match = re.search(r'\d+', credit_str)  # Finds the first number in the string
    return int(match.group()) if match else 0

# Define a function to organize courses into semesters with dynamic semester titles
def plan_semesters(remaining_courses, max_credits_per_semester, start_year=2024):
    # Data structure to hold planned semesters
    semesters = defaultdict(list)
    current_semester = 1
    remaining_credits = max_credits_per_semester
    
    # Determine semester title sequence
    term = 'FA'  # Start with Fall
    year = start_year
    
    # Sort courses by prerequisites to satisfy dependencies
    remaining_courses.sort(key=lambda course: course[3])  # Sorting by prerequisites

    for course in remaining_courses:
        course_code = course[0]       # Course code is the first element
        course_credits = extract_credits(course[1])  # Extract credits as integer
        prerequisites = course[3]     # Prerequisites are the fourth element
        
        # Check if prerequisites are already completed or in remaining courses
        if all(prereq not in [c[0] for c in remaining_courses] for prereq in prerequisites):
            # Check if the course can fit in the current semester's credit load
            if course_credits <= remaining_credits:
                semesters[(term, year)].append(f"{course_code}. {course[2]} {course[1]}")
                remaining_credits -= course_credits
            else:
                # Move to the next semester if credit limit is exceeded
                current_semester += 1
                # Alternate term and update year as needed
                term = 'FA' if term == 'SP' else 'SP'
                if term == 'SP':
                    year += 1
                remaining_credits = max_credits_per_semester - course_credits
                semesters[(term, year)].append(f"{course_code}. {course[2]} {course[1]}")
    
    # Prepare response text for UI
    response_text = "Here is your semester-by-semester course plan:\n"
    for (term, year), courses in semesters.items():
        response_text += f"\n{term} {year}:\n" + "\n".join(f" - {course}" for course in courses)

    print(response_text)
    return response_text

def insert_space_before_number(strings):
    # This regular expression finds a letter followed by a number and adds a space in between
    return [re.sub(r'([A-Za-z])(\d)', r'\1 \2', string) for string in strings]

def join_strings_with_commas(strings_list):
    # Join the list of strings into a single string, separated by commas
    return ', '.join(strings_list)

def grab_until_period(strings_list):
    result = []
    
    for string in strings_list:
        # Find the index of the first period
        period_index = string.find('.')
        
        # If a period is found, grab everything up to and including the period
        if period_index != -1:
            result.append(string[:period_index + 1])
        else:
            result.append(string)  # If no period, return the original string
    
    return result

def process_course_plan_with_rag(major, completed_courses, course_load, interests=""):
    #print(completed_courses)

    new_complete = grab_until_period(completed_courses)

    # Convert the list into a single comma-separated string
    # function to get course code.
    courses = fetch_course_id(new_complete)
    #print("This is ids:", courses)
    remaining_courses = get_remaining_courses(major, courses)

    semesters = plan_semesters(remaining_courses, 15)

    #print(remaining_courses)

    if not remaining_courses:
        return "No remaining courses found or all courses are completed.", []

    course_context = "\n".join(
        f"{course[0]} (Credits: {course[1]}, Prerequisites: {course[3]})"
        for course in remaining_courses
    )

    completed_courses = join_strings_with_commas(completed_courses)

    # Include user interests in the prompt if provided
    interest_text = f"\nUser interests: {interests}" if interests else ""

    prompt = (
        f"Based on the remaining required courses for a {major} degree:\n{course_context}\n"
        f"And based on the completed courses: \n{completed_courses}\n"
        f"{interest_text}\n\n"
        f"Please create a personalized course plan for a student considering a course load of {course_load} credits per semester."
        f"Only use the required remaining courses to create the plan. Do not include elective or additional credits beyond what is necessary to complete the degree. If all required courses can be completed in one semester, limit the plan to one semester."
        f"Also prequisite courses should be in the complteded courses unless a student still needs to take a prequisite course"

    )

    #response_text = process_query_with_ollama(prompt)

    response_text = semesters

    return response_text, remaining_courses

# Utility function to extract all text from a PDF file
def extract_text_from_pdf(pdf_file_path):
    with fitz.open(pdf_file_path) as pdf:
        text = ""
        for page_num in range(pdf.page_count):
            page = pdf.load_page(page_num)
            text += page.get_text()
    return text


@app.route('/upload', methods=['POST'])
def upload_degree_audit():
    if not os.path.exists('DegreeAuditPDF'):
        os.makedirs('DegreeAuditPDF')

    if 'file' not in request.files:
        return jsonify({"error": "No file part"})
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No selected file"})
    
    file_path = f"DegreeAuditPDF/{file.filename}"
    file.save(file_path)

    pdf_text = extract_text_from_pdf(file_path)

    with open("AUDIT.txt", "w") as file:
    # Write text to the file
        file.write(pdf_text)

    # Define a pattern to match the course code, title, and look for 'CONVERTED TO'
    pattern = re.compile(r'([A-Z]+\s*[A-Z]*\s*\d{3,4}\s*[A-Z]?)\n\d+\.\d+\s+[A-Z]+\-?\+?\n(.+?)(?=(?:\nCONVERTED TO: ([A-Z]+\s*\d{3,4}[A-Z]*))|\n|$)')

    # Read the file and extract the relevant data
    courses = []
    # Find all matches of the course pattern, including converted courses
    matches = pattern.findall(pdf_text)

    for match in matches:
        course_code = match[0]  # Original course code like ENGL111G
        course_title = match[1]  # Course title like COMPOSITION & RHETORIC I
        converted_to = match[2]  # Converted course code if exists like MATH1511G

        # If there is a converted course code, use that instead of the original one
        if converted_to:
            course_code = converted_to

        courses.append(f"{course_code}. {course_title}")

    # Clean up the course list to remove unnecessary labels like FA, SP
    for i in range(len(courses)):
        courses[i] = courses[i].replace("FA\n", "").replace("SP\n", "")

    # Now, the 'courses' list will have updated course codes if any were converted

    #print("Before edit: ", courses)

    courses = insert_space_before_number(courses)

    #print("After edit: ", courses)


    # Integrate PDF extraction with the course plan generation
    major = "Computer Science"  # Example major, can be dynamic based on user input
    course_load = 15  # Default course load, can be dynamic based on user input

    # response_text, course_plan = generate_course_plan(major, courses, course_load)

    interests = "Artificial Intelligence, Cybersecurity"
    response_text, course_plan = process_course_plan_with_rag(major, courses, course_load, interests)

    return jsonify({
            "fulfillmentMessages": [
                {"text": {"text": [response_text]}},
                {"flowchartData": course_plan}
            ]
        })

if __name__ == '__main__':
    app.run(port=5000, debug=True)
