import streamlit as st
import os
import shutil
import io
from dotenv import load_dotenv
from main import fetch_news
from fastapi import HTTPException

# LangChain & Vector DB imports
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
import google.generativeai as genai
from gtts import gTTS

# Load environment variables
load_dotenv()

# Configure Streamlit page
st.set_page_config(page_title="News AI Chat", page_icon="📰", layout="wide")
st.title("📰 Smart News Chat with Streamlit and LangChain")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Check for Google API Key
if "GOOGLE_API_KEY" not in os.environ:
    st.error("Please add GOOGLE_API_KEY to your .env file.")
    st.stop()

genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

# Sidebar for fetching news
with st.sidebar:
    st.header("Configuration")
    
    # Dynamic Model Selection: Fetch available models from Google
    try:
        model_options = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods and 'gemini' in m.name:
                model_options.append(m.name.replace("models/", ""))
        if not model_options:
            model_options = ["gemini-1.5-flash", "gemini-pro"]
    except Exception:
        model_options = ["gemini-1.5-flash", "gemini-pro"]

    selected_model = st.selectbox("Select AI Model", model_options, index=0)
    
    country = st.selectbox("Country", ["in", "us", "gb", "au"], index=0)
    category = st.selectbox("Category", ["general", "technology", "business", "sports", "science", "health", "entertainment"], index=1)
    
    if st.button("Fetch & Index News"):
        with st.spinner("Fetching news and updating Vector DB..."):
            # Reset chat history when new news is fetched to avoid context mismatch
            st.session_state.messages = []
            try:
                # 1. Fetch News using existing logic from main.py
                news_data = fetch_news(country, category)
                articles = news_data.get("articles", [])
                
                if not articles:
                    st.warning("No articles found.")
                else:
                    # Clear existing DB to keep it fresh (optional)
                    if os.path.exists("db"):
                        shutil.rmtree("db")

                    # 2. Prepare Documents for Vector DB
                    documents = []
                    for article in articles:
                        # Combine title, description and content for context
                        text_content = f"Title: {article['title']}\nDescription: {article['description']}\nContent: {article['content']}"
                        meta = {"url": article['url'], "source": article['source']['name']}
                        doc = Document(page_content=text_content, metadata=meta)
                        documents.append(doc)
                    
                    # 3. Initialize Embeddings
                    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
                    
                    # 4. Create Vector Store (Persisted to disk in 'db' folder)
                    vectordb = Chroma.from_documents(
                        documents=documents, 
                        embedding=embeddings,
                        persist_directory="db"
                    )

                    st.session_state['db_ready'] = True
                    st.success(f"Successfully indexed {len(articles)} articles! You can now chat.")
                    
            except HTTPException as e:
                st.error(f"API Error: {e.detail}")
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

    st.markdown("---")
    if st.button("Clear Conversation"):
        st.session_state.messages = []
        st.rerun()

# Chat Interface
st.subheader("📺 Live News Desk")

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar=message.get("avatar")):
        st.markdown(message["content"])
        if "audio" in message:
            st.audio(message["audio"], format="audio/mp3")

if user_query := st.chat_input("Ask the news anchor a question..."):
    if not os.path.exists("db") and not st.session_state.get('db_ready'):
        st.warning("Please fetch and index news using the sidebar first.")
    else:
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": user_query, "avatar": "👤"})
        with st.chat_message("user", avatar="👤"):
            st.markdown(user_query)

        with st.spinner("Thinking..."):
            # Setup LLM and Embeddings
            embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
            vectordb = Chroma(persist_directory="db", embedding_function=embeddings)
            llm = ChatGoogleGenerativeAI(model=selected_model, temperature=0.3)
            
            # Setup Retrieval Chain
            retriever = vectordb.as_retriever(search_kwargs={"k": 4})
            
            template = """You are a professional news anchor. 
            Answer the question based only on the following context. 
            Adopt an engaging, reporting style tone. Start with a hook like "In today's news..." or "Breaking story...".

            Context:
            {context}

            Question: {question}"""
            prompt = ChatPromptTemplate.from_template(template)
            
            chain = (
                {"context": retriever | (lambda docs: "\n\n".join(d.page_content for d in docs)), "question": RunnablePassthrough()}
                | prompt
                | llm
                | StrOutputParser()
            )
            
            # Get Answer
            response = chain.invoke(user_query)
            
            # Generate Audio (TTS)
            tts = gTTS(text=response, lang='en')
            audio_fp = io.BytesIO()
            tts.write_to_fp(audio_fp)
            audio_data = audio_fp.getvalue()
            
            # Display Assistant Response with Audio
            with st.chat_message("assistant", avatar="🎙️"):
                st.markdown(response)
                st.audio(audio_data, format="audio/mp3")
            
            # Save to history
            st.session_state.messages.append({
                "role": "assistant", 
                "content": response, 
                "avatar": "🎙️",
                "audio": audio_data
            })
