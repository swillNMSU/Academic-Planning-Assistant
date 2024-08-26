# Academic Planning Assistant

The **Academic Planning Assistant** is a web-based service that helps students explore academic majors based on their interests. It provides personalized major recommendations, shows relevant course listings, and generates a visual flowchart to guide students through their course planning. The service is fully hosted online, so users only need to visit the website to interact with the system.

## Table of Contents

- [Features](#features)
- [Technologies Used](#technologies-used)
- [How It Works](#how-it-works)
- [Usage](#usage)
  - [Step 1: Major Recommendations](#step-1-major-recommendations)
  - [Step 2: Course Listings](#step-2-course-listings)
  - [Step 3: Flowchart Display](#step-3-flowchart-display)
  - [Step 4: Save and Compare](#step-4-save-and-compare)
- [File Structure](#file-structure)
- [Live Service](#live-service)
- [Optimizations and Improvements](#optimizations-and-improvements)
- [Future Enhancements](#future-enhancements)
- [Credits](#credits)

---

## Features

1. **Major Recommendations**: Uses AI to recommend suitable academic majors based on user interests.
2. **Course Listings**: Displays courses by semester, organized based on the selected major, including prerequisites.
3. **Flowchart Visualization**: Generates an interactive flowchart for students to visualize course sequences and dependencies.
4. **Save and Compare (In Progress)**: Users can save their selected majors, compare different majors, and download or email their personalized academic plan.
5. **Web-Based (In Progress)**: Fully online service—no software downloads or database setups are required by the user.

---

## Technologies Used

1. **Backend**:
   - **Python (Flask)**: Handles the backend logic and API routing.
   - **GPT4All / Meta-LLaMA**: AI models for generating major recommendations.
   - **PostgreSQL**: Backend database for storing course, major, and semester data.
   - **MongoDB** (optional): For session management and user interactions.

2. **Frontend**:
   - **HTML/CSS/JavaScript**: Frontend UI and interactivity.
   - **jsPlumb**: Library for generating flowcharts.

3. **Hosting**:
   - The entire service is hosted online (e.g., AWS, Heroku, or DigitalOcean), allowing users to access it via a web browser.

---

## How It Works

The Academic Planning Assistant works in three key steps:
1. **User Input**: The user provides input about their academic interests via the web interface.
2. **AI Model Recommendation**: The AI model processes the user input and suggests suitable academic majors.
3. **Course Planning**: Once a major is selected, the system displays the relevant courses by semester and presents them in an interactive flowchart. The user can explore the courses, view prerequisites, and save or download their academic plan.

### Fully Hosted Service
The backend databases (PostgreSQL for course and major data, MongoDB for session data) are fully managed on the server. Users only need to access the web-based service—no local installation or setup is required.

---

## Usage

### Step 1: Major Recommendations

- Users input their interests (e.g., "I enjoy video game development").
- The AI model analyzes the input and suggests majors that align with those interests.
- The recommendations are displayed as interactive cards, where users can click to learn more about each major.

### Step 2: Course Listings

- Once a major is selected, the user is shown the relevant courses for that major, organized by semester.
- Each semester's courses are displayed in an accordion-style list, allowing the user to expand and collapse sections.

### Step 3: Flowchart Display

- A dynamic flowchart is generated, showing the sequence of courses and their prerequisites.
- The flowchart is interactive: users can drag elements, and hovering over a course provides more information about it.

### Step 4: Save and Compare

- Users can save multiple majors and compare their courses, duration, and core requirements.
- A downloadable PDF summary is available, as well as the option to email the summary to themselves.

---

## File Structure

```bash
├── app.py                      # Main Flask app
├── db_interaction.py            # Database interaction logic (PostgreSQL, MongoDB)
├── huggingface_integration.py   # AI model integration for major recommendations
├── static/                      # JavaScript and CSS files
│   ├── script.js                # Frontend logic for interactivity
├── templates/                   # HTML templates
│   └── index.html               # Main HTML page
├── requirements.txt             # Python dependencies
├── README.md                    # This README file
```

---

## Live Service

The **Academic Planning Assistant** is hosted online, meaning users only need to visit the web URL to interact with the system. All major recommendations, course data, and flowchart visualizations are handled on the backend, so users don’t need to download or set up anything locally.

### Accessing the Service
Simply visit the URL to start exploring major recommendations and planning your courses. All user sessions are managed in the cloud, and no personal downloads are required.

---

## Optimizations and Improvements

1. **AI Model Efficiency**:
   - Reduced model size and token generation time to improve the speed of recommendations.
   - Caching frequently accessed recommendations to reduce response times for common queries.

2. **Database Optimization**:
   - Efficient indexing and query optimization for the PostgreSQL database ensure that course recommendations and flowcharts are generated quickly.

3. **Interactive Features**:
   - Courses are displayed with tooltips, hover effects, and draggable flowchart elements, allowing for a more engaging user experience.

---

## Future Enhancements

1. **Advanced Major Recommendations**:
   - Use more advanced natural language processing to provide more nuanced and accurate major recommendations.
   
2. **Mobile Optimization**:
   - Fully optimize the web interface for mobile and tablet users, making the service accessible across all devices.

3. **GPA and Degree Progress Tracking**:
   - Integrate GPA tracking and semester-by-semester degree progress tracking to help students stay on track with their academic goals.

4. **User Account System**:
   - Implement a user account system where students can save their academic plans, view them later, and update them as they complete courses.

---

## Credits

- **GPT4All & Meta-LLaMA** for powering the AI-based major recommendations.
- **jsPlumb** for interactive flowchart rendering.
- **Flask** for the backend infrastructure and routing.
- **PostgreSQL** for handling course and major data.

---