import psycopg2
from pymongo import MongoClient

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
                # cur.execute("""
                # SELECT c.course_name, c.course_code
                # FROM courses c
                # JOIN degree_requirements dr ON c.course_id = dr.course_id
                # WHERE dr.major_id = (
                #   SELECT major_id FROM majors WHERE major_name = %s
                # )
                # """, (major,))
                # recommendations = cur.fetchall()
                cur.execute("""
                SELECT 
                    c.course_name, 
                    c.course_code, 
                    s.semester_name, 
                    scm.prerequisites
                FROM courses c
                JOIN semester_course_mapping scm ON c.course_id = scm.course_id
                JOIN semesters s ON scm.semester_id = s.semester_id
                WHERE scm.major_id = (
                    SELECT major_id FROM majors WHERE major_name = %s
                )
                ORDER BY s.semester_id;
                """, (major,))
                
                # Fetch all rows
                rows = cur.fetchall()
                print("Fetched rows:", rows)

                # Structure the recommendations by semester
                for row in rows:
                    course_name, course_code, semester_name, prerequisites = row
                    print(f"Processing row: {row}")
                    if semester_name not in recommendations:
                        recommendations[semester_name] = []
                    
                    recommendations[semester_name].append({
                        "course_name": course_name,
                        "course_code": course_code,
                        "prerequisites": prerequisites
                    })
        except Exception as e:
            print(f"Error fetching course recommendations for {major}: {e}")
        finally:
            conn.close()
    return recommendations



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
