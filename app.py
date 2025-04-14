from flask import Flask, render_template, redirect, url_for, request
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from flask_oauthlib.client import OAuth
import sqlite3,os
from flask import jsonify
from flask_wtf.csrf import CSRFProtect
from models import User, Database

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Change this to a secure secret key
csrf = CSRFProtect(app)

# Initialize Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

@app.context_processor
def inject_user():
    return dict(current_user=current_user)

"""@app.route('/')
def home():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get all categories with scheme counts
    cursor.execute('''
        SELECT 
            c.name, 
            c.title, 
            c.icon,
            COUNT(s.id) as scheme_count
        FROM categories c
        LEFT JOIN schemes s ON c.id = s.category_id
        GROUP BY c.id, c.name, c.title, c.icon
    ''')
    categories = cursor.fetchall()
    
    # Remove duplicate categories
    unique_categories = {category['name']: category for category in categories}.values()
    
    # Format categories for template
    categories_list = [{
        'name': category['name'],
        'title': category['title'],
        'icon': category['icon'],
        'count': category['scheme_count'],
        'link': f'/{category["name"]}'
    } for category in unique_categories]
    
    # Get featured schemes with more details
    cursor.execute('''
        SELECT 
            s.title,
            s.description,
            s.apply_link,
            s.eligibility,
            s.benefits,
            c.name as category_name
        FROM schemes s
        JOIN categories c ON s.category_id = c.id
        LIMIT 3
    ''')
    featured_schemes = cursor.fetchall()
    
    conn.close()
    return render_template('index.html', 
                         categories=categories_list,
                         schemes=featured_schemes)"""
                    
                    

@app.route('/<category>')
def show_schemes(category):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get category details with all its schemes
    cursor.execute('''
        SELECT 
            c.id,
            c.title,
            s.title as scheme_title,
            s.description,
            s.apply_link,
            s.eligibility,
            s.benefits,
            c.name as category_name
        FROM categories c
        LEFT JOIN schemes s ON c.id = s.category_id
        WHERE c.name = ?
    ''', (category,))
    
    results = cursor.fetchall()
    
    if results:
        schemes = [{
            'title': row['scheme_title'],
            'description': row['description'],
            'apply_link': row['apply_link'],
            'eligibility': row['eligibility'],
            'benefits': row['benefits'],
            'category': category  # Add category to each scheme
        } for row in results if row['scheme_title']]
        
        conn.close()
        
        # Check if template exists, otherwise use a generic template
        template_name = f'{category}.html'
        if not os.path.exists(os.path.join('templates', template_name)):
            template_name = 'generic_category.html'
            
        return render_template(
            template_name,
            schemes=schemes,
            title=results[0]['title']
        )
    
    conn.close()
    return "Category not found", 404
@app.route('/search')
def search():
    query = request.args.get('q', '').lower()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Search schemes in database
    cursor.execute('''
        SELECT s.title, s.description, s.apply_link, s.eligibility,
               c.name as category
        FROM schemes s
        JOIN categories c ON s.category_id = c.id
        WHERE LOWER(s.title) LIKE ? OR LOWER(s.description) LIKE ?
    ''', (f'%{query}%', f'%{query}%'))
    
    results = cursor.fetchall()
    conn.close()
    
    return render_template('search_results.html', 
                         results=results, 
                         query=query)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/faqs')
def faqs():
    return render_template('faqs.html')

def get_db_connection():
    return Database.get_connection()

schemes_data = {
    'healthcare': {
        'title': 'Healthcare',
        'icon': '🏥',
        'count': '30',
        'schemes': [
            {
                'title': 'Ayushman Bharat',
                'description': 'Provides health coverage up to Rs. 5 lakhs per family per year for secondary and tertiary care.',
                'apply_link': 'https://pmjay.gov.in/',
                'eligibility': 'Poor and vulnerable families as per SECC database',
                'benefits': 'Medical coverage up to ₹5 lakhs per family per year'
            },
            {
                'title': 'PM Jan Arogya Yojana',
                'description': 'Flagship scheme to provide health coverage for poor and vulnerable families.',
                'apply_link': 'https://pmjay.gov.in/apply',
                'eligibility': 'Families listed in SECC database',
                'benefits': 'Cashless health coverage up to ₹5 lakhs'
            }
        ]
    },
    'education': {
        'title': 'Education',
        'icon': '📚',
        'count': '25',
        'schemes': [
            {
                'title': 'PM Vidya Scheme',
                'description': 'Scholarship program for meritorious students.',
                'apply_link': 'https://scholarships.gov.in/',
                'eligibility': 'Students with more than 80% marks',
                'benefits': 'Annual scholarship of ₹12,000'
            }
        ]
    },
    'agriculture': {
        'title': 'Agriculture & Rural',
        'icon': '🌾',
        'count': '20',
        'schemes': [
            {
                'title': 'PM Kisan Samman Nidhi',
                'description': 'Income support to farmer families.',
                'apply_link': 'https://pmkisan.gov.in/',
                'eligibility': 'All farmer families with cultivable land',
                'benefits': '₹6,000 per year in three installments'
            }
        ]
    },
    'housing': {
        'title': 'Housing',
        'icon': '🏠',
        'count': '15',
        'schemes': [
            {
                'title': 'PM Awas Yojana',
                'description': 'Housing for All scheme providing affordable housing.',
                'apply_link': 'https://pmaymis.gov.in/',
                'eligibility': 'EWS/LIG/MIG categories',
                'benefits': 'Subsidy on home loans up to ₹2.67 lakhs'
            }
        ]
    },
    'employment': {
        'title': 'Employment',
        'icon': '💼',
        'count': '35',
        'schemes': [
            {
                'title': 'PM Rozgar Yojana',
                'description': 'Self-employment scheme for educated unemployed youth.',
                'apply_link': 'https://pmry.gov.in/',
                'eligibility': 'Educated unemployed youth',
                'benefits': 'Loans up to ₹1 lakh for self-employment'
            }
        ]
    },
    'family_welfare': {
        'title': 'Family Welfare',
        'icon': '👨‍👩‍👧‍👦',
        'count': '15',
        'schemes': [
            {
                'title': 'Beti Bachao Beti Padhao',
                'description': 'Initiative to save and educate the girl child.',
                'apply_link': 'https://wcd.nic.in/bbbp-schemes/',
                'eligibility': 'Girl children and their families',
                'benefits': 'Educational support and incentives'
            }
        ]
    }
}

@app.route('/chatbot', methods=['POST'])
@csrf.exempt
def chatbot():
    try:
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'error': 'Missing message parameter'}), 400

        user_message = data['message'].lower()
        
        # Get database connection for scheme queries
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500

        cursor = conn.cursor()
        
        # Basic response logic
        if 'hello' in user_message or 'hi' in user_message:
            return jsonify({
                'response': 'Hello! How can I help you find government schemes today?'
            })
            
        elif any(word in user_message for word in ['scheme', 'schemes']):
            return jsonify({
                'response': 'We have various categories of schemes. Which category interests you?\n- Education\n- Healthcare\n- Housing\n- Agriculture\n- Employment\n- Family Welfare'
            })
            
        elif 'eligibility' in user_message:
            return jsonify({
                'response': 'To check eligibility, please specify which scheme category you\'re interested in.'
            })
            
        else:
            return jsonify({
                'response': 'I\'m here to help you with government schemes. Would you like to:\n1. View all schemes\n2. Check eligibility\n3. Learn how to apply'
            })

    except Exception as e:
        print(f"Error in chatbot: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

    finally:
        if 'conn' in locals() and conn:
            conn.close()

    # Define category mappings
    category_urls = {
        'education': url_for('show_schemes', category='education'),
        'healthcare': url_for('show_schemes', category='healthcare'),
        'housing': url_for('show_schemes', category='housing'),
        'agriculture': url_for('show_schemes', category='agriculture'),
        'employment': url_for('show_schemes', category='employment'),
        'family welfare': url_for('show_schemes', category='family_welfare')
    }
    
    # Check if message contains category reference
    for category, url in category_urls.items():
        if category in user_message:
            return jsonify({
                'response': f"I'll take you to the {category} schemes page.",
                'redirect_url': url
            })
    
    # Regular chatbot responses
    if 'hello' in user_message or 'hi' in user_message:
        response = "Hello! I'm your BenefitHub Assistant. How can I help you today? You can ask me about:\n- Available schemes\n- Eligibility criteria\n- Application process\n- Document requirements"
    
    elif any(word in user_message for word in ['scheme', 'schemes', 'benefits']):
        response = "We have schemes in various categories. Click any category to view schemes:\n"
        for category in category_urls.keys():
            response += f"- {category.title()}\n"
        
        if 'education' in user_message:
            cursor.execute('SELECT title FROM schemes WHERE category_id = 1 LIMIT 3')
            schemes = cursor.fetchall()
            response = "Here are some educational schemes:\n" + "\n".join([f"- {scheme['title']}" for scheme in schemes])
            response += "\nWould you like to know more about any specific scheme?"
        
        elif 'health' in user_message:
            cursor.execute('SELECT title FROM schemes WHERE category_id = 2 LIMIT 3')
            schemes = cursor.fetchall()
            response = "Here are some healthcare schemes:\n" + "\n".join([f"- {scheme['title']}" for scheme in schemes])
            response += "\nWould you like to know more about any specific scheme?"
        
        else:
            response = "We have schemes in various categories:\n- Education & Scholarships\n- Healthcare\n- Housing\n- Agriculture\n- Employment\nWhich category interests you?"

    elif 'eligibility' in user_message:
        response = "Eligibility criteria vary by scheme. Could you specify which scheme or category you're interested in? I can help you check the specific requirements."

    elif 'document' in user_message:
        response = "Common documents required for most schemes include:\n- Aadhaar Card\n- Income Certificate\n- Domicile Certificate\n- Bank Account Details\nFor specific scheme requirements, please mention the scheme name."

    elif 'apply' in user_message:
        if not current_user.is_authenticated:
            response = "To apply for schemes, you'll need to login first. Would you like to:\n1. Login to your account\n2. Create a new account"
        else:
            response = "To apply, follow these steps:\n1. Select your scheme\n2. Check eligibility\n3. Upload documents\n4. Submit application\nWhich scheme would you like to apply for?"

    elif 'status' in user_message:
        if not current_user.is_authenticated:
            response = "Please login to check your application status."
        else:
            response = "You can check your application status in the 'My Applications' section of your dashboard. Would you like me to guide you there?"

    else:
        response = "I understand you're looking for information. To help you better, could you specify if you're interested in:\n1. Finding suitable schemes\n2. Checking eligibility\n3. Application process\n4. Document requirements"
    
    conn.close()
    return jsonify({'response': response})

@app.route('/login', methods=['POST'])
def login():
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember') == 'on'

        if not username or not password:
            return jsonify({'success': False, 'message': 'Please fill in all fields'})

        try:
            user = User.authenticate(username, password)
            if user:
                login_user(user, remember=remember)
                return jsonify({'success': True, 'message': 'Login successful!'})
            else:
                return jsonify({'success': False, 'message': 'Invalid username or password'})
        except Exception as e:
            print(f"Login error: {e}")
            return jsonify({'success': False, 'message': 'An error occurred during login'})

    return redirect(url_for('home'))

@app.route('/login/google')
def google_login():
    return google.authorize(callback=url_for('google_authorized', _external=True))

@app.route('/login/google/authorized')
def google_authorized():
    resp = google.authorized_response()
    if resp is None or resp.get('access_token') is None:
        return 'Access denied: reason={} error={}'.format(
            request.args['error_reason'],
            request.args['error_description']
        )
    
    google_user_info = google.get('userinfo').data
    email = google_user_info.get('email')
    username = email.split('@')[0]  # Use email prefix as username
    
    # Check if user exists, if not create new user
    user = User.get_by_email(email)
    if not user:
        user = User.create_google_user(username, email, google_user_info.get('id'))
    
    login_user(user)
    return redirect(url_for('home'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/register', methods=['POST'])
def register():
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if not all([username, email, password, confirm_password]):
            return jsonify({'success': False, 'message': 'Please fill in all fields'})

        if password != confirm_password:
            return jsonify({'success': False, 'message': 'Passwords do not match'})

        try:
            user = User.create(username, password, email)
            if user:
                login_user(user)
                return jsonify({'success': True, 'message': 'Registration successful!'})
            else:
                return jsonify({'success': False, 'message': 'Username or email already exists'})
        except Exception as e:
            print(f"Registration error: {e}")
            return jsonify({'success': False, 'message': 'An error occurred during registration'})

    return redirect(url_for('home'))

@app.route('/profile')
@login_required
def profile():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT created_at
        FROM users
        WHERE id = ?
    ''', (current_user.id,))
    
    user_info = cursor.fetchone()
    conn.close()
    
    return render_template('profile.html', user_info=user_info)
@app.route('/pragati-shramik-yojana')
def pragati_shramik_yojana():
    return render_template('pragati_shramik_yojana.html')
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/employment')
def employment():
    return render_template('employment.html')
# Add a route to populate the database with schemes
@app.route('/add-healthcare-schemes')
def add_healthcare_schemes():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get healthcare category ID
    cursor.execute('SELECT id FROM categories WHERE name = ?', ('healthcare',))
    category = cursor.fetchone()
    
    if not category:
        conn.close()
        return "Healthcare category not found. Please create it first."
    
    healthcare_id = category['id']
    
    # Healthcare schemes to add
    healthcare_schemes = [
        {
            "title": "Central Government Health Scheme (CGHS)",
            "description": "Provides comprehensive health care to central government employees, pensioners and their dependents.",
            "apply_link": "https://cghs.gov.in/",
            "eligibility": "Central government employees, pensioners and their dependents",
            "benefits": "Comprehensive healthcare services"
        },
        {
            "title": "National Health Mission (NHM)",
            "description": "Umbrella program for universal access to equitable, affordable and quality health care services.",
            "apply_link": "https://nhm.gov.in/",
            "eligibility": "All citizens",
            "benefits": "Improved healthcare access and quality"
        },
        {
            "title": "National AIDS Control Organisation (NACO)",
            "description": "Prevention and control of HIV/AIDS in India through awareness and treatment programs.",
            "apply_link": "http://naco.gov.in/",
            "eligibility": "All citizens, especially high-risk groups",
            "benefits": "HIV/AIDS prevention and treatment services"
        },
        {
            "title": "National Organ and Tissue Transplant Organisation (NOTTO)",
            "description": "National level organization for coordination and networking for procurement and distribution of organs and tissues.",
            "apply_link": "https://notto.gov.in/",
            "eligibility": "Patients requiring organ transplants",
            "benefits": "Organ donation and transplantation services"
        },
        {
            "title": "National Vector Borne Disease Control Programme (NVBDCP)",
            "description": "Prevention and control of vector borne diseases like Malaria, Dengue, etc.",
            "apply_link": "https://nvbdcp.gov.in/",
            "eligibility": "All citizens",
            "benefits": "Prevention and treatment of vector-borne diseases"
        },
        {
            "title": "Revised National Tuberculosis Control Programme (RNTCP)",
            "description": "Now known as National TB Elimination Programme (NTEP) for TB control and elimination.",
            "apply_link": "https://tbcindia.gov.in/",
            "eligibility": "TB patients and high-risk groups",
            "benefits": "Free TB diagnosis and treatment"
        },
        {
            "title": "National Mental Health Programme (NMHP)",
            "description": "Universal access to mental health care and psychological support.",
            "apply_link": "https://main.mohfw.gov.in/major-programmes/non-communicable-diseases-injury-trauma/mental-health-programme",
            "eligibility": "All citizens with mental health concerns",
            "benefits": "Mental health services and support"
        },
        {
            "title": "National Programme for Control of Blindness and Visual Impairment (NPCBVI)",
            "description": "Reduces the prevalence of blindness through early identification and treatment.",
            "apply_link": "https://npcbvi.gov.in/",
            "eligibility": "All citizens with vision problems",
            "benefits": "Eye care services and treatments"
        },
        {
            "title": "National Leprosy Eradication Programme (NLEP)",
            "description": "Early detection and treatment of leprosy cases for elimination of the disease.",
            "apply_link": "https://nlep.gov.in/",
            "eligibility": "Leprosy patients and high-risk groups",
            "benefits": "Free leprosy diagnosis and treatment"
        },
        {
            "title": "National Programme for Health Care of the Elderly (NPHCE)",
            "description": "Provides dedicated healthcare services to senior citizens.",
            "apply_link": "https://main.mohfw.gov.in/major-programmes/other-national-health-programmes/national-programme-health-care-elderly-nphce",
            "eligibility": "Senior citizens (60+ years)",
            "benefits": "Specialized healthcare for elderly"
        },
        {
            "title": "National Tobacco Control Programme (NTCP)",
            "description": "Implementation of tobacco control laws and awareness about tobacco hazards.",
            "apply_link": "https://ntcp.nhp.gov.in/",
            "eligibility": "All citizens, especially tobacco users",
            "benefits": "Tobacco cessation support and awareness"
        },
        {
            "title": "National Programme for Prevention and Control of Deafness (NPPCD)",
            "description": "Prevention, early identification and treatment of hearing impairments.",
            "apply_link": "https://dghs.gov.in/content/1362_3_NationalProgrammePreventionControl.aspx",
            "eligibility": "All citizens with hearing issues",
            "benefits": "Hearing assessment and treatment services"
        },
        {
            "title": "National Programme for Palliative Care (NPPC)",
            "description": "Provides palliative care for patients with chronic diseases.",
            "apply_link": "https://palliumindia.org/resources/national-programme",
            "eligibility": "Patients with chronic, terminal illnesses",
            "benefits": "Pain management and end-of-life care"
        },
        {
            "title": "National Viral Hepatitis Control Programme (NVHCP)",
            "description": "Prevention, diagnosis and treatment of viral hepatitis.",
            "apply_link": "https://nvhcp.gov.in/",
            "eligibility": "Hepatitis patients and high-risk groups",
            "benefits": "Hepatitis prevention and treatment"
        },
        {
            "title": "Rashtriya Bal Swasthya Karyakram (RBSK)",
            "description": "Child health screening and early intervention services.",
            "apply_link": "https://rbsk.gov.in/",
            "eligibility": "Children from birth to 18 years",
            "benefits": "Comprehensive child health screening"
        },
        {
            "title": "Rashtriya Kishor Swasthya Karyakram (RKSK)",
            "description": "Comprehensive health development program for adolescents.",
            "apply_link": "https://nhm.gov.in/index1.php?lang=1&level=3&sublinkid=1247&lid=421",
            "eligibility": "Adolescents (10-19 years)",
            "benefits": "Adolescent health services and counseling"
        },
        {
            "title": "Mission Indradhanush",
            "description": "Vaccination program to cover unvaccinated and partially vaccinated children.",
            "apply_link": "https://nhm.gov.in/index1.php?lang=1&level=2&sublinkid=824&lid=220",
            "eligibility": "Children under 2 years and pregnant women",
            "benefits": "Free vaccination against preventable diseases"
        },
        {
            "title": "Janani Suraksha Yojana (JSY)",
            "description": "Safe motherhood intervention promoting institutional delivery.",
            "apply_link": "https://nhm.gov.in/index1.php?lang=1&level=3&sublinkid=841&lid=309",
            "eligibility": "Pregnant women, especially from low-income families",
            "benefits": "Cash assistance for institutional delivery"
        },
        {
            "title": "Janani Shishu Suraksha Karyakram (JSSK)",
            "description": "Free ante-natal care, delivery, and post-natal care services.",
            "apply_link": "https://nhm.gov.in/index1.php?lang=1&level=3&sublinkid=842&lid=308",
            "eligibility": "Pregnant women and newborns",
            "benefits": "Free delivery and post-natal care"
        },
        {
            "title": "Poshan Abhiyaan",
            "description": "Multi-ministerial convergence mission for improvement in nutritional outcomes.",
            "apply_link": "https://poshanabhiyaan.gov.in/",
            "eligibility": "Children, pregnant women and lactating mothers",
            "benefits": "Nutritional support and counseling"
        }
    ]
    
    # Add family welfare schemes
    cursor.execute('SELECT id FROM categories WHERE name = ?', ('family_welfare',))
    family_welfare_category = cursor.fetchone()
    
    if family_welfare_category:
        family_welfare_id = family_welfare_category['id']
        
        family_welfare_schemes = [
            {
                "title": "Scheme 1",
                "description": "Description of Family Welfare Scheme 1",
                "apply_link": "/apply/family-welfare-1",
                "eligibility": "All families",
                "benefits": "Various family welfare benefits"
            },
            {
                "title": "Scheme 2",
                "description": "Description of Family Welfare Scheme 2",
                "apply_link": "/apply/family-welfare-2",
                "eligibility": "Low-income families",
                "benefits": "Financial assistance for families"
            }
        ]
        
        # Insert family welfare schemes
        for scheme in family_welfare_schemes:
            cursor.execute('''
                INSERT OR IGNORE INTO schemes 
                (category_id, title, description, apply_link, eligibility, benefits)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                family_welfare_id,
                scheme['title'],
                scheme['description'],
                scheme['apply_link'],
                scheme['eligibility'],
                scheme['benefits']
            ))
    
    # Insert healthcare schemes
    for scheme in healthcare_schemes:
        cursor.execute('''
            INSERT OR IGNORE INTO schemes 
            (category_id, title, description, apply_link, eligibility, benefits)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            healthcare_id,
            scheme['title'],
            scheme['description'],
            scheme['apply_link'],
            scheme['eligibility'],
            scheme['benefits']
        ))
    
    conn.commit()
    conn.close()
    
    return "Healthcare and Family Welfare schemes added successfully! <a href='/'>Go to Home</a>"

# Add a route to populate the database with family welfare schemes
@app.route('/add-family-welfare-schemes')
def add_family_welfare_schemes():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get family welfare category ID
    cursor.execute('SELECT id FROM categories WHERE name = ?', ('family_welfare',))
    category = cursor.fetchone()
    
    if not category:
        conn.close()
        return "Family Welfare category not found. Please create it first."
    
    family_welfare_id = category['id']
    
    # Family welfare schemes to add
    family_welfare_schemes = [
        {
            "title": "Pradhan Mantri Matru Vandana Yojana (PMMVY)",
            "description": "Maternity benefit program providing cash incentives to pregnant and lactating mothers.",
            "apply_link": "https://pmmvy-cas.nic.in/",
            "eligibility": "Pregnant women and lactating mothers for first child",
            "benefits": "Cash benefit of ₹5,000 in three installments"
        },
        {
            "title": "Beti Bachao Beti Padhao (BBBP)",
            "description": "Initiative to save and educate the girl child and improve gender equality.",
            "apply_link": "https://wcd.nic.in/bbbp-schemes/",
            "eligibility": "Girl children and their families",
            "benefits": "Educational support and awareness programs"
        },
        {
            "title": "Sukanya Samriddhi Yojana (SSY)",
            "description": "Small savings scheme for girl child education and marriage expenses.",
            "apply_link": "https://www.indiapost.gov.in/Financial/Pages/Content/Sukanya-Samriddhi-Account.aspx",
            "eligibility": "Parents of girl child below 10 years",
            "benefits": "High interest rate savings account with tax benefits"
        },
        {
            "title": "Integrated Child Development Services (ICDS)",
            "description": "Provides food, preschool education, and primary healthcare to children under 6 years and mothers.",
            "apply_link": "https://icds-wcd.nic.in/",
            "eligibility": "Children under 6 years and pregnant/lactating mothers",
            "benefits": "Supplementary nutrition, immunization, health check-ups"
        },
        {
            "title": "Pradhan Mantri Ujjwala Yojana (PMUY)",
            "description": "Provides LPG connections to women from Below Poverty Line households.",
            "apply_link": "https://pmuy.gov.in/",
            "eligibility": "Women from BPL households without LPG connection",
            "benefits": "Free LPG connection with financial assistance"
        },
        {
            "title": "Swadhar Greh Scheme",
            "description": "Provides shelter, food, clothing, and care to women in difficult circumstances.",
            "apply_link": "https://wcd.nic.in/schemes/swadhar-greh-scheme-women-difficult-circumstances",
            "eligibility": "Women in difficult circumstances without social and economic support",
            "benefits": "Temporary accommodation, food, clothing, counseling"
        },
        {
            "title": "One Stop Centre Scheme (Sakhi)",
            "description": "Supports women affected by violence in private and public spaces.",
            "apply_link": "https://sakhi.gov.in/",
            "eligibility": "Women affected by violence",
            "benefits": "Medical, legal, psychological support and temporary shelter"
        },
        {
            "title": "Women Helpline Scheme",
            "description": "24-hour emergency response to women affected by violence.",
            "apply_link": "https://wcd.nic.in/schemes/women-helpline-scheme-2",
            "eligibility": "Women in distress",
            "benefits": "Emergency response and rescue services"
        },
        {
            "title": "Mahila Shakti Kendra",
            "description": "Empowers rural women through community participation.",
            "apply_link": "https://wcd.nic.in/schemes/mahila-shakti-kendra",
            "eligibility": "Rural women",
            "benefits": "Skill development, employment, digital literacy"
        },
        {
            "title": "Pradhan Mantri Vaya Vandana Yojana (PMVVY)",
            "description": "Pension scheme for senior citizens providing assured pension.",
            "apply_link": "https://www.licindia.in/Products/Pension-Plans/Pradhan-Mantri-Vaya-Vandana-Yojana",
            "eligibility": "Senior citizens aged 60 years and above",
            "benefits": "Assured pension with 8% return for 10 years"
        },
        {
            "title": "National Family Benefit Scheme (NFBS)",
            "description": "Provides financial assistance to BPL families on death of primary breadwinner.",
            "apply_link": "https://nsap.nic.in/",
            "eligibility": "BPL families who have lost primary breadwinner",
            "benefits": "One-time financial assistance of ₹20,000"
        },
        {
            "title": "Rashtriya Mahila Kosh (RMK)",
            "description": "Provides micro-credit to poor women for income generation activities.",
            "apply_link": "https://rmk.nic.in/",
            "eligibility": "Poor women for self-employment",
            "benefits": "Micro-credit at concessional terms"
        },
        {
            "title": "Support to Training and Employment Programme (STEP)",
            "description": "Provides skills that give employability to women.",
            "apply_link": "https://wcd.nic.in/schemes/support-training-and-employment-programme-women-step",
            "eligibility": "Women above 16 years",
            "benefits": "Training for skills and employment"
        },
        {
            "title": "Mahila E-Haat",
            "description": "Online marketing platform for women entrepreneurs/SHGs.",
            "apply_link": "https://mahilaehaat-rmk.gov.in/",
            "eligibility": "Women entrepreneurs and Self Help Groups",
            "benefits": "Direct marketing platform without intermediaries"
        },
        {
            "title": "Working Women Hostel",
            "description": "Provides safe and affordable accommodation to working women.",
            "apply_link": "https://wcd.nic.in/schemes/working-women-hostel",
            "eligibility": "Working women and women students",
            "benefits": "Safe and affordable accommodation"
        }
    ]
    
    # Insert family welfare schemes
    for scheme in family_welfare_schemes:
        cursor.execute('''
            INSERT OR IGNORE INTO schemes 
            (category_id, title, description, apply_link, eligibility, benefits)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            family_welfare_id,
            scheme['title'],
            scheme['description'],
            scheme['apply_link'],
            scheme['eligibility'],
            scheme['benefits']
        ))
    
    conn.commit()
    conn.close()
    
    return "Family Welfare schemes added successfully! <a href='/'>Go to Home</a>"
# Add this route after your existing routes

@app.route('/agriculture')
def agriculture():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get agriculture category ID
    cursor.execute('SELECT id FROM categories WHERE name = ?', ('agriculture',))
    category = cursor.fetchone()
    
    if not category:
        conn.close()
        return "Agriculture category not found."
    
    agriculture_id = category['id']
    
    # Get all schemes for agriculture category
    cursor.execute('''
        SELECT id, title, description, apply_link, eligibility, benefits
        FROM schemes
        WHERE category_id = ?
    ''', (agriculture_id,))
    
    schemes = cursor.fetchall()
    conn.close()
    
    return render_template('agriculture.html', schemes=schemes)
# Add a route to populate the database with agriculture schemes
@app.route('/add-agriculture-schemes')
def add_agriculture_schemes():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get agriculture category ID
    cursor.execute('SELECT id FROM categories WHERE name = ?', ('agriculture',))
    category = cursor.fetchone()
    
    if not category:
        conn.close()
        return "Agriculture category not found. Please create it first."
    
    agriculture_id = category['id']
    
    # Agriculture schemes to add
    agriculture_schemes = [
        {
            "title": "Pradhan Mantri Kisan Samman Nidhi (PM-KISAN)",
            "description": "Income support scheme providing financial benefit to all landholding farmers' families in the country.",
            "apply_link": "https://pmkisan.gov.in/",
            "eligibility": "All landholding farmer families with cultivable land",
            "benefits": "₹6,000 per year in three equal installments"
        },
        {
            "title": "Pradhan Mantri Fasal Bima Yojana (PMFBY)",
            "description": "Crop insurance scheme providing comprehensive risk coverage for crops.",
            "apply_link": "https://pmfby.gov.in/",
            "eligibility": "Farmers growing notified crops in notified areas",
            "benefits": "Insurance coverage for crop loss due to natural calamities"
        },
        {
            "title": "Kisan Credit Card (KCC)",
            "description": "Provides farmers with affordable credit for their agricultural needs.",
            "apply_link": "https://www.pmkisan.gov.in/",
            "eligibility": "All farmers, sharecroppers, tenant farmers",
            "benefits": "Short-term credit for cultivation and other needs"
        },
        {
            "title": "Pradhan Mantri Krishi Sinchai Yojana (PMKSY)",
            "description": "Scheme to improve farm water management and irrigation facilities.",
            "apply_link": "https://pmksy.gov.in/",
            "eligibility": "Farmers in water-scarce areas",
            "benefits": "Improved irrigation facilities and water efficiency"
        },
        {
            "title": "Soil Health Card Scheme",
            "description": "Provides information on soil health to farmers to help improve productivity.",
            "apply_link": "https://soilhealth.dac.gov.in/",
            "eligibility": "All farmers",
            "benefits": "Soil health assessment and recommendations"
        },
        {
            "title": "National Mission for Sustainable Agriculture (NMSA)",
            "description": "Promotes sustainable agriculture through climate change adaptation measures.",
            "apply_link": "https://nmsa.dac.gov.in/",
            "eligibility": "Farmers in rain-fed and other vulnerable areas",
            "benefits": "Support for climate-resilient agricultural practices"
        },
        {
            "title": "Paramparagat Krishi Vikas Yojana (PKVY)",
            "description": "Promotes organic farming and improves soil health.",
            "apply_link": "https://pgsindia-ncof.gov.in/pkvy/index.aspx",
            "eligibility": "Farmers willing to adopt organic farming",
            "benefits": "Financial assistance for organic farming certification"
        },
        {
            "title": "National Food Security Mission (NFSM)",
            "description": "Aims to increase production of rice, wheat, pulses, coarse cereals and commercial crops.",
            "apply_link": "https://nfsm.gov.in/",
            "eligibility": "Farmers in identified districts",
            "benefits": "Financial assistance for increasing crop production"
        },
        {
            "title": "Mission for Integrated Development of Horticulture (MIDH)",
            "description": "Promotes holistic growth of horticulture sector including fruits, vegetables, and flowers.",
            "apply_link": "https://midh.gov.in/",
            "eligibility": "Farmers engaged in horticulture",
            "benefits": "Financial assistance for horticulture development"
        },
        {
            "title": "National Bamboo Mission (NBM)",
            "description": "Promotes holistic growth of bamboo sector by adopting area-based, regionally differentiated strategy.",
            "apply_link": "https://nbm.nic.in/",
            "eligibility": "Farmers and entrepreneurs in bamboo sector",
            "benefits": "Financial assistance for bamboo plantation and industry"
        },
        {
            "title": "Rashtriya Krishi Vikas Yojana (RKVY)",
            "description": "Ensures holistic development of agriculture and allied sectors.",
            "apply_link": "https://rkvy.nic.in/",
            "eligibility": "State governments and farmers",
            "benefits": "Financial assistance for agriculture infrastructure"
        },
        {
            "title": "Pradhan Mantri Annadata Aay Sanrakshan Abhiyan (PM-AASHA)",
            "description": "Ensures farmers receive remunerative prices for their produce.",
            "apply_link": "https://pmaaasha.gov.in/",
            "eligibility": "Farmers growing notified crops",
            "benefits": "Price support and market linkage"
        },
        {
            "title": "E-National Agriculture Market (e-NAM)",
            "description": "Online trading platform for agricultural commodities.",
            "apply_link": "https://enam.gov.in/",
            "eligibility": "Farmers registered with local mandis",
            "benefits": "Direct access to markets across India"
        },
        {
            "title": "Micro Irrigation Fund (MIF)",
            "description": "Facilitates states in mobilizing resources for expanding coverage of micro irrigation.",
            "apply_link": "https://pmksy.gov.in/microirrigation/index.aspx",
            "eligibility": "State governments and farmers",
            "benefits": "Financial assistance for micro irrigation projects"
        },
        {
            "title": "Agriculture Infrastructure Fund",
            "description": "Financing facility for investment in agriculture infrastructure projects.",
            "apply_link": "https://agriinfra.dac.gov.in/",
            "eligibility": "Farmers, FPOs, PACS, Agri-entrepreneurs",
            "benefits": "Interest subvention and credit guarantee for post-harvest infrastructure"
        }
    ]
    
    # Insert agriculture schemes
    for scheme in agriculture_schemes:
        cursor.execute('''
            INSERT OR IGNORE INTO schemes 
            (category_id, title, description, apply_link, eligibility, benefits)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            agriculture_id,
            scheme['title'],
            scheme['description'],
            scheme['apply_link'],
            scheme['eligibility'],
            scheme['benefits']
        ))
    
    conn.commit()
    conn.close()
    
    return "Agriculture schemes added successfully! <a href='/'>Go to Home</a>"

@app.route('/add-education-schemes')
def add_education_schemes():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get education category ID
    cursor.execute('SELECT id FROM categories WHERE name = ?', ('education',))
    category = cursor.fetchone()
    
    if not category:
        conn.close()
        return "Education category not found. Please create it first."
    
    education_id = category['id']
    
    # Education schemes to add
    education_schemes = [
        {
            "title": "National Scholarship Portal (NSP)",
            "description": "Single-window platform for various scholarship schemes offered by central and state governments.",
            "apply_link": "https://scholarships.gov.in/",
            "eligibility": "Students from economically weaker sections, minorities, and other specified categories",
            "benefits": "Financial assistance for education expenses"
        },
        {
            "title": "Prime Minister's Research Fellowship (PMRF)",
            "description": "Fellowship program for doctoral studies in IITs, IISERs, and other premier institutions.",
            "apply_link": "https://pmrf.in/",
            "eligibility": "Meritorious students pursuing PhD in STEM fields",
            "benefits": "Fellowship of ₹70,000-80,000 per month with research grant"
        },
        {
            "title": "Post Matric Scholarship for SC Students",
            "description": "Financial assistance to SC students for post-matriculation education.",
            "apply_link": "https://scholarships.gov.in/",
            "eligibility": "SC students whose parents' annual income is below ₹2.5 lakhs",
            "benefits": "Full reimbursement of tuition fees and maintenance allowance"
        },
        {
            "title": "Central Sector Scheme of Scholarships (CSSS)",
            "description": "Merit-based scholarships for college and university students.",
            "apply_link": "https://scholarships.gov.in/",
            "eligibility": "Students who scored above 80th percentile in Class 12",
            "benefits": "₹10,000 per annum for undergraduate studies"
        },
        {
            "title": "Pragati Scholarship for Girl Students",
            "description": "Scholarship scheme for girl students in technical education.",
            "apply_link": "https://www.aicte-pragati-saksham-gov.in/",
            "eligibility": "Girl students admitted to AICTE approved technical institutions",
            "benefits": "₹50,000 per annum and tuition fee reimbursement"
        },
        {
            "title": "Mid-Day Meal Scheme",
            "description": "School meal program to improve nutritional status of school-going children.",
            "apply_link": "https://mdm.nic.in/",
            "eligibility": "Children studying in Classes I-VIII in government schools",
            "benefits": "Free nutritious meal on all school days"
        }
    ]
    
    # Prepare data for insertion
    schemes_data = []
    for scheme in education_schemes:
        schemes_data.append((
            education_id,
            scheme["title"],
            scheme["description"],
            scheme["apply_link"],
            scheme.get("eligibility", ""),
            scheme.get("benefits", "")
        ))
    
    # Insert schemes
    try:
        cursor.executemany('''
        INSERT INTO schemes (category_id, title, description, apply_link, eligibility, benefits)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', schemes_data)
        conn.commit()
    except Exception as e:
        conn.close()
        return f"Error adding education schemes: {str(e)}"
    
    conn.close()
    return "Education schemes added successfully!"

@app.route('/')
def home():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get all categories
    cursor.execute('SELECT id, name, title, icon, scheme_count FROM categories')
    db_categories = cursor.fetchall()
    
    # Format categories with proper links
    categories = []
    for category in db_categories:
        categories.append({
            'id': category['id'],
            'name': category['name'],
            'title': category['title'],
            'icon': category['icon'],
            'count': category['scheme_count'],
            'link': f"/{category['name']}"  # This ensures proper URL format
        })
    
    # Get featured schemes (rest of your existing code)
    cursor.execute('''
        SELECT id, title, description, apply_link, eligibility, benefits
        FROM schemes
        WHERE title = 'Pragati Shramik Yojana'
        LIMIT 1
    ''')
    pragati_scheme = cursor.fetchone()
    
    # Get the BenefitHub Special Tourism Scheme
    cursor.execute('''
        SELECT id, title, description, apply_link, eligibility, benefits
        FROM schemes
        WHERE title = 'BenefitHub Special Tourism Scheme'
        LIMIT 1
    ''')
    tourism_scheme = cursor.fetchone()
    
    # Combine featured schemes
    featured_schemes = []
    if pragati_scheme:
        featured_schemes.append(pragati_scheme)
    if tourism_scheme:
        featured_schemes.append(tourism_scheme)
    
    # If no featured schemes found, get some random schemes
    if not featured_schemes:
        cursor.execute('''
            SELECT id, title, description, apply_link, eligibility, benefits
            FROM schemes
            LIMIT 2
        ''')
        featured_schemes = cursor.fetchall()
    
    conn.close()
    
    return render_template('index.html', categories=categories, schemes=featured_schemes)
@app.route('/education')
def education():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get education category ID
    cursor.execute('SELECT id FROM categories WHERE name = ?', ('education',))
    category = cursor.fetchone()
    
    if not category:
        conn.close()
        return "Education category not found."
    
    education_id = category['id']
    
    # Get all schemes for education category
    cursor.execute('''
        SELECT id, title, description, apply_link, eligibility, benefits
        FROM schemes
        WHERE category_id = ?
    ''', (education_id,))
    
    schemes = cursor.fetchall()
    conn.close()
    
    return render_template('education.html', schemes=schemes)
@app.route('/add-tourism-schemes')
def add_tourism_schemes():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get tourism category ID
    cursor.execute('SELECT id FROM categories WHERE name = ?', ('tourism',))
    category = cursor.fetchone()
    
    if not category:
        # Create tourism category if it doesn't exist
        cursor.execute('INSERT INTO categories (name, title, icon) VALUES (?, ?, ?)', 
                      ('tourism', 'Tourism & Travel', '🏝️'))
        conn.commit()
        cursor.execute('SELECT id FROM categories WHERE name = ?', ('tourism',))
        category = cursor.fetchone()
    
    tourism_id = category['id']
    
    # Tourism schemes to add
    tourism_schemes = [
        {
            "title": "BenefitHub Special Tourism Scheme",
            "description": "Exclusive scheme offering special travel packages and discounts for domestic tourism to promote local destinations and cultural heritage sites.",
            "apply_link": "https://benefithub.gov.in/special-tourism",
            "eligibility": "All Indian citizens with valid ID proof",
            "benefits": "Up to 50% discount on accommodation, transportation subsidies, and free guided tours at select heritage sites"
        },
        {
            "title": "Swadesh Darshan Scheme",
            "description": "Integrated development of theme-based tourist circuits in India.",
            "apply_link": "https://tourism.gov.in/schemes/swadesh-darshan",
            "eligibility": "State Governments, Union Territory Administrations, and other implementing agencies",
            "benefits": "Financial assistance for infrastructure development in tourist circuits"
        },
        {
            "title": "PRASHAD Scheme",
            "description": "Pilgrimage Rejuvenation and Spiritual, Heritage Augmentation Drive for development of pilgrimage destinations.",
            "apply_link": "https://tourism.gov.in/schemes/prashad",
            "eligibility": "State Governments and Union Territory Administrations",
            "benefits": "Financial support for infrastructure development at pilgrimage sites"
        },
        {
            "title": "Incredible India Tourist Facilitator Certification Programme",
            "description": "Online certification program for individuals to become tourist guides.",
            "apply_link": "https://iitf.gov.in/",
            "eligibility": "Indian citizens with educational qualification of 10+2 or above",
            "benefits": "Certification and training to become a professional tourist guide"
        },
        {
            "title": "Adopt a Heritage Project",
            "description": "Entrusts heritage sites to private and public companies for development and maintenance.",
            "apply_link": "https://adoptaheritage.in/",
            "eligibility": "Private and Public Sector Companies, Individuals",
            "benefits": "Recognition and visibility for corporate social responsibility"
        },
        {
            "title": "DG Shipping Cruise Tourism Incentive Scheme",
            "description": "Provides financial incentives to cruise lines operating in India.",
            "apply_link": "https://www.dgshipping.gov.in/",
            "eligibility": "Cruise lines operating in Indian waters",
            "benefits": "Reduced port charges and financial incentives"
        },
        {
            "title": "Dekho Apna Desh Initiative",
            "description": "Promotes domestic tourism through webinars, quizzes, and pledge campaigns.",
            "apply_link": "https://dekhoappnadesh.gov.in/",
            "eligibility": "All Indian citizens",
            "benefits": "Recognition and certificates for visiting multiple tourist destinations"
        }
    ]
    
    # Prepare data for insertion
    schemes_data = []
    for scheme in tourism_schemes:
        schemes_data.append((
            tourism_id,
            scheme["title"],
            scheme["description"],
            scheme["apply_link"],
            scheme.get("eligibility", ""),
            scheme.get("benefits", "")
        ))
    
    # Insert schemes
    try:
        cursor.executemany('''
        INSERT INTO schemes (category_id, title, description, apply_link, eligibility, benefits)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', schemes_data)
        conn.commit()
    except Exception as e:
        conn.close()
        return f"Error adding tourism schemes: {str(e)}"
    
    conn.close()
    return "Tourism schemes added successfully! <a href='/tourism'>View Tourism Schemes</a>"
    # Rest of the function remains the same
    # ...

@app.route('/add-tourism-category')
def add_tourism_category():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if tourism category already exists
    cursor.execute('SELECT id FROM categories WHERE name = ?', ('tourism',))
    category = cursor.fetchone()
    
    if not category:
        # Add tourism category with only the columns that exist in your table
        # Assuming your categories table has name, title, and icon columns
        cursor.execute('''
        INSERT INTO categories (name, title, icon)
        VALUES (?, ?, ?)
        ''', ('tourism', 'Tourism & Travel', '🏝️'))
        conn.commit()
        result = "Tourism category added successfully! <a href='/'>Go to Home</a>"
    else:
        result = "Tourism category already exists. <a href='/'>Go to Home</a>"
    
    conn.close()
    return result
@app.route('/tourism')
def tourism():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get tourism category ID
    cursor.execute('SELECT id FROM categories WHERE name = ?', ('tourism',))
    category = cursor.fetchone()
    
    if not category:
        # Create tourism category if it doesn't exist
        cursor.execute('INSERT INTO categories (name, title, icon) VALUES (?, ?, ?)', 
                      ('tourism', 'Tourism & Travel', '🏝️'))
        conn.commit()
        cursor.execute('SELECT id FROM categories WHERE name = ?', ('tourism',))
        category = cursor.fetchone()
    
    tourism_id = category['id']
    
    # Get all schemes for tourism category
    cursor.execute('''
        SELECT id, title, description, apply_link, eligibility, benefits
        FROM schemes
        WHERE category_id = ?
    ''', (tourism_id,))
    
    schemes = cursor.fetchall()
    conn.close()
    
    return render_template('tourism.html', schemes=schemes)
# Add a route to populate the database with housing schemes

@app.route('/add-housing-schemes')
def add_housing_schemes():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get housing category ID
    cursor.execute('SELECT id FROM categories WHERE name = ?', ('housing',))
    category = cursor.fetchone()
    
    if not category:
        conn.close()
        return "Housing category not found. Please create it first."
    
    housing_id = category['id']
    
    # Housing schemes to add
    housing_schemes = [
        {
            "title": "Pradhan Mantri Awas Yojana - Urban (PMAY-U)",
            "description": "Housing for All Mission that provides central assistance to Urban Local Bodies and other implementing agencies for affordable housing to urban poor.",
            "apply_link": "https://pmaymis.gov.in/",
            "eligibility": "Urban poor belonging to EWS/LIG/MIG categories",
            "benefits": "Interest subsidy up to ₹2.67 lakhs and direct financial assistance"
        },
        {
            "title": "Pradhan Mantri Awas Yojana - Gramin (PMAY-G)",
            "description": "Provides financial assistance for construction of pucca houses for rural homeless and those living in dilapidated houses.",
            "apply_link": "https://pmayg.nic.in/",
            "eligibility": "Rural households living in kutcha/dilapidated houses",
            "benefits": "Financial assistance of ₹1.20 lakh to ₹1.30 lakh per house"
        },
        {
            "title": "Credit Linked Subsidy Scheme (CLSS)",
            "description": "Interest subsidy on home loans for EWS, LIG and MIG categories under PMAY-Urban.",
            "apply_link": "https://pmaymis.gov.in/",
            "eligibility": "EWS, LIG and MIG households with annual income up to ₹18 lakhs",
            "benefits": "Interest subsidy of 3-6.5% on home loans"
        },
        {
            "title": "Affordable Housing in Partnership (AHP)",
            "description": "Provides financial assistance to private developers for affordable housing projects.",
            "apply_link": "https://pmaymis.gov.in/",
            "eligibility": "EWS category with annual income up to ₹3 lakhs",
            "benefits": "Central assistance of ₹1.5 lakh per EWS house"
        },
        {
            "title": "Beneficiary-led Construction (BLC)",
            "description": "Financial assistance to individual eligible families for construction of houses.",
            "apply_link": "https://pmaymis.gov.in/",
            "eligibility": "EWS families with land ownership",
            "benefits": "Central assistance of ₹1.5 lakh per house"
        },
        {
            "title": "In-situ Slum Redevelopment (ISSR)",
            "description": "Uses land as resource for providing houses to slum dwellers.",
            "apply_link": "https://pmaymis.gov.in/",
            "eligibility": "Slum dwellers",
            "benefits": "Central assistance of ₹1 lakh per house"
        },
        {
            "title": "Deendayal Antyodaya Yojana - National Urban Livelihoods Mission (DAY-NULM)",
            "description": "Provides shelter for urban homeless through construction of shelters.",
            "apply_link": "https://nulm.gov.in/",
            "eligibility": "Urban homeless",
            "benefits": "Shelter with basic amenities"
        },
        {
            "title": "Rajiv Awas Yojana (RAY)",
            "description": "Aims at providing housing to slum dwellers and preventing new slums.",
            "apply_link": "https://mohua.gov.in/",
            "eligibility": "Slum dwellers in 2,613 cities/towns",
            "benefits": "Affordable housing with basic amenities"
        },
        {
            "title": "Rental Housing Scheme",
            "description": "Affordable Rental Housing Complexes (ARHCs) for urban migrants/poor.",
            "apply_link": "https://arhc.mohua.gov.in/",
            "eligibility": "Urban migrants/poor from EWS/LIG categories",
            "benefits": "Affordable rental housing with basic amenities"
        },
        {
            "title": "Working Women Hostel Scheme",
            "description": "Promotes availability of safe and conveniently located accommodation for working women.",
            "apply_link": "https://wcd.nic.in/schemes/working-women-hostel",
            "eligibility": "Working women with income up to ₹50,000 per month",
            "benefits": "Safe and affordable accommodation"
        },
        {
            "title": "Indira Awaas Yojana (IAY)",
            "description": "Predecessor to PMAY-G, provides housing for rural poor.",
            "apply_link": "https://rural.nic.in/",
            "eligibility": "BPL families in rural areas",
            "benefits": "Financial assistance for house construction"
        },
        {
            "title": "National Urban Housing Fund (NUHF)",
            "description": "Extra-budgetary resource for PMAY-Urban to meet fund requirements.",
            "apply_link": "https://mohua.gov.in/",
            "eligibility": "Implementing agencies of PMAY-U",
            "benefits": "Financial support for affordable housing projects"
        },
        {
            "title": "Atal Mission for Rejuvenation and Urban Transformation (AMRUT)",
            "description": "Provides basic services including housing to households and build amenities in cities.",
            "apply_link": "https://amrut.gov.in/",
            "eligibility": "Urban areas selected under AMRUT",
            "benefits": "Improved urban infrastructure including housing"
        },
        {
            "title": "Smart Cities Mission",
            "description": "Promotes cities that provide core infrastructure including affordable housing.",
            "apply_link": "https://smartcities.gov.in/",
            "eligibility": "Cities selected under Smart Cities Mission",
            "benefits": "Improved housing and urban infrastructure"
        },
        {
            "title": "Pradhan Mantri Gramin Awaas Yojana (PMGAY)",
            "description": "Aims to provide housing for the rural poor in India.",
            "apply_link": "https://pmayg.nic.in/",
            "eligibility": "Rural households living in kutcha/dilapidated houses",
            "benefits": "Financial assistance for house construction"
        }
    ]
    
    # Insert housing schemes
    for scheme in housing_schemes:
        cursor.execute('''
            INSERT OR IGNORE INTO schemes 
            (category_id, title, description, apply_link, eligibility, benefits)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            housing_id,
            scheme['title'],
            scheme['description'],
            scheme['apply_link'],
            scheme['eligibility'],
            scheme['benefits']
        ))
    
    conn.commit()
    conn.close()
    
    return "Housing schemes added successfully! <a href='/'>Go to Home</a>"


# Initialize OAuth before the app runs
oauth = OAuth(app)

# This should be the last part of your file

# Initialize OAuth before the app runs
oauth = OAuth(app)

google = oauth.remote_app(
    'google',
    consumer_key='YOUR_GOOGLE_CLIENT_ID',  # Replace with your Google Client ID
    consumer_secret='YOUR_GOOGLE_CLIENT_SECRET',  # Replace with your Google Client Secret
    request_token_params={
        'scope': 'email profile'
    },
    base_url='https://www.googleapis.com/oauth2/v1/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth'
)

# This should be the last part of your file
if __name__ == '__main__':
    app.run(debug=True)



   