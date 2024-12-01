#Importing All Necccessary modules
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph.state import CompiledStateGraph
from langgraph.graph import StateGraph,START,END
import os
from dotenv import load_dotenv
from IPython.display import Image,display
from typing_extensions import TypedDict
from langchain_core.prompts import PromptTemplate

# Loading all environment variables
load_dotenv()

#Getting my Gemini API
gemini_api_key = os.getenv('GEMINI_API_KEY')

llm:ChatGoogleGenerativeAI = ChatGoogleGenerativeAI(model="gemini-1.5-flash",api_key=gemini_api_key)


# Graph Structure Class
class State(TypedDict):
    topic:str
    essay:str
    relevance:str
    grammar:str
    structure:str
    overallRating:str
    
# Relevance Function
def relevance(state:State):
    "This function will check the relevance of essay with topic"
    prompt = PromptTemplate(input_variables='topic',template=f"Check If this essay :{state['essay']} is of this topic: {state['topic']}. Only Answer in one word Yes or No")
    message = prompt.format(topic=state['topic'])
    relevance = llm.invoke(message).content
    return {"relevance":relevance}
    
# Grammr Function
def grammar(state:State):
    "This function will check the essays grammar usage quality"
    prompt=PromptTemplate(input_variables='essay', template='Check this english essays:{essay} Grammar usage quality . And Categorize its grammar quality in these categories : Excellent, good, fair enough,bad,worse. And do not give any description of this just give one word out of the categories defined')
    message=prompt.format(essay=state['essay'])
    grammar=llm.invoke(message).content
    return {"grammar" :grammar}

# Structure Function
def structure(state:State):
    "Check the Structure of the essay"
    prompt=PromptTemplate(input_variables='essay',template='Check the Structure of this essay :{essay} . And Categorizes its structure in these categories :very Good, bad ,average. And do not give any description of this just give one word out of the categories defined')
    message = prompt.format(essay=state['essay'])
    structure=llm.invoke(message).content
    return {"structure":structure}

# OverallRating Function
def overallRating(state:State):
    "This Function will give the essay overall rating in 1-10 scale according to its quality"
    prompt = PromptTemplate(input_variables='essay',template='Analyze this essay :{essay} . And Rate this in 1-10 scale and Only give its rating for example : 7/10. And do not write anything else')
    message = prompt.format(essay=state['essay'])
    overallRating = llm.invoke(message).content
    return {"overallRating":overallRating}

# Function for Route_handling in Graph
def route_handling(state:State):
    if state['relevance'].lower == 'no':
        return END
    else:
        return 'grammatically'
    

# Defining the schema of Graph
workflow:StateGraph = StateGraph(State)

#Adding Nodes
workflow.add_node('relevant',relevance)
workflow.add_node('grammatically',grammar)
workflow.add_node('structured',structure)
workflow.add_node('OverallRating',overallRating)

# Connecting nodes through Edges
workflow.add_edge(START,'relevant')
workflow.add_conditional_edges('relevant',route_handling,{
        END: END,
        'grammatically': 'grammatically'
    })
workflow.add_edge('grammatically','structured')
workflow.add_edge('structured','OverallRating')
workflow.add_edge('OverallRating',END)


graph:CompiledStateGraph = workflow.compile()

# graph_image = graph.get_graph().draw_mermaid_png()
# st.image(graph_image, caption='Workflow Graph', use_column_width=True)


# Streamlit Frontend Portion
st.title("Essay Grading AI Agent")

topic = st.text_input("Topic of Essay")
essay = st.text_area("Enter Essay")
button = st.button('Submit')

# Invoking_graph function
def invoking_graph():
    # When button will be clicked by user
    if(button):
      if topic and essay:
        results = graph.invoke({'essay':essay,'topic':topic})
        # Just for Line Break
        st.write("                                                   ")
        # Checking If relevance state will be Yes then it will display all these states
        if results['relevance'] and results['grammar'] and results['structure'] and results['overallRating']:
           st.write(f" Relevance : {results['relevance']}")
           st.write(f"Grammar : {results['grammar']}")
           st.write(f"Structure : {results['structure']}")
           st.write(f"OverallRating : {results['overallRating']}") 
           # Checking If relevance state will be No it will display the below code 
        elif not results['relevance']:
            st.write(f" Relevance : {results['relevance']}")
            st.warning("This Essay is Irrelevant from the topic")
        
        
      else:
        st.warning("Fill the Above Fields first")
    else:
       pass
        
invoking_graph()