import streamlit.components.v1 as components
import streamlit as st
import pandas as pd
import random
import numpy as np

st.set_page_config(
    page_title="Math Trainer",
    page_icon="💪",
)

st.write(
    """
    # Math Trainer
    """
)


# --------------------------------- CONSTANS
# NUMBER_QUESTIONS = 2
OPERATION = "+"
        
# --------------------------------- FUNCTIONS
def QuestionAnswered(n1, n2, operation, correct_answer, user_answer=None):
    return {"n1": n1, "n2": n2, "operation": operation, "correct_answer": correct_answer, "user_answer": user_answer}
    
def summed_max_generator(max, operation):
    while True:
        n1 = random.randint(1,99)
        n2 = random.randint(1,99)
        correct_answer = n1 + n2
        if correct_answer < max:
            yield QuestionAnswered(n1, n2, operation, correct_answer)

def summed_max_list():
    return [ next( summed_max_generator(st.session_state.config_total_sum, OPERATION ) ) for n in range(st.session_state.config_number_questions) ]

def reset_sum():
    st.session_state.answers = []
    st.session_state.questions = summed_max_list()
            
# --------------------------------- STATE
if "config_total_sum" not in st.session_state:
    st.session_state.config_total_sum = 25

if "config_number_questions" not in st.session_state:
    st.session_state.config_number_questions = 2
    
if "answers" not in st.session_state:
    st.session_state.answers = []

if "questions" not in st.session_state:
    st.session_state.questions = summed_max_list()
        

# --------------------------------- MAIN

st.write(
    """
    ### Settings
    """
)

tab1, tab2, tab3, tab4 = st.tabs(["Sum", "Subtraction", "Multiplication", "Division"])

with tab1:
    st.number_input('Total sum of operators', key="config_total_sum", step=1, min_value=0, max_value=100000,)
    st.number_input('Number of questions', key="config_number_questions", step=1, min_value=1, max_value=100000)

    if st.button('Ok'):
        reset_sum()
    

with tab2:
    pass
with tab3:
    pass
with tab4:
    pass