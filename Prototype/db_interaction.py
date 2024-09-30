import psycopg2
from pymongo import MongoClient
import re

# PostgreSQL Connection Setup
def get_postgres_connection():
    try:
        conn = psycopg2.connect(
            dbname="academic_planner",
            user="postgres",
            password="4S2CiZ$GTr",
            host="localhost"
        )
        return conn
    except Exception as e:
        print(f"Error connecting to PostgreSQL database: {e}")
        return None

# MongoDB Connection Setup
def get_mongo_connection():
    try:
        client = MongoClient('localhost', 27017)
        db = client.academic_planner_db
        return db
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        return None

# Example PostgreSQL Query: Fetch All Courses
def fetch_all_courses():
    conn = get_postgres_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM courses;")
                courses = cur.fetchall()
                return courses
        except Exception as e:
            print(f"Error fetching courses: {e}")
        finally:
            conn.close()
    return []

def log_user_session(user_id, session_data):
    db = get_mongo_connection()
    if db is not None:
        try:
            user_sessions = db.user_sessions
            session_data['user_id'] = user_id
            session_id = user_sessions.insert_one(session_data).inserted_id
            return session_id
        except Exception as e:
            print(f"Error logging user session: {e}")
    return None

def get_course_recommendations(major):
    conn = get_postgres_connection()
    recommendations = {}
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute("""
                SELECT 
                    c.name AS course_name, 
                    s.semester_name, 
                    c.prerequisites AS prerequisites
                FROM courses c
                JOIN course_semester_mapping csm ON c.course_id = csm.course_id
                JOIN semesters s ON csm.semester_id = s.semester_id
                WHERE csm.major_id = (
                    SELECT major_id FROM majors WHERE major_name = %s
                )
                ORDER BY s.semester_id;
                """, (major,))
                
                # Fetch all rows
                rows = cur.fetchall()

                # Structure the recommendations by semester
                for row in rows:
                    course_name, semester_name, prerequisites = row
                    if semester_name not in recommendations:
                        recommendations[semester_name] = []

                    recommendations[semester_name].append({
                        "course_name": course_name,
                        "prerequisites": prerequisites if prerequisites else "None"
                    })
        except Exception as e:
            print(f"Error fetching course recommendations for {major}: {e}")
        finally:
            conn.close()
    return recommendations

def parse_credits(credits_str):
    # Use regex to extract the number at the start of the string (e.g., "4 Credits")
    match = re.search(r'\d+', credits_str)
    if match:
        return int(match.group(0))  # Convert the matched number to an integer
    return 0  # Return 0 if no match is found

def fetch_remaining_courses(major, completed_courses):
    conn = get_postgres_connection()
    remaining_courses = []
    
    if conn:
        try:
            with conn.cursor() as cur:
                # Fetch remaining courses for the major, excluding completed ones
                cur.execute("""
                SELECT 
                    c.name AS course_name,
                    c.prerequisites, 
                    c.credits
                FROM courses c
                JOIN course_semester_mapping csm ON c.course_id = csm.course_id
                WHERE csm.major_id = (
                    SELECT major_id FROM majors WHERE major_name = %s
                )
                AND c.name NOT IN %s
                ORDER BY csm.semester_id;
                """, (major, tuple(completed_courses)))
                
                remaining_courses = cur.fetchall()
        except Exception as e:
            print(f"Error fetching remaining courses: {e}")
        finally:
            conn.close()

    return [{'course_name': row[0], 'prerequisites': row[1], 'credits': parse_credits(row[2])} for row in remaining_courses]


# Example Usage
if __name__ == "__main__":
    # PostgreSQL Example: Fetch and print all courses
    courses = fetch_all_courses()
    for course in courses:
        print(course)
    
    # MongoDB Example: Log a user session
    user_session_data = {
        "session_start": "2024-03-21T10:00:00",
        "actions": ["logged in", "viewed courses"],
    }
    session_id = log_user_session("user123", user_session_data)
    print(f"Logged user session with ID: {session_id}")
