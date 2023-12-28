import streamlit.components.v1 as components
import streamlit as st
import pandas as pd
import random
import numpy as np
import time
import threading
from streamlit.runtime.scriptrunner import add_script_run_ctx
from streamlit.runtime.scriptrunner.script_run_context import get_script_run_ctx


import os
from supabase import create_client, Client

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

if "first_run" not in st.session_state:
    st.session_state.first_run = True

if st.session_state.first_run:
    st.set_page_config(
        page_title="Math Trainer - Addition",
        page_icon="💪",
    )
    st.session_state.first_run = False

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

def summed_max_list(number_questions):
    return [ next( summed_max_generator(st.session_state.settings_total_sum, OPERATION ) ) for n in range(number_questions) ]


def start_train_number_questions():
    st.session_state.answers = []
    # create new questions
    st.session_state.questions = summed_max_list(st.session_state.settings_number_questions)
    question = st.session_state.questions.pop()
    st.session_state.question = question
    
    start_train()
    
def run_after_x_minutes(minutes, setPage):
    # seconds = minutes * 60
    seconds = 5
    for remaining_seconds in range(seconds, 0, -1):
        print(f"Remaining seconds: {remaining_seconds}")
        time.sleep(1)  # Sleep for 1 second
        
    # change page component shown
    setPage(PAGE_RESULTS)
    st.rerun()
    
def setPage(page):
    st.session_state.page_show = page
    # show_results() #it doesnt work because the tread doesnt have the state

def start_train_timed():
    st.session_state.answers = []
    # create new questions
    st.session_state.questions = summed_max_list(10_000)
    question = st.session_state.questions.pop()
    st.session_state.question = question
    
    # start timer
    t = threading.Thread( target=run_after_x_minutes, args=(st.session_state.settings_time, setPage), daemon=True )
    add_script_run_ctx(t)
    t.start()
    
    start_train()
    
def start_train():
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
        
    print("st.session_state.answers")
    print(st.session_state.answers)

# --------------------- PAGE FUNCTIONS
            
def show_settings():
    st.write(
        """
        ### Train settings
        """
    )
    
    st.number_input('Total sum of operators', key="settings_total_sum", step=1, min_value=4, max_value=100000,)
    st.number_input('Number of questions', key="settings_number_questions", step=1, min_value=1, max_value=100000)
    st.number_input('Total time', key="settings_time", step=1, min_value=1, max_value=100000,)

    st.button('Start with limit of number of questions ', on_click=start_train_number_questions)
    st.button('Start with limit of time', on_click=start_train_timed)
        
        
def show_question():
    st.write(
    f"""
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
    if st.session_state.answers:
        df = pd.DataFrame(st.session_state.answers)
        # df["answered_correctly"] = np.where( df["correct_answer"] == df["user_answer"], "Yes", "No" )
        st.write(df)
        
        value_counts = df["answered_correctly"].value_counts()
        time_mean = df["time"].mean()
        time_min = df["time"].min()
        time_max = df["time"].max()
        time_total = df["time"].sum()
        total_questions = df.shape[0]
        acuracy = value_counts.get(True, 0) / total_questions
        correctly = int(value_counts.get(True, 0))
        wrong = int(value_counts.get(False, 0))
                                    
        data, count = supabase.table('Sessions').update({
            "correctly": correctly,
            "wrong": wrong,
            "time_mean": time_mean,
            "time_min":time_min,
            "time_max": time_max,
            "time_total": time_total,
            "operation": "+",
            "total_questions": total_questions,
            "total_sum": st.session_state.settings_total_sum,
            "acuracy": acuracy
            }).eq('id', st.session_state.session_id).execute()
        
        st.write(
            f"""
            ## Acuracy: {acuracy}
            Correctly: {correctly} of {total_questions}
            \n
            Wrong: {wrong} of {total_questions}
            \n
            Average time: {time_mean:.2f} seconds
            \n
            Minimum time: {time_min:.2f} seconds
            \n
            Maximum time: {time_max:.2f} seconds
            \n
            Total time: {time_total:.2f} seconds
            """
        )
    else:
        st.write("""## Try again""")
    
    st.button('Restart', on_click=restart_train)

# -------------------------------- PAGE

st.write(
    f"""
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
