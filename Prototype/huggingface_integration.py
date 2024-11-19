import requests

OLLAMA_API_URL = "http://localhost:11434/v1/chat/completions"

def process_query_with_ollama(query):
    messages = [
        {"role": "system", "content": "You are an academic planning assistant who leverages data from a personalized student record to recommend courses."},
        {"role": "user", "content": query}
    ]

    headers = {
        'Content-Type': 'application/json',
    }

    data = {
        "model": "llama3.1:latest",
        "messages": messages
    }

    response = requests.post(OLLAMA_API_URL, headers=headers, json=data)

    if response.status_code == 200:
        response_data = response.json()
        try:
            return response_data['choices'][0]['message']['content']
        except (IndexError, KeyError):
            return "No valid content found in response."
    else:
        return f"Error communicating with Ollama: {response.status_code}, {response.text}"


# Example usage
if __name__ == "__main__":
    user_query = "What courses do I need to complete my Computer Science degree?"
    response_text = process_query_with_ollama(user_query)
    print(response_text)