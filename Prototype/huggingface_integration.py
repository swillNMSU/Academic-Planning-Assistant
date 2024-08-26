from transformers import BartForConditionalGeneration, BartTokenizer
import random
from db_interaction import get_course_recommendations
from gpt4all import GPT4All

model = GPT4All("Meta-Llama-3-8B-Instruct.Q4_0.gguf") # downloads / loads a 4.66GB LLM

def process_query_with_bart(query):
    with model.chat_session():
        # print(model.generate(query, max_tokens=1024))
        generated_text = model.generate(query, max_tokens=256)

    # For demonstration, assume BART's generated text gives us a major like "Computer Science"
    major = extract_major_from_response(generated_text)

    if major:
         course_recommendations = get_course_recommendations(major)
    
    if course_recommendations:
        # Format the course recommendations into a response text
        response_text = f"For the major in {major}, you should consider the following courses:\n"
        for semester, courses in course_recommendations.items():
            response_text += f"\n{semester}:\n"
            for course in courses:
                course_name = course['course_name']
                course_code = course['course_code']
                prerequisites = course['prerequisites']
                prereq_text = ', '.join(str(p) for p in prerequisites) if prerequisites else 'None'
                response_text += f"- {course_code}: {course_name} (Prerequisites: {prereq_text})\n"
    else:
        response_text = f"Sorry, I couldn't find course recommendations for the major in {major}."

    # Combine generated text with response text, separated by a newline
    combined_text = generated_text + "\n" + response_text

    return combined_text, course_recommendations

def extract_major_from_response(response):
    # A placeholder function to extract the major from BART's response
    # You could improve this with named entity recognition (NER) or keyword matching
    if "Computer Science" in response:
        return "Computer Science"
    elif "Business" in response:
        return "Business"
    return None

if __name__ == "__main__":
    test_query = "I'm interested in video game development, what major should I choose?"
    print(process_query_with_bart(test_query))