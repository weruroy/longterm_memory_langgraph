from typing import TypedDict, Optional, Annotated
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    question:  str
    user_name: Optional[str]
    age:       Optional[str]
    intent:    Optional[str]
    answer:    Optional[str]
    messages:  Annotated[list, add_messages]