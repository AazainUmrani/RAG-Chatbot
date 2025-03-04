import mysql.connector
from mysql.connector import Error
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from google import genai
import requests
import os
from django.contrib.auth.models import User  # Import Django's User model
from .models import ChatHistory  # Import the ChatHistory model

client = genai.Client(api_key=os.getenv("GENAI_API_KEY"))
model_id = "sentence-transformers/all-mpnet-base-v2"
hf_token = os.getenv("HF_API_TOKEN")
api_url = f"https://api-inference.huggingface.co/pipeline/feature-extraction/{model_id}"
headers = {"Authorization": f"Bearer {hf_token}"}

def query(text):
    response = requests.post(api_url, headers=headers, json={"inputs": text, "options": {"wait_for_model": True}})
    return response.json()

def fetch_embeddings_from_mysql():
    try:
        db = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="12344321",
            database="testDatabase"
        )
        cursor = db.cursor()
        fetch_query = "SELECT heading, embedding, content FROM embeddings"
        cursor.execute(fetch_query)
        results = cursor.fetchall()
        return results
    except Error as e:
        print(f"Error: {e}")
    finally:
        if db.is_connected():
            cursor.close()
            db.close()

def find_most_similar(question_embedding, embeddings_data):
    max_similarity = -1
    most_similar_heading = None
    most_similar_content = None

    for heading, embedding_json, content in embeddings_data:
        embedding = eval(embedding_json)
        similarity = cosine_similarity([question_embedding], [embedding])[0][0]
        if similarity > max_similarity:
            max_similarity = similarity
            most_similar_heading = heading
            most_similar_content = content

    if max_similarity < 0.3:
        most_similar_heading = " "
        most_similar_content = " "
    return most_similar_heading, most_similar_content, max_similarity

def GeminiResponse(question, instruction_prompt):
    response = client.models.generate_content(
        model="gemini-2.0-flash", contents=question + instruction_prompt
    )
    return response.text

def get_chatbot_response(question, user):
    print("Hello here is the question :", question)

    # Fetch the user's last 5 messages from the database
    user_chat_history = ChatHistory.objects.filter(user=user).order_by('-timestamp')[:5]
    user_conversation_history = [{"role": chat.role, "content": chat.message} for chat in user_chat_history]

    question_embedding = query(question)  # Pass question as a string

    if question_embedding is None:
        return {"error": "Failed to retrieve embeddings from Hugging Face API"}

    embeddings_data = fetch_embeddings_from_mysql()
    if not embeddings_data:
        return {"error": "No embeddings found in the database"}

    most_similar_heading, most_similar_content, similarity_score = find_most_similar(question_embedding, embeddings_data)

    instruction_prompt = f'''
    You are a helpful, friendly, and strictly controlled customer service chatbot exclusively for InterSys Limited. Your ONLY purpose is to assist users with questions DIRECTLY related to InterSys Limited's products, services, internal operations, technological infrastructure, and information derived from our current conversation. You must NOT answer questions about other companies, general knowledge, personal opinions, or anything else that does not pertain specifically to InterSys Limited. If a user asks a question outside of this scope, politely decline to answer and suggest they try searching online for that information. Avoid phrases like "Based on the context". Respond naturally, as if you are a human customer representative.
    **Conversation History:**
    {user_conversation_history}  # Show the user's last 5 messages
    **Relevant Context:**
    {most_similar_heading + most_similar_content}
    **Current Query:**
    {question}
    '''

    print("Similarity Score: ", similarity_score, instruction_prompt)
    response = GeminiResponse(question, instruction_prompt)

    # Save the user's message and the bot's response to the database
    ChatHistory.objects.create(user=user, message=question, role='user')
    ChatHistory.objects.create(user=user, message=response, role='assistant')

    return response