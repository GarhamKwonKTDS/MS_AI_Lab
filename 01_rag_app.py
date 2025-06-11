import os
from dotenv import load_dotenv
from openai import AzureOpenAI
import streamlit as st

os.system('cls' if os.name == 'nt' else 'clear')
load_dotenv()
print("Loading environment variables...")

openai_endpoint = os.getenv("OPENAI_ENDPOINT")
openai_api_key = os.getenv("OPENAI_API_KEY")
openai_api_version = os.getenv("OPENAI_API_VERSION")
chat_model = os.getenv("CHAT_MODEL")
chat_model_name = os.getenv("CHAT_MODEL_NAME")
embedding_model = os.getenv("EMBEDDING_MODEL")
embedding_model_name = os.getenv("EMBEDDING_MODEL_NAME")
search_api_key = os.getenv("SEARCH_API_KEY")
search_endpoint = os.getenv("SEARCH_ENDPOINT")
search_index_name = os.getenv("SEARCH_INDEX_NAME")

chat_client = AzureOpenAI(
    api_version=openai_api_version,
    azure_endpoint=openai_endpoint,
    api_key=openai_api_key
)

st.title("Margie's Travel Assistant")
st.write("Ask your travel-related questions below:")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system",
            "content": "You are a travel assistant that provides information and tips available from Margie's Travel."
        }
    ]

for message in st.session_state.messages:
    st.chat_message(message["role"]).write(message["content"])

def get_openai_response(messages):
    rag_params = {
        "data_sources": [
            {
                "type": "azure_search",
                "parameters": {
                    "endpoint": search_endpoint,
                    "index_name": search_index_name,
                    "authentication": {
                        "type": "api_key",
                        "key": search_api_key
                    },
                    "query_type": "vector",
                    "embedding_dependency": {
                        "type": "deployment_name",
                        "deployment_name": embedding_model_name
                    }
                },
                
            }
        ]
    }

    response = chat_client.chat.completions.create(
        model=chat_model,
        messages=st.session_state.messages,
        extra_body=rag_params
    )

    completion = response.choices[0].message.content
    return completion


if user_input := st.chat_input("Enter your question"):
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.chat_message("user").write(user_input)

    with st.spinner("Thinking..."):
        response = get_openai_response(st.session_state.messages)
    
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.chat_message("assistant").write(response)