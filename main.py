#main.py

# GLOBAL imports
from typing import TypedDict , Dict, Optional, Annotated
from langgraph.graph import StateGraph , END , START
# import the checkpointer  
from langgraph.checkpoint.sqlite import SqliteSaver
from dotenv import load_dotenv

#rich formatting for the terminal 
from langgraph.graph.message import add_messages
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich import print as rprint


#LOCAL imports : imports withing our root folder/project
from memory.db import init_db, save_user, get_user, update_age
from nodes import detect_intent, ask_age ,ask_user_name, general_response , handle_memory_question,check_user
from state import AgentState

load_dotenv() # Loads the OPENAI_API_KEY , make sure your key is set in the secret environment variable and it is going to be detected like magic and automatically added with your llm calls

init_db()   

# Constructing the graph
builder = StateGraph(AgentState)

# Adding nodes to graph state

builder.add_node("detect_intent", detect_intent)
builder.add_node("check_user" , check_user)
builder.add_node("ask_user",ask_user_name)
builder.add_node("ask_age", ask_age)
builder.add_node("memory", handle_memory_question)
builder.add_node("general", general_response)

# Connecting the nodes by adding eddges 

builder.add_edge(START, "detect_intent")
builder.add_edge("detect_intent", "check_user")

 #conditional edges and routing at this point
 
def route(state:AgentState):
    if state["intent"] == "get_name" :
        return "memory"

    if state["intent"] == "get_age" :
        if not state.get("age"):
            return "ask_age"
        return "memory"
    
    if not state.get("user_name"):
        return "ask_user"
    
    return "general"

builder.add_conditional_edges("check_user",route)
builder.add_edge("ask_age", "check_user")
builder.add_edge("ask_user", "check_user")
builder.add_edge("memory", END)
builder.add_edge("general", END)

# Importing this for terminal formating , no worries nothing to worry think of this like a terminal decoratoin
# In short this has nothing to do with the agent , its just formatting and presentation of the answer
console= Console()

import uuid 
thread_id = str(uuid.uuid4())
config = {"configurable":{"thread_id":thread_id}}

# Compiling everything together
with SqliteSaver.from_conn_string("memory/memory.db") as checkpointer:
    app = builder.compile(checkpointer=checkpointer)
    
    while True:
        q = input("\nAsk me a question ,I'm Mr Bot🤖 : ")

        if q in ("quit", "exit"):
            console.print("\n[bold yellow]Just exited the workflow...Nice time though ✨[/bold yellow]")
            break

        console.print("\n" + "-" * 60)
        console.print("[bold cyan] Bot is thinking...[/bold cyan]")
        console.print("-" * 60)

        res = app.invoke({"question": q}, config=config)

        # Render the answer as markdown inside a styled panel
        console.print(
            Panel(
                Markdown(res["answer"]),
                title="[bold green]🤖 Mr.Bot responded... [/bold green]",
                border_style="bright_blue",
                padding=(1, 2)
            )
        )

        