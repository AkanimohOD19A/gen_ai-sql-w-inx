from os import getenv
import streamlit as st
import cohere
from cohere import ClientV2
from dotenv import load_dotenv

load_dotenv()

#---------------
## Dependencies
#---------------
## session states
if 'contextual_counter' not in st.session_state:
    st.session_state.contextual_counter = 0
if 'messages' not in st.session_state:
    st.session_state.messages = []

# contextual status
if st.session_state.contextual_counter < 3:
    st.sidebar.success(f"Counter: {st.session_state.contextual_counter}")
else:
    st.sidebar.warning(f"Counter: {st.session_state.contextual_counter}")

## credentials
co = ClientV2(getenv('COHERE_API_KEY'))

#-------------
## User Query
#-------------
query = st.text_input("Enter your query:")

if st.button("Submit") and query:
    #------------------
    ## System context
    #------------------
    system_message = """
    ## Task and Context
    You are an assistant who assist new SQL programmers identify relationships in a dataset.
    
    ## Style Guide
    Try to return the best fit SQL query as much as possible. Be succinct and straight to the point.
    """

    message = f"Convert this {query} into a legitimate SQL query"
    st.session_state.messages.append({"role": "user", "content": query})


    ## Handling context retrieval length
    st.session_state.contextual_counter += 1
    if st.session_state.contextual_counter >= 5:
        st.session_state.messages = []
        st.session_state.contextual_counter = 0
        st.info("Chat history cleared - starting fresh!")


    complied_messages = [{"role": "user", "content": system_message}] + st.session_state.messages

    try:
        response = co.chat_stream(
            model="command-a-03-2025",
            messages=complied_messages
        )

        #print(response.message.content[0].text)

        # Streaming response
        response_placeholder = st.empty()
        full_response = ""


        for event in response:
            if event.type == "content-delta":
                full_response += event.delta.message.content.text
                response_placeholder.write(full_response)

        # Add assistant response to messages
        st.session_state.messages.append({"role": "assistant", "content": full_response})
    except Exception as e:
        st.error(f"Error: {str(e)}")


#----------------
## Chat history
#----------------
with st.sidebar:
    if st.session_state.messages:
        st.subheader("Chat History:")
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                st.text(f"**You**: {msg['content']}")
                st.divider()
            else:
                st.text(f"**Assistant**: {msg['content']}")

            st.divider()
    st.markdown("")

## Debug
    with st.expander("Debug Info"):
        st.markdown("")
        st.write(f"Current counter: {st.session_state.contextual_counter}")
        st.write(f"Messages: {len(st.session_state.messages)}")