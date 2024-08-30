from flask import Flask, request, jsonify, render_template
from flask_restful import Api
from huggingface_integration import process_query_with_bart
from db_interaction import get_course_recommendations

app = Flask(__name__, template_folder='templates', static_folder='static')
api = Api(app)

@app.route('/')
def home():
    return render_template('index.html')

def process_major_choice(major):
    # Fetch course recommendations for the chosen major
    course_recommendations = get_course_recommendations(major)
    
    if course_recommendations:
        # Format the course recommendations into a response text
        response_text = f"For the major in {major}, you should consider the following courses:\n"
        for semester, courses in course_recommendations.items():
            response_text += f"\n{semester}:\n"
            for course in courses:
                course_name = course['course_name']
                prerequisites = course['prerequisites']
                prereq_text = ', '.join(str(p) for p in prerequisites) if prerequisites else 'None'
                response_text += f"- {course_name} (Prerequisites: {prereq_text})\n"
    else:
        response_text = f"Sorry, I couldn't find course recommendations for the major in {major}."

    # Return both response text and structured data for flowchart
    return response_text, course_recommendations

@app.route('/webhook', methods=['POST'])
def dialogflow_webhook():
    req = request.get_json(silent=True, force=True)
    
    # Extract the intent name from the request
    intent_name = req.get("queryResult").get("intent").get("displayName")
    
    # Process the request based on the intent
    if intent_name == 'ChooseMajor':
        major = req.get("queryResult").get("parameters").get("Major")
        response_text, course_recommendations = process_major_choice(major)
        
        # Respond with both the text and the course recommendations for the flowchart
        return jsonify({
            "fulfillmentMessages": [
                {"text": {"text": [response_text]}},
                {"flowchartData": course_recommendations}
            ]
        })

    elif intent_name == 'GenerateAdvice':
        # Using Hugging Face model for generating advice
        query = req.get("queryResult", {}).get("queryText", "")
        response_text, course_recommendations = process_query_with_bart(query)

        return jsonify({
            "fulfillmentMessages": [
                {"text": {"text": [response_text]}},
                {"flowchartData": course_recommendations}
            ]
        })
if __name__ == '__main__':
    app.run(port=5000, debug=True)
