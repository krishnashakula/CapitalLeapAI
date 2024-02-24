import streamlit as st

import sqlite3

def get_db_connection():
    conn = sqlite3.connect('user_data.db')
    conn.row_factory = sqlite3.Row
    return conn


def create_user_table():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL
        );
    ''')
    conn.commit()
    conn.close()

# Function to register a new user
def register_user(username, password):
    try:
        conn = get_db_connection()
        conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False 

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'show_signup' not in st.session_state:
    st.session_state['show_signup'] = False
if 'user_db' not in st.session_state:
    st.session_state['user_db'] = {'admin': 'password'} 


# Function to validate user credentials
def validate_user(username, password):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()
    return user is not None and user["password"] == password


# Login form
def login_form():
    with st.sidebar.form("login_form"):
        st.write("Login")
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        login_button = st.form_submit_button("Login")
        
        if login_button:
            if validate_user(username, password):
                st.session_state.logged_in = True
                st.session_state.current_user = username
                st.rerun()
            else:
                st.error("Incorrect username or password.")
                st.session_state.show_signup = True

# Sign-up form
def sign_up_form():
    with st.sidebar.form("sign_up_form"):
        st.write("Sign Up")
        new_username = st.text_input("New Username", key="signup_username")
        new_password = st.text_input("New Password", type="password", key="signup_password")
        sign_up_button = st.form_submit_button("Sign Up")
        
        if sign_up_button:
            if register_user(new_username, new_password):
                st.success(f"User {new_username} created successfully.")
                st.session_state.logged_in = True
                st.session_state.current_user = new_username
                st.rerun()
            else:
                st.error("Username already exists.")

# Risk assessment function
def risk_assessment():
    st.title(f"Risk Appetite Assessment for {st.session_state.current_user}")

    # Define the questions and their associated weights
    questions = {
        "General Risk Appetite": ("Rate your willingness to take financial risks for high returns on a scale from 1 to 5, with 1 being low and 5 being high.", 2),
        "Specific Risk Tolerance": ("Given a 50% chance to either gain or lose 10% of your investment, rate your likely reaction on a scale from 1 to 5, with 1 being very unwilling and 5 being very willing.", 2),
        "Experience with Loss": ("Describe a past financial loss and how it has impacted your investment decisions.", 1.5),
        "Investment Horizon": ("Rate your focus on investment time horizon: 1 for short-term, 2 for medium-term, and 3 for long-term.", 1),
        "Financial Goals and Priorities": ("Describe your primary financial goals and their priority.", 1.5),
        "Comfort with Volatility": ("On a scale from 1 to 5, how comfortable are you with fluctuations in the value of your investments?", 2),
        "Risk vs. Reward": ("What's more important to you: protecting your investment from losses (1) or maximizing gains (5)?", 2),
        "Diversification Preferences": ("Rate your preference for diversifying investments to spread risk on a scale from 1 to 5.", 1),
        "Reaction to Market Downturns": ("If the market downturns and your portfolio loses value, what would be your immediate reaction? Sell (1), Hold (3), or Buy more (5)?", 2),
        "Sacrifice for Potential Gains": ("How much of your current lifestyle would you be willing to sacrifice for higher future gains, on a scale from 1 to 5?", 1.5)
    }

    responses = {}
    for question, (prompt, weight) in questions.items():
        if "Describe" in prompt or "Describe" in question:
            answer = st.text_area(prompt, key=question)
        elif "time horizon" in prompt.lower():
            answer = st.select_slider(prompt, options=[1, 2, 3], key=question)
        else:
            answer = st.slider(prompt, 1, 5, key=question)
        responses[question] = (answer, weight)

    if st.button('Calculate Risk Tolerance'):
        normalized_score = calculate_weighted_score(responses, questions)
        SYMBOLS_STOCKS = ["MSFT", "Apple Inc.", "Nvidia Corp", "Amazon.com Inc", "Meta Platforms, Inc. Class A",
        "Alphabet Inc. Class A" ]
        SYMBOLS_CRYPTOS = ["Bitcoin", "Ethereum" ,"Solana",
     "XRP", "USDC", "Cardano", "ADA", "Avalanche", "AVAX", "Dogecoin"] 

        risk_tolerance = "Low" if normalized_score <= 40 else "Moderate" if normalized_score <= 70 else "High"
        st.subheader(f"Your Risk Tolerance: {risk_tolerance}")
        st.write(f"Normalized Score: {normalized_score:.2f}")
        if risk_tolerance == "Low":
            st.write("Based on your low risk tolerance, we suggest a conservative investment portfolio. Consider allocating a higher percentage to bonds (70-80%) about $7000 to  $8000, with the remainder split between stocks (15-25%) such as", ", ".join(SYMBOLS_STOCKS[0:2]), " and a very small portion in cryptocurrencies (0-5%) for diversification.")
        elif risk_tolerance == "Moderate":
            st.write("With a moderate risk tolerance, a balanced investment portfolio could be ideal. You might consider distributing your investments across bonds (40-50%) around $4500 to $5000, stocks such as ", ", ".join(SYMBOLS_STOCKS[0:4]), " (40-50%), and a small but slightly higher allocation to cryptocurrencies (5-10%) like ", ", ".join(SYMBOLS_CRYPTOS[0:2]), " to add potential for higher returns.")
        elif risk_tolerance == "High":
            st.write("Given your high risk tolerance, you may pursue a more aggressive investment strategy. This could involve a larger allocation to stocks  such as ", ", ".join(SYMBOLS_STOCKS[0:4]), "(60-70%), complemented by investments in cryptocurrencies (10-20%) in ", ", ".join(SYMBOLS_CRYPTOS[0:2]), "  for high growth potential, and a smaller portion in bonds (10-20%) or $2000 for some stability.")
        

# Define the function to calculate the weighted score
def calculate_weighted_score(responses, questions):
    total_score = 0
    total_weight = sum(weight for _, weight in questions.values())
    
    for question, (answer, weight) in responses.items():
        score = sentiment_analysis(answer) if isinstance(answer, str) else answer
        total_score += score * weight
    
    return (total_score / (total_weight * 5)) * 100

# Function for sentiment analysis (placeholder for actual analysis)
def sentiment_analysis(text):
    positive_keywords = ['positive', 'good', 'learned', 'valuable', 'beneficial']
    negative_keywords = ['negative', 'bad', 'loss', 'lost', 'hurt', 'harmful']
    
    positive_score = sum(word in text.lower() for word in positive_keywords)
    negative_score = sum(word in text.lower() for word in negative_keywords)
    
    return 4 if positive_score > negative_score else 2 if negative_score > positive_score else 3

# Initialize session state variables
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'show_signup' not in st.session_state:
    st.session_state.show_signup = False
if 'current_user' not in st.session_state:
    st.session_state.current_user = ''

# Main app logic
def main():
    # Check if the user is logged in
    if st.session_state.get('logged_in', False):
        # User is logged in, show the risk assessment or other secured content
        risk_assessment()
    elif st.session_state.get('show_signup', False):
        # Show the sign-up form if the user chooses to sign up
        sign_up_form()
    else:
        # Default to showing the login form
        login_form()

# Ensure the main logic is called to execute the app
main()
create_user_table()  # Ensure the users table exists
