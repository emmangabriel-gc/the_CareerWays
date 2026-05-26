"""
Database initialization script with course data for CareerWays
Run this script once to populate the database with courses
"""

from app import create_app, db
from models import Course
import uuid

# Course data based on the specification
COURSES_DATA = [
    {
        'name': 'BS Nursing',
        'description': 'Comprehensive nursing degree covering patient care, medical science, and healthcare management.',
        'duration': '4 years',
        'difficulty': 'Advanced',
        'career_path': 'Healthcare Professional',
        'skills_taught': ['Patient Care', 'Medical Knowledge', 'Clinical Skills', 'Communication', 'Teamwork'],
        'prerequisites': ['High school diploma', 'Biology', 'Chemistry'],
        'career_prospects': 'Work in hospitals, clinics, or private practice as a registered nurse',
        'requirements': 'Biology and Chemistry background recommended',
        'category': 'Healthcare',
        'licensure_exams': 'PNLE (Philippine Nursing Licensure Examination)',
        'keywords': ['nursing', 'healthcare', 'patient', 'medical', 'clinical', 'care']
    },
    {
        'name': 'BS Midwifery',
        'description': 'Specialized program in maternal and child health care with focus on pregnancy and childbirth.',
        'duration': '4 years',
        'difficulty': 'Advanced',
        'career_path': 'Healthcare Professional',
        'skills_taught': ['Obstetric Care', 'Patient Assessment', 'Communication', 'Critical Thinking'],
        'prerequisites': ['High school diploma', 'Biology'],
        'career_prospects': 'Practice as a midwife in hospitals or community settings',
        'requirements': 'Strong interest in maternal and child health',
        'category': 'Healthcare',
        'licensure_exams': 'MLE (Midwifery Licensure Examination)',
        'keywords': ['midwifery', 'obstetrics', 'pregnancy', 'childbirth', 'maternal', 'health']
    },
    {
        'name': 'BS Accountancy',
        'description': 'Study of financial accounting, auditing, taxation, and business finance.',
        'duration': '4 years',
        'difficulty': 'Intermediate',
        'career_path': 'Finance Professional',
        'skills_taught': ['Financial Analysis', 'Auditing', 'Taxation', 'Data Analysis', 'Business Acumen'],
        'prerequisites': ['High school diploma', 'Mathematics'],
        'career_prospects': 'Work as accountant, auditor, or financial consultant',
        'requirements': 'Strong analytical and mathematical skills',
        'category': 'Business',
        'licensure_exams': 'CPALE (Certified Public Accountant Licensure Examination)',
        'keywords': ['accounting', 'finance', 'auditing', 'taxation', 'business', 'numbers']
    },
    {
        'name': 'BS Business Administration - Financial Management',
        'description': 'Focus on financial planning, investment analysis, and corporate finance management.',
        'duration': '4 years',
        'difficulty': 'Intermediate',
        'career_path': 'Business Professional',
        'skills_taught': ['Financial Planning', 'Investment Analysis', 'Risk Management', 'Leadership'],
        'prerequisites': ['High school diploma', 'Mathematics'],
        'career_prospects': 'Finance manager, investment banker, or business analyst',
        'requirements': 'Interest in finance and business strategy',
        'category': 'Business',
        'keywords': ['business', 'finance', 'management', 'investment', 'administration']
    },
    {
        'name': 'BS Business Administration - Human Resource Management',
        'description': 'Study of employee relations, recruitment, training, and organizational development.',
        'duration': '4 years',
        'difficulty': 'Intermediate',
        'career_path': 'HR Professional',
        'skills_taught': ['Recruitment', 'Employee Relations', 'Training & Development', 'Leadership'],
        'prerequisites': ['High school diploma'],
        'career_prospects': 'HR Manager, Recruitment Specialist, or Organizational Development Consultant',
        'requirements': 'Strong interpersonal and communication skills',
        'category': 'Business',
        'keywords': ['hr', 'human resources', 'recruitment', 'management', 'employees', 'training']
    },
    {
        'name': 'BS Business Administration - Marketing Management',
        'description': 'Marketing strategy, consumer behavior, digital marketing, and brand management.',
        'duration': '4 years',
        'difficulty': 'Intermediate',
        'career_path': 'Marketing Professional',
        'skills_taught': ['Marketing Strategy', 'Consumer Behavior', 'Digital Marketing', 'Branding'],
        'prerequisites': ['High school diploma'],
        'career_prospects': 'Marketing Manager, Brand Manager, or Digital Marketing Specialist',
        'requirements': 'Creative thinking and analytical mindset',
        'category': 'Business',
        'keywords': ['marketing', 'business', 'branding', 'advertising', 'digital', 'consumer']
    },
    {
        'name': 'BS Custom Administration',
        'description': 'Study of customs procedures, international trade, and regulatory compliance.',
        'duration': '4 years',
        'difficulty': 'Intermediate',
        'career_path': 'Customs Professional',
        'skills_taught': ['Customs Regulations', 'International Trade', 'Compliance', 'Administration'],
        'prerequisites': ['High school diploma'],
        'career_prospects': 'Customs Officer, Trade Compliance Specialist, or International Trade Consultant',
        'requirements': 'Attention to detail and strong analytical skills',
        'category': 'Business',
        'licensure_exams': 'CBLE (Customs Broker Licensure Examination)',
        'keywords': ['customs', 'trade', 'administration', 'compliance', 'regulations', 'international']
    },
    {
        'name': 'BS Information Technology',
        'description': 'Comprehensive IT education covering programming, networking, and system management.',
        'duration': '4 years',
        'difficulty': 'Advanced',
        'career_path': 'IT Professional',
        'skills_taught': ['Programming', 'Database Management', 'Networking', 'System Administration'],
        'prerequisites': ['High school diploma', 'Mathematics'],
        'career_prospects': 'Software Developer, System Administrator, or IT Consultant',
        'requirements': 'Strong problem-solving and analytical skills',
        'category': 'IT',
        'tesda_certification': 'NC II in Computer Systems Servicing, NC III in Programming (.NET Technology/Java), NC III in Web Development)',
        'keywords': ['programming', 'information technology', 'coding', 'software', 'network', 'database']
    },
    {
        'name': 'BS Entertainment and Multimedia Computing - Game Development',
        'description': 'Game design, development, graphics programming, and interactive media creation.',
        'duration': '4 years',
        'difficulty': 'Advanced',
        'career_path': 'Game Developer',
        'skills_taught': ['Game Design', 'Graphics Programming', 'Game Engines', 'Project Management'],
        'prerequisites': ['High school diploma', 'Mathematics', 'Computing basics'],
        'career_prospects': 'Game Developer, Game Designer, or Graphics Programmer',
        'requirements': 'Passion for gaming and creative problem-solving',
        'category': 'IT',
        'tesda_certification': 'NC III in Game Programming',
        'keywords': ['game', 'development', 'graphics', 'programming', 'entertainment', 'multimedia']
    },
    {
        'name': 'BS Entertainment and Multimedia Computing - Digital Animation Technology',
        'description': 'Animation production, digital art, visual effects, and motion graphics.',
        'duration': '4 years',
        'difficulty': 'Advanced',
        'career_path': 'Animator/VFX Artist',
        'skills_taught': ['Animation', 'Visual Effects', 'Digital Art', 'Motion Graphics'],
        'prerequisites': ['High school diploma', 'Art background'],
        'career_prospects': 'Animator, VFX Artist, or Motion Graphics Designer',
        'requirements': 'Artistic talent and creative vision',
        'category': 'Arts',
        'tesda_certification': 'NC II and NC III in Digital Animation, NC III in 3D Animation, NC II in Illustration and NC III in Visual Graphic Design',
        'keywords': ['animation', 'digital art', 'visual effects', 'graphics', 'multimedia', 'motion']
    },
    {
        'name': 'BS Computer Science',
        'description': 'Advanced computing concepts, algorithms, data structures, and theoretical computer science.',
        'duration': '4 years',
        'difficulty': 'Advanced',
        'career_path': 'Computer Scientist',
        'skills_taught': ['Algorithms', 'Data Structures', 'Software Engineering', 'Research'],
        'prerequisites': ['High school diploma', 'Mathematics', 'Physics'],
        'career_prospects': 'Software Engineer, AI Researcher, or Systems Architect',
        'requirements': 'Strong mathematical and logical reasoning',
        'category': 'IT',
        'tesda_certification': 'NC II in Computer Systems Servicing, NC III in Programming (.NET Technology/Java), NC III in Web Development)',
        'keywords': ['computer science', 'algorithms', 'programming', 'software', 'research', 'technology']
    },
    {
        'name': 'Bachelor of Secondary Education - Math',
        'description': 'Mathematics education, pedagogy, and secondary level teaching preparation.',
        'duration': '4 years',
        'difficulty': 'Intermediate',
        'career_path': 'Secondary Educator',
        'skills_taught': ['Mathematics', 'Teaching Methods', 'Curriculum Development', 'Leadership'],
        'prerequisites': ['High school diploma', 'Strong math background'],
        'career_prospects': 'High School Math Teacher or Mathematics Educator',
        'requirements': 'Passion for teaching and strong mathematical knowledge',
        'category': 'Education',
        'licensure_exams': 'LET (Licensure Examination for Teachers)',
        'keywords': ['education', 'teaching', 'mathematics', 'secondary', 'school', 'curriculum']
    },
    {
        'name': 'Bachelor of Elementary Education',
        'description': 'Preparation for teaching in elementary/primary education with focus on child development.',
        'duration': '4 years',
        'difficulty': 'Intermediate',
        'career_path': 'Elementary Educator',
        'skills_taught': ['Child Development', 'Teaching Methods', 'Curriculum Design', 'Classroom Management'],
        'prerequisites': ['High school diploma'],
        'career_prospects': 'Elementary School Teacher or Education Specialist',
        'requirements': 'Patience and love for working with children',
        'category': 'Education',
        'licensure_exams': 'LET (Licensure Examination for Teachers)',
        'keywords': ['education', 'teaching', 'elementary', 'primary', 'children', 'school']
    },
    {
        'name': 'Bachelor of Early Childhood Education',
        'description': 'Specialized education for preschool and early childhood development.',
        'duration': '4 years',
        'difficulty': 'Intermediate',
        'career_path': 'Early Childhood Educator',
        'skills_taught': ['Child Development', 'Early Learning Methods', 'Play-based Teaching', 'Family Engagement'],
        'prerequisites': ['High school diploma'],
        'career_prospects': 'Preschool Teacher, Daycare Director, or Early Childhood Specialist',
        'requirements': 'Passion for early childhood development',
        'category': 'Education',
        'licensure_exams': 'LET (Licensure Examination for Teachers)',
        'keywords': ['education', 'early childhood', 'preschool', 'children', 'development', 'teaching']
    },
    {
        'name': 'Bachelor of Culture and Arts Education',
        'description': 'Arts education, cultural studies, and creative pedagogy.',
        'duration': '4 years',
        'difficulty': 'Intermediate',
        'career_path': 'Arts Educator',
        'skills_taught': ['Art History', 'Creative Teaching', 'Cultural Studies', 'Arts Management'],
        'prerequisites': ['High school diploma', 'Arts background'],
        'career_prospects': 'Arts Teacher, Cultural Coordinator, or Arts Administrator',
        'requirements': 'Passion for arts and culture',
        'category': 'Arts',
        'licensure_exams': 'LET (Licensure Examination for Teachers)',
        'keywords': ['arts', 'education', 'culture', 'teaching', 'creative', 'history']
    },
    {
        'name': 'Bachelor of Secondary Education - English',
        'description': 'English language teaching, literature, writing, and communication skills development.',
        'duration': '4 years',
        'difficulty': 'Intermediate',
        'career_path': 'Secondary Educator',
        'skills_taught': ['English Language', 'Literature', 'Writing', 'Communication', 'Teaching Methods'],
        'prerequisites': ['High school diploma', 'Strong English background'],
        'career_prospects': 'High School English Teacher or Language Educator',
        'requirements': 'Strong writing and communication skills',
        'category': 'Education',
        'licensure_exams': 'LET (Licensure Examination for Teachers)',
        'keywords': ['education', 'teaching', 'english', 'literature', 'writing', 'secondary']
    },
    {
        'name': 'Bachelor of Secondary Education - Filipino',
        'description': 'Filipino language teaching, literature, and cultural studies.',
        'duration': '4 years',
        'difficulty': 'Intermediate',
        'career_path': 'Secondary Educator',
        'skills_taught': ['Filipino Language', 'Literature', 'Cultural Studies', 'Teaching Methods'],
        'prerequisites': ['High school diploma', 'Filipino background'],
        'career_prospects': 'Filipino Language Teacher or Cultural Educator',
        'requirements': 'Fluency in Filipino and passion for language teaching',
        'category': 'Education',
        'licensure_exams': 'LET (Licensure Examination for Teachers)',
        'keywords': ['education', 'teaching', 'filipino', 'language', 'literature', 'secondary']
    },
    {
        'name': 'Bachelor of Physical Education',
        'description': 'Sports science, physical fitness, athletic coaching, and health promotion.',
        'duration': '4 years',
        'difficulty': 'Intermediate',
        'career_path': 'Sports/PE Professional',
        'skills_taught': ['Coaching', 'Sports Science', 'Fitness Training', 'Leadership'],
        'prerequisites': ['High school diploma', 'Physical fitness'],
        'career_prospects': 'Physical Education Teacher, Coach, or Fitness Manager',
        'requirements': 'Passion for sports and physical fitness',
        'category': 'Education',
        'licensure_exams': 'LET (Licensure Examination for Teachers)',
        'keywords': ['education', 'physical education', 'sports', 'coaching', 'fitness', 'health']
    },
    {
        'name': 'Bachelor of Arts and Communication',
        'description': 'Communication theory, media studies, journalism, and public relations.',
        'duration': '4 years',
        'difficulty': 'Intermediate',
        'career_path': 'Communication Professional',
        'skills_taught': ['Communication Theory', 'Journalism', 'Public Relations', 'Media Production'],
        'prerequisites': ['High school diploma'],
        'career_prospects': 'Journalist, PR Manager, or Media Producer',
        'requirements': 'Strong communication and writing skills',
        'category': 'Arts',
        'keywords': ['communication', 'arts', 'journalism', 'media', 'public relations', 'writing']
    },
    {
        'name': 'BS Hospitality Management',
        'description': 'Hotel management, restaurant operations, event planning, and customer service excellence.',
        'duration': '4 years',
        'difficulty': 'Intermediate',
        'career_path': 'Hospitality Professional',
        'skills_taught': ['Hotel Management', 'Customer Service', 'Event Planning', 'Operations Management'],
        'prerequisites': ['High school diploma'],
        'career_prospects': 'Hotel Manager, Event Planner, or Restaurant Manager',
        'requirements': 'Excellent customer service orientation',
        'category': 'Hospitality',
        'tesda_certification': 'NC II in Food and Beverage Services, NC II in Bartending, NC II in Housekeeping, NC II in Bread and Pastry Production',
        'professional_certification': 'CHP (Certified Hospitality Professional)',
        'keywords': ['hospitality', 'hotel', 'management', 'service', 'event', 'tourism']
    },
    {
        'name': 'BS Tourism Management',
        'description': 'Tourism operations, destination management, tour planning, and travel industry expertise.',
        'duration': '4 years',
        'difficulty': 'Intermediate',
        'career_path': 'Tourism Professional',
        'skills_taught': ['Destination Management', 'Tour Operations', 'Travel Planning', 'Marketing'],
        'prerequisites': ['High school diploma'],
        'career_prospects': 'Tourism Manager, Travel Consultant, or Destination Manager',
        'requirements': 'Passion for travel and cultural diversity',
        'category': 'Hospitality',
        'tesda_certification': 'NC II in Travel Services, NC II in Tour Guiding, NC III in Events Management Services',
        'professional_certification': 'CTP (Certified Tourism Professional), CATP (Certified Associate in Tourism and Hospitality Professionals), CGSP (Certified Guest Service Professional)',
        'keywords': ['tourism', 'travel', 'management', 'destination', 'hospitality', 'planning']
    },
]


def init_database():
    """Initialize database with course data"""
    app = create_app()

    with app.app_context():
        try:
            # Create all tables first
            print("[CareerWays] Creating database tables...")
            db.create_all()
            print("[CareerWays] Database tables created/verified successfully")

            # Check if courses already exist
            existing_courses = Course.query.count()
            if existing_courses > 0:
                print(
                    f"[CareerWays] Database already contains {existing_courses} courses")
                print("[CareerWays] Skipping course initialization")
                return

            # Clear existing courses (if any)
            Course.query.delete()
            db.session.commit()

            # Add courses
            print(
                f"[CareerWays] Adding {len(COURSES_DATA)} courses to database...")
            for course_data in COURSES_DATA:
                course = Course(
                    id=str(uuid.uuid4()),
                    **course_data
                )
                db.session.add(course)

            db.session.commit()

            print(
                f"[CareerWays] Database initialized successfully with {len(COURSES_DATA)} courses")
            print("\n[CareerWays] Courses added:")
            for course_data in COURSES_DATA:
                print(f"  ✓ {course_data['name']}")

        except Exception as e:
            db.session.rollback()
            print(f"[CareerWays] Error initializing database: {str(e)}")
            raise


if __name__ == '__main__':
    init_database()
