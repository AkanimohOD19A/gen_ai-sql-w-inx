# helper/insight_gen.py
import streamlit as st
import cohere
from cohere import ClientV2
import pandas as pd
from typing import Optional, Dict, Any, dataclass_transform
import json

class SQLInsightGenerator:
    def __init__(self, API_KEY: str):
        self.client = ClientV2(API_KEY) if API_KEY else None
        self.initialize_session_state()

    def initialize_session_state(self):
        """Iniitialize all session state variables"""
        if 'contextual_counter' not in st.session_state:
            st.session_state.contextual_counter = 0
        if 'ai_messages' not in st.session_state:
            st.session_state.ai_messages = []
        if 'current_context' not in st.session_state:
            st.session_state.current_context = {}

    def update_context(self,
                       query: str = None,
                       dataframe: pd.DataFrame = None,
                       tables_info: Dict = None,
                       db_type: str = None):
        """Update the current context for AI responses"""
        context = {
            'last_query': query,
            'db_type': db_type,
            'tables_info': tables_info
        }

        if dataframe is not None and not dataframe.empty:
            context['data_summary'] = {
                'shape': dataframe.shape,
                'columns': list(dataframe.columns),
                'dtypes': dataframe.dtypes.to_dict(),
                'sample_data': dataframe.head(3).to_dict('records') if len(dataframe) > 0 else []
            }

        st.session_state.current_context = context

    def generate_response(self,
                          prompt: str,
                          response_type: str = "general") -> str:
        """Generate an AI response based on prompt"""
        if not self.client:
            return "❌ API key not provided. Please enter a valid Cohere API key."

        try:
            system_messages = {
                "query_explanation": """
                You are a SQL expert assistant. Explain SQL queries in a clear, educational manner.
                Focus on:
                - What the query does
                - Key SQL concepts used
                - Potential optimizations
                - Expected results
                """,
                "query_generation": """
                You are a SQL query generator. Create SQL queries based on user requirements.
                Always:
                - Write syntactically correct SQL
                - Use appropriate database-specific syntax
                - Include comments for complex logic
                - Suggest alternative approaches when relevant
                """,
                "data_insights": """
                You are a data analyst. Provide insights about datasets and query results.
                Focus on:
                - Data patterns and trends
                - Potential data quality issues
                - Suggested analyses
                - Business implications
                """,
                "general": """
                You are a helpful SQL and data analysis assistant. Provide clear, 
                actionable responses based on the context provided.
                """
            }

            system_message = system_messages.get(response_type, system_messages["general"])

            # Build Context information
            context_info = ""
            if st.session_state.current_context:
                ctx = st.session_state.current_context
                context_info = f"""
                
                Current context: :
                - Database Type: {ctx.get('db_type', 'Unknown')}
                - Last Query: {ctx.get('last_query', 'None')}
                """

                if 'data_summary' in ctx:
                    ds = ctx['data_summary']
                    context_info += f"""
                    
                    - Dataset Shape: {ds['shape']} (rows, columns)
                    - Columns: {', '.join(ds['columns'])}
                    - Sample Data: {json.dumps(ds['sample_data'][:2], indent=2)}
                    """

            full_propmt = f"{system_message}\n\n{context_info}\n\nUser Query: {prompt}"

            # Manage conversation history
            self._manage_conversation_history()

            # Add current message
            st.session_state.ai_messages.append({"role": "user", "content": prompt})

            # Prep. message for API
            messages = [{"role": "user", "content": full_propmt}] + st.session_state.ai_messages[-4:] #Limited to the last 4 messages

            response = self.client.chat(
                model="command-a-03-2025",
                messages=messages,
                max_tokens=1000,
                temperature=0.3
            )

            assistant_response = response.message.content[0].text
            st.session_state.ai_messages.append({"role": "assistant", "content": assistant_response})

            return assistant_response

        except Exception as e:
            return f"❌ Error generating response: {str(e)}"

    def _manage_conversation_history(self):
        """Manage conversation history to prevent token overflow"""
        st.session_state.contextual_counter += 1

        # Reset every 10 interactions
        if st.session_state.contextual_counter >= 10:
            st.session_state.ai_messages = st.session_state.ai_messages[-2:] #keep last 2
            st.session_state.contextual_counter = 0
            st.info("🔄 Chat history trimmed to maintain performance")

    def generate_sql_query(self,
                           natural_language_query: str,
                           table_info: Dict = None) -> str:
        """Generate a SQL query based on natural language query"""
        context = ""
        if table_info:
            context = f"Available tables and columns: {json.dumps(table_info, indent=2)}"

        prompt = f"""
        {context}
        
        Generate a SQL query for: {natural_language_query}
        
        Please provide:
        1. The SQL query
        2. Brief explanation of what it does
        """

        return self.generate_response(prompt, "query_generation")

    def explain_query(self, sql_query: str) -> str:
        """Explain what a SQL query does"""
        prompt = f"Please explain this SQL query step by step:\n\n{sql_query}"
        return self.generate_response(prompt, "query_explanation")

    def analyze_data(self, dataframe: pd.DataFrame, analysis_request: str = "") -> str:
        """Analyze dataframe and provide insights"""
        if analysis_request:
            prompt = f"Based on the provided dataset, please: {analysis_request}"
        else:
            prompt = "Please analyze this dataset and provide key insights, patterns, and recommendations."

        return self.generate_response(prompt, "data_insights")

    def suggest_visualizations(self, dataframe: pd.DataFrame) -> str:
        """Suggest appropriate visualizations for the data"""
        prompt = "Based on the dataset structure and data types, suggest appropriate charts and visualizations that would be most effective for exploring this data."
        return self.generate_response(prompt, "data_insights")

def display_chat_history():
    """Display chat history in sidebar"""
    if st.session_state.ai_messages:
        st.sidebar.subheader("💬 AI Chat History")

        with st.sidebar:
            # Show last 6 messages
            recent_messages = st.session_state.ai_messages[-6:]

            for i, msg in enumerate(recent_messages):
                with st.expander(f"{'🧑' if msg['role'] == 'user' else '🤖'} "
                                         f"{msg['role'].title()} {i+1}"):
                    st.write(msg['content'][:200] + "..." if len(msg['content']) > 200 else msg['content'])

            # Clear history button with timestamp-based unique key
            import time
            clear_key = f"clear_chat_{int(time.time() * 1000)}"

            if st.button("Clear Chat History",
                         key=clear_key, #f"clear_chat_{id(st.session_state.ai_messages)}",  # Make key unique
                         icon="🗑"):
                st.session_state.ai_messages = []
                st.session_state.contextual_counter = 0
                st.rerun()

def create_sample_data_for_testing():
    """Create sample data for testing"""
    return pd.DataFrame({
        'id': range(1, 101),
        'name': [f'Employee_{i}' for i in range(1, 101)],
        'department': ['Engineering', 'Marketing', 'Sales', 'HR'] * 25,
        'salary': [50000 + (i * 1000) for i in range(100)],
        'years_experience': [i % 10 + 1 for i in range(100)]
    })