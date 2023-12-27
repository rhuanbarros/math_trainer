import streamlit.components.v1 as components
import streamlit as st
import pandas as pd
import random
import numpy as np

from Main import reset_sum

# --------------------------------- CONSTANS
# NUMBER_QUESTIONS = 2
OPERATION = "+"
        
# --------------------------------- FUNCTIONS
def submit():
    question["user_answer"] = st.session_state.answer
    
    st.session_state.answers.append( st.session_state.question )
    st.session_state.answer = None
    
def train_results():
    df = pd.DataFrame(st.session_state.answers)
    df["answered_correctly"] = np.where( df["correct_answer"] == df["user_answer"], "Ok", "Not ok" )
    st.write(df)
    
    correctly = df["answered_correctly"].value_counts().get("Ok", 0)
    total = len(df)
    
    st.write(
        f"""
        #### Correctly answered {correctly} of {total}
        """
    )

# --------------------------------- MAIN

if len(st.session_state.questions):
    st.write(
        """
        ### Answer quickly
        """
        )
    
    question = st.session_state.questions.pop()
    st.session_state.question = question
        
    st.write( f"{question['n1']} {question['operation']} {question['n2']}")

    st.number_input('Type your answer', value=None, key="answer", on_change=submit, step=1, min_value=0, max_value=10000)
    
else:
    st.write(
        """
        ## Train results
        """
        )
    train_results()
    
    # if st.button('Reset'):  #not working
    #     reset_sum()