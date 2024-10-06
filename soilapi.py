import streamlit as st
import google.generativeai as genai
import os
import re

# Configure the API key
os.environ['GOOGLE_API_KEY'] = "AIzaSyDE1vp33z8kjpf0AlbPmmzRm9aougE0oLM"

genai.configure(api_key=os.environ["GOOGLE_API_KEY"])  # Replace YOUR_API_KEY with your actual API key

# Set the title of the app
st.title("Agriculture Chatbot")

# Create a text input for user questions
user_input = st.text_input("Ask a question about agriculture:")

# Function to check if the question is related to agriculture
def is_agriculture_related(question):
    # Define a simple pattern to match agriculture-related terms
    agriculture_keywords = r'\b(agriculture|farming|crops|soil|irrigation|pesticides|fertilizers|livestock|harvest|sustainability|agronomy|horticulture|agricultural technology)\b'
    return bool(re.search(agriculture_keywords, question, re.IGNORECASE))

# Function to call the Gemini API
def generate_response(prompt):
    model = genai.GenerativeModel(model_name="gemini-1.5-flash")
    response = model.generate_content(prompt)
    return response.text

# Check if user input is provided
if user_input:
    # Validate the user input
    if is_agriculture_related(user_input):
        # Generate a response from the AI model
        response = generate_response(user_input)
        
        # Display the response
        st.write("**AI Response:**")
        st.write(response)
    else:
        # Provide a response indicating the topic is out of scope
        st.write("**AI Response:** Sorry, I can only answer questions related to agriculture. Please ask something about farming, crops, soil, irrigation, or related topics.")