import streamlit as st

# Define the sentiment analysis function
def sentiment_analysis(text):
    positive_keywords = ['positive', 'good', 'learned', 'valuable', 'beneficial']
    negative_keywords = ['negative', 'bad', 'loss', 'lost', 'hurt', 'harmful']
    
    positive_score = sum(word in text.lower() for word in positive_keywords)
    negative_score = sum(word in text.lower() for word in negative_keywords)
    
    return 4 if positive_score > negative_score else 2 if negative_score > positive_score else 3

# Define the function to calculate the weighted score
def calculate_weighted_score(responses, questions):
    total_score = 0
    total_weight = sum(weight for _, weight in questions.values())
    
    for question, (answer, weight) in zip(questions.keys(), responses):
        score = sentiment_analysis(answer) if isinstance(answer, str) else answer
        total_score += score * weight
    
    return (total_score / (total_weight * 5)) * 100

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


# Streamlit app starts here
st.title("Risk Appetite Assessment")

responses = []

# Iterate through the questions and use appropriate Streamlit widgets to collect responses
for question, (prompt, weight) in questions.items():
    if "Describe" in prompt or "Describe" in question:
        answer = st.text_area(prompt, key=question)
    elif "time horizon" in prompt.lower():
        # Special case for the time horizon as it only has 3 options
        answer = st.select_slider(prompt, options=[1, 2, 3], key=question)
    else:
        answer = st.slider(prompt, 1, 5, key=question)
    responses.append((answer, weight))

# When the user clicks the 'Calculate' button, compute the risk tolerance
if st.button('Calculate Risk Tolerance'):
    normalized_score = calculate_weighted_score(responses, questions)
    risk_tolerance = "Low" if normalized_score <= 40 else "Moderate" if normalized_score <= 70 else "High"
    st.subheader(f"Your Risk Tolerance: {risk_tolerance}")
    st.write(f"Normalized Score: {normalized_score:.2f}")

# To run this Streamlit app, save the script as a .py file and run it using the command: streamlit run your_script.py 
