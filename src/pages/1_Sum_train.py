import streamlit.components.v1 as components
import streamlit as st
import pandas as pd
import random
import numpy as np
import time

import os
from supabase import create_client, Client

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

st.set_page_config(
    page_title="Math Trainer - Addition",
    page_icon="💪",
)

# --------------------------------- CONSTANS
# NUMBER_QUESTIONS = 2
OPERATION = "+"

# it doesnt work with enum
# class PageComponent(Enum):
#     SETTINGS = 1
#     TRAIN = 2
#     RESULTS = 3

PAGE_SETTINGS = 0
PAGE_TRAIN = 1
PAGE_RESULTS = 2

# --------------------------------- STATE
if "settings_total_sum" not in st.session_state:
    st.session_state.settings_total_sum = 25

if "settings_number_questions" not in st.session_state:
    st.session_state.settings_number_questions = 2

if "page_show" not in st.session_state:
    st.session_state.page_show = PAGE_SETTINGS
    
if "answers" not in st.session_state:
    st.session_state.answers = []

if "start_time" not in st.session_state:
    st.session_state.start_time = None
        
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
    return [ next( summed_max_generator(st.session_state.settings_total_sum, OPERATION ) ) for n in range(st.session_state.settings_number_questions) ]

def start_train():
    new_train()
    
    data, count = supabase.table('Sessions').insert({
        "operation": "+", 
        "total_questions": st.session_state.settings_number_questions, 
        "total_sum": st.session_state.settings_total_sum 
        }).execute()
    
    st.session_state.session_id = data[1][0]["id"]    
    
    # change page component shown
    st.session_state.page_show = PAGE_TRAIN

def restart_train():
    # change page component shown
    st.session_state.page_show = PAGE_SETTINGS

def new_train():
    st.session_state.answers = []
    # create new questions
    st.session_state.questions = summed_max_list()
    question = st.session_state.questions.pop()
    st.session_state.question = question
    

def submit():
    # save question
    end_time = time.time()
    st.session_state.question["time"] = end_time - st.session_state.start_time
    st.session_state.question["user_answer"] = st.session_state.answer
    st.session_state.question["session_id"] = st.session_state.session_id
    st.session_state.question["answered_correctly"] = True if st.session_state.question["correct_answer"] == st.session_state.question["user_answer"] else False
    st.session_state.answers.append( st.session_state.question )
    st.session_state.answer = None
    
    data, count = supabase.table('Questions').insert(st.session_state.question).execute()
    
    # take another question
    if st.session_state.questions:
        question = st.session_state.questions.pop()
        st.session_state.question = question
    else:
        # change page component shown
        st.session_state.page_show = PAGE_RESULTS

# --------------------- PAGE FUNCTIONS
            
def show_settings():
    st.write(
        """
        ### Train settings
        """
    )

    st.number_input('Total sum of operators', key="settings_total_sum", step=1, min_value=4, max_value=100000,)
    st.number_input('Number of questions', key="settings_number_questions", step=1, min_value=1, max_value=100000)

    st.button('Start', on_click=start_train)
        
        
def show_question():
    st.write(
    """
    ### Answer quickly
    """
    )
    
    question = st.session_state.question       
    st.write( f"{question['n1']} {question['operation']} {question['n2']}")
    st.session_state.start_time = time.time()
    st.number_input('Type your answer', value=None, key="answer", on_change=submit, step=1, min_value=0, max_value=10000)

def show_results():
    st.write(
        """
        ## Train results
        """
        )
    
    df = pd.DataFrame(st.session_state.answers)
    # df["answered_correctly"] = np.where( df["correct_answer"] == df["user_answer"], "Yes", "No" )
    st.write(df)
    
    value_counts = df["answered_correctly"].value_counts()
    avg_time = df["time"].mean()
    min_time = df["time"].min()
    max_time = df["time"].max()
    total_time = df["time"].sum()
    number_questions = df.shape[0]
    acuracy = value_counts.get("Yes", 0) / number_questions
    
    
    st.write(
        f"""
        ## Acuracy: {acuracy}
        Correctly: {value_counts.get("Yes", 0)} / {number_questions}
          \n
        Wrong: {value_counts.get("No", 0)} / {number_questions}
          \n
        Average time: {avg_time:.2f} seconds
          \n
        Minimum time: {min_time:.2f} seconds
          \n
        Maximum time: {max_time:.2f} seconds
          \n
        Total time: {total_time:.2f} seconds
        """
    )
    
    st.button('Restart', on_click=restart_train)

# -------------------------------- PAGE

st.write(
    """
    # Addition
    """
)

        
# if st.session_state.page_show == PAGE_SETTINGS:
#     show_settings()
# elif st.session_state.page_show == PAGE_TRAIN:
#     show_question()
# elif st.session_state.page_show == PAGE_RESULTS:
#     show_results()

# match case doesnt work with "CONSTANTS" because it isnt a real constant....
        
match st.session_state.page_show:
    case 0:
        show_settings()
    case 1:
        show_question()
    case 2:
        show_results()
