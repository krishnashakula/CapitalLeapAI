import streamlit as st
import sqlite3
from streamlit import secrets

# Create a connection to the SQLite database
conn = sqlite3.connect('user_credentials.db')
c = conn.cursor()

# Create a table for storing user credentials if it doesn't exist
c.execute('''CREATE TABLE IF NOT EXISTS users
             (username TEXT PRIMARY KEY, password TEXT)''')
conn.commit()

# Function to validate user credentials
def validate_user(username, password):
    c.execute("SELECT password FROM users WHERE username=?", (username,))
    saved_password = c.fetchone()
    if saved_password:
        return secrets.compare_hashes(password, saved_password[0])
    return False

# Function to register a new user
def register_user(username, password):
    try:
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, secrets.hash(password)))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False  # User already exists

# Login form displayed in the sidebar
def login_form():
    with st.sidebar:
        st.title("Login")
        username = st.text_input("Username", key="login")
        password = st.text_input("Password", type="password", key="login_pass")
        login_button = st.button("Login")
        if login_button:
            if validate_user(username, password):
                st.session_state.logged_in = True
                st.success("Logged in successfully.")
            else:
                st.error("Login failed. Incorrect username or password.")
        if st.button("Sign up"):
            st.session_state.show_signup = True  # Show sign-up form upon request.

# Sign-up form
def sign_up_form():
    with st.sidebar:
        st.title("Create an Account")
        new_username = st.text_input("Choose a Username", key="new_user")
        new_password = st.text_input("Choose a Password", type="password", key="new_pass")
        confirm_password = st.text_input("Confirm Password", type="password", key="confirm_pass")
        sign_up_button = st.button("Sign Up")
        if sign_up_button:
            if new_password != confirm_password:
                st.error("Passwords do not match.")
            elif register_user(new_username, new_password):
                st.success("Account created successfully. You can log in now.")
                st.session_state.show_signup = False  # Hide sign-up form after successful registration.
            else:
                st.error("Username already exists. Please choose a different one.")

# Risk assessment function incorporating the detailed questions provided
def risk_assessment():
    st.title("Risk Appetite Assessment")
    st.write("Please answer the following questions to assess your risk appetite:")
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
        # Placeholder for the calculation of the weighted score based on responses
        st.success("Your risk profile has been calculated. (Implement calculation logic based on responses.)")

# Main app logic
if 'logged_in' in st.session_state and st.session_state.logged_in:
    risk_assessment()
elif 'show_signup' in st.session_state and st.session_state.show_signup:
    sign_up_form()
else:
    login_form()
