import streamlit as st
import openai
from mem0 import MemoryClient
import time

# Initialize OpenAI and Mem0 clients
openai.api_key = st.secrets["OPENAI_API_KEY"]
client = MemoryClient(api_key=st.secrets["mem0_API"])

def chat_with_gpt4(messages):
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=messages,
        max_tokens=150,
        n=1,
        stop=None,
        temperature=0.7,
    )
    return response.choices[0].message.content.strip()

def get_system_prompt(student):
    user_memories = client.get_all(user_id=student)
    memories = "\n".join([i["memory"] for i in user_memories])
    return f"You are a tutor for {student}. Be more elaborate on a topic if one struggles with it more. Keep the following information about the student in mind:-\n\n{memories}"

def main():
    st.title("AI Tutor Chat")

    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "student_name" not in st.session_state:
        st.session_state.student_name = ""

    # Student name input
    if not st.session_state.student_name:
        st.session_state.student_name = st.text_input("Enter your name:")
        if st.session_state.student_name:
            st.success(f"Welcome, {st.session_state.student_name}!")

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if st.session_state.student_name:
        if prompt := st.chat_input("What would you like to ask?"):
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # Add user input to Mem0
            client.add(prompt, user_id=st.session_state.student_name)

            # Get updated system prompt
            system_prompt = get_system_prompt(st.session_state.student_name)

            # Prepare messages for GPT-4
            gpt_messages = [
                {"role": "system", "content": system_prompt},
                *st.session_state.messages
            ]

            # Get AI response
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                full_response = ""
                assistant_response = chat_with_gpt4(gpt_messages)
                
                # Simulate stream of response with milliseconds delay
                for chunk in assistant_response.split():
                    full_response += chunk + " "
                    time.sleep(0.05)
                    # Add a blinking cursor to simulate typing
                    message_placeholder.markdown(full_response + "▌")
                message_placeholder.markdown(full_response)
            
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": full_response})

if __name__ == "__main__":
    main()
