import streamlit as st
import openai

# Read the API Key and Setup an OpenAI Client
with open("keys/.openai_api_key.txt") as f:
    key = f.read().strip()

# Set OpenAI API key
openai.api_key = key

st.title("💬AI Chat Code Reviewer")

# Initialize session states for messages and memory
if "messages" not in st.session_state:
    st.session_state["messages"] = []

if "memory" not in st.session_state:
    st.session_state["memory"] = []

# Display previous messages
for msg in st.session_state["messages"]:
    st.chat_message(msg["role"]).write(msg["content"])

# Input area for code
code_input = st.text_area("Enter your Python code here:", height=300)

# Generate button
if st.button("Generate"):
    if not code_input.strip():
        st.error("Please enter some code to analyze.")
    else:
        # Add user code to session messages
        st.session_state["messages"].append({"role": "user", "content": code_input})
        st.chat_message("user").write(code_input)

        # Prepare the prompt for OpenAI
        prompt = f"""You are a helpful AI Code Reviewer. Analyze the following Python code for potential bugs and suggest improvements. Also, provide the fixed code if needed.
        
        Code:
        {code_input}
        
        Respond with a detailed bug report and the corrected code.
        """

        # Get response from OpenAI
        try:
            response = openai.Completion.create(
                model="gpt-3.5-turbo",  # Or use "gpt-4" if you have access to it
                prompt=prompt,
                max_tokens=1500,  # Adjust token limit as needed
                temperature=0.3,  # Control randomness
            )

            # Correctly parse the response
            choices = response.get("choices", [])
            if choices:
                analysis_result = choices[0].get("text", "")
                bug_report, fixed_code = parse_analysis(analysis_result)

                # Append AI response to session memory and display it
                st.session_state["memory"].append({"role": "assistant", "content": analysis_result})
                st.chat_message("assistant").write(analysis_result)

                # Display code review
                st.subheader("Code Review")
                st.text("Bug Report:")
                st.text(bug_report)

                st.text("Fixed Code:")
                st.code(fixed_code, language='python')
            else:
                st.error("No response received from the OpenAI API.")

        except Exception as e:
            st.error(f"Error in OpenAI API call: {str(e)}")

# Function to parse OpenAI response
def parse_analysis(analysis):
    # Attempt to split based on expected keywords
    if "Fixed Code:" in analysis:
        bug_report, fixed_code = analysis.split("Fixed Code:", 1)
    else:
        bug_report = analysis
        fixed_code = "No fixed code available."

    return bug_report.strip(), fixed_code.strip()
