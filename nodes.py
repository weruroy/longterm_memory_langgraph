# ------------------------------
# This is where we keep the nodes 
# -----------------------------

from state import AgentState
from typing import Dict 
from memory.db import get_user, save_user , update_age 
#NODES
def detect_intent(state:AgentState) ->Dict:
    """
     This node is meant to detect the users intent/need with the question they have
     provided
    """
    q= state["question"].lower()
    if "my name" in q or "called" in q or "name" in q :
        intent = "get_name"
    elif "age" in q or "old" in q or "how old" in q:
        intent = "get_age"
    else :
        intent = "general"
    
    return {"intent":intent}

def check_user(state:AgentState) -> Dict :
    """ Check if a user exists in the db - Long term memory and get their details"""
    user = get_user()
    if user :
        return {"user_name":user["name"], "age":user["age"] if user["age"] else None}
    return {"user_name":None}

def ask_user_name(state:AgentState) -> Dict :
    """ This node asks the user for their info like age and name"""
    name = input("Hey , I don't know your name . What's your name ? ")
    if not state.get("age") :
        age = input("Just to know you better, do you mind sharing your age ? (if no just skip this)")

    if name :
        if age:
            save_user(name, age)
            return {"user_name":name, "age":age}
        
        save_user(name)
        return {"user_name":name}
    
    return {"user_name":None }

def ask_age(state:AgentState) -> Dict:
    """ 
    This node gets the user age , but we cannot get the user age without getting their name 
    in the long term memory first 
    """
    user_name = state.get("user_name")
    if not user_name :
        name = input("You never even gave me your name to begin with 🥺, what is your name : ")
        if name : save_user(name)
        else :
            print("We cannont proceed without name : ")
            return {
                "user_name":None, "age":None
            }
    age = print ("I never got your age 🤓, what's your age ? preferably (18 -75): ")
    if age :
        update_age(user_name, age)
        return {"age": age}
    return {"age":None}

def handle_memory_question(state:AgentState) -> Dict:
    """
    Based on what is stored in the long term memory (our DB), the user gets a response based 
    on their personal details  
    """
    
    user = get_user()
    if state["intent"] == "get_name" :
        ans = {
            f"Your name is {state.get("user_name")}" if user else "Oopsy ! I don't know you"
        }
    elif state["intent"] == "get_age" :
        ans = {
            f"You are {state.get("age")} years old ! \n It seems like you are not that old I guess 😉" if user["age"] else "It seems like I don't know your age 🥺"
        }
    
    return {"answer":ans}

def general_response(state:AgentState) -> Dict:
    """
    User gets their answer based on a general question they ask , if the user had provided their details
    e.g name and age , the response is going to be personalized and interesting...
    """
    from langchain_openai import ChatOpenAI
    user = get_user()
    
    llm = ChatOpenAI(
        model = "gpt-5-nano",
        temperature=1.0
    )
    
    system_prompt = f"""
    
    You are a helpful assistant and a wise agent , don't give plain and boring answers
    . Don't give AI slope and generic looking answers. I want to take the users question do
    your search with your tools to update your context .
    
    Here are some of the user details :
    Name : {user["name"] if user else "Unknown"} 
    Age : {user["age"] if user else "Unknown"}
    
    Instructions :
    -Always do search with your tools to update your context ,
    -Be concise where needed and detailed where needed 
    - Personalize response if the name and age exists
    - If age of user exists make sure to give the response to  match their demographic , e.g older more mature , younger more energetic and fancy , the ages range from 18 -70
    """
    messages =[
        {"role":"system", "content":system_prompt},
        #tweaked
        #{"role":"user", "content":system_prompt}
    ]
    #was not there 
    role_map = {"human": "user", "ai": "assistant"}
    for msg in state["messages"]:
        messages.append({
            "role":role_map.get(msg.type, "user"),
            "content":msg.content
            })
    
    messages.append({"role":"user","content":state["question"]})
    res = llm.invoke(messages)
    
    answer = res.content
    return {"answer":answer, "messages":[
        {"role":"user","content":state["question"]},
        {"role":"assistant", "content":answer}
    ]}