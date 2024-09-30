import transformers
import torch
from db_interaction import get_course_recommendations, fetch_remaining_courses
from huggingface_hub import login

# from transformers import BartForConditionalGeneration, BartTokenizer
# import random
# from db_interaction import get_course_recommendations
# from gpt4all import GPT4All

# model = GPT4All("Meta-Llama-3-8B-Instruct.Q4_0.gguf") # downloads / loads a 4.66GB LLM

# def process_query_with_bart(query):
#     with model.chat_session():
#         # print(model.generate(query, max_tokens=1024))
#         generated_text = model.generate(query, max_tokens=256)

#     # For demonstration, assume BART's generated text gives us a major like "Computer Science"
#     major = extract_major_from_response(generated_text)

#     if major:
#          course_recommendations = get_course_recommendations(major)
    
#     if course_recommendations:
#         # Format the course recommendations into a response text
#         response_text = f"For the major in {major}, you should consider the following courses:\n"
#         for semester, courses in course_recommendations.items():
#             response_text += f"\n{semester}:\n"
#             for course in courses:
#                 course_name = course['course_name']
#                 prerequisites = course['prerequisites']
#                 prereq_text = ', '.join(str(p) for p in prerequisites) if prerequisites else 'None'
#                 response_text += f"- {course_name} (Prerequisites: {prereq_text})\n"
#     else:
#         response_text = f"Sorry, I couldn't find course recommendations for the major in {major}."

#     # Combine generated text with response text, separated by a newline
#     combined_text = generated_text + "\n" + response_text

#     return combined_text, course_recommendations

# def extract_major_from_response(response):
#     # A placeholder function to extract the major from BART's response
#     # You could improve this with named entity recognition (NER) or keyword matching
#     if "Computer Science" in response:
#         return "Computer Science"
#     elif "Business" in response:
#         return "Business"
#     return None

# if __name__ == "__main__":
#     test_query = "I'm interested in video game development, what major should I choose?"
#     print(process_query_with_bart(test_query))


# Initialize Llama 3.1 using the Transformers pipeline
model_id = "meta-llama/Meta-Llama-3.1-8B-Instruct"

pipeline = transformers.pipeline(
    "text-generation",
    model=model_id,
    model_kwargs={"torch_dtype": torch.bfloat16},
    device_map="auto",
)

# Process user query with LLM
def process_query_with_llm(query, completed_courses=None):
    # Use LLM to interpret the user's query
    messages = [
        {"role": "system", "content": "You are a helpful assistant providing academic planning advice to students."},
        {"role": "user", "content": query},
    ]
    
    # Generate a response using Llama 3.1
    llm_response = pipeline(messages, max_new_tokens=50)[0]["generated_text"]
    
    # Extract potential major or other context from the LLM response
    major = extract_major_from_response(llm_response)
    
    response_text = ""
    course_plan = []

    if major:
        # Use the provided completed courses to fetch remaining courses or full recommendations
        if completed_courses:
            course_plan = fetch_remaining_courses(major, completed_courses)
        else:
            course_plan = get_course_recommendations(major)

    if course_plan:
        # Construct the response text with personalized course recommendations
        response_text = f"For the major in {major}, based on your input, here are the recommended courses:\n"
        for semester, courses in course_plan.items():
            response_text += f"\n{semester}:\n"
            for course in courses:
                course_name = course['course_name']
                credits = course.get('credits', 'N/A')
                prerequisites = course.get('prerequisites', 'None')
                response_text += f"- {course_name} (Credits: {credits}, Prerequisites: {prerequisites})\n"
    else:
        response_text = f"Sorry, I couldn't find any course recommendations for the major '{major}'."

    # Combine LLM generated response with structured academic recommendations
    combined_text = f"LLM Insight:\n{llm_response}\n\nPersonalized Course Plan:\n{response_text}"
    
    return combined_text, course_plan

# Extract the major or context based on the LLM response
def extract_major_from_response(response):
    # List of possible majors to recognize from the response
    potential_majors = ["Computer Science", "Business", "Engineering", "Mathematics"]  # Extend as needed
    for major in potential_majors:
        if major.lower() in response.lower():
            return major
    return None

if __name__ == "__main__":
    # Example query with completed courses
    test_query = "I've already completed Math 121 and CS 101. What should I take next to finish my Computer Science degree?"
    completed_courses = ["Math 121", "CS 101"]

    # Generate course recommendations
    combined_text, course_plan = process_query_with_llm(test_query, completed_courses=completed_courses)
    print(combined_text)
