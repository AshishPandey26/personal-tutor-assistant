import streamlit as st
import os
import pandas as pd
from io import StringIO
from dotenv import load_dotenv

# from langchain.text_splitter import RecursiveCharacterTextSplitter

from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain.chains.question_answering import load_qa_chain
from langchain_community.vectorstores import FAISS
from langchain_community.vectorstores import FAISS
from langchain.prompts import PromptTemplate
import google.generativeai as genai

# Load API key
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Step 1: Read and clean text from CSV
def get_csv_text(csv_file):
    stringio = StringIO(csv_file.getvalue().decode("utf-8"))
    df = pd.read_csv(stringio)
    combined_text = ""

    for _, row in df.iterrows():
        class_ = str(row.get("Class", ""))
        subject = str(row.get("Subject", ""))
        unit = str(row.get("Unit Number", ""))
        chapter = str(row.get("Chapter Number", ""))
        chapter_name = str(row.get("Chapter Name", ""))
        topics = str(row.get("Chapter Topics", ""))

        combined_text += f"""
Class: {class_}
Subject: {subject}
Unit: {unit}
Chapter: {chapter} - {chapter_name}
Topics: {topics}

"""
    return combined_text

# Step 2: Chunk the text
def get_text_chunks(text):
    splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=1000)
    return splitter.split_text(text)

# Step 3: Build vector store
def get_vector_store(chunks):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vector_store = FAISS.from_texts(chunks, embedding=embeddings)
    vector_store.save_local("faiss_index")

# Step 4: Setup prompt chain
def get_conversational_chain():
    prompt_template = """
You are a helpful study assistant.
Based on the academic syllabus provided, generate accurate responses to the user’s question.
Stick to the relevant chapters, units, and topics from the content.

Context:
{context}

Question:
{question}

Answer:
"""
    model = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
    return load_qa_chain(model, chain_type="stuff", prompt=prompt)

# Step 5: Run user query
def user_input(user_question):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
    docs = db.similarity_search(user_question)

    chain = get_conversational_chain()
    response = chain({"input_documents": docs, "question": user_question}, return_only_outputs=True)
    st.write("Reply:", response["output_text"])

# Step 6: Streamlit UI
def main():
    st.set_page_config("Ask Syllabus Anything 📚")
    st.header("Ask Your Syllabus 🧠")

    with st.sidebar:
        st.title("Upload CSV 📄")
        csv_doc = st.file_uploader("Upload structured syllabus CSV", type="csv")

        if st.button("Process CSV") and csv_doc:
            with st.spinner("Reading and indexing CSV..."):
                csv_text = get_csv_text(csv_doc)
                chunks = get_text_chunks(csv_text)
                get_vector_store(chunks)
                st.success("CSV indexed. You can now ask questions.")

    user_question = st.text_input("What do you want to ask?")
    if user_question:
        user_input(user_question)

if __name__ == "__main__":
    main()
