# Import necessary libraries
import os

from composio_crewai import Action, App, ComposioToolSet
from crewai import Agent, Task
from dotenv import load_dotenv
from flask import Flask, request
from langchain_openai import ChatOpenAI


# Load environment variables
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
trello_todo_list_id = os.getenv("TRELLO_TODO_LIST_ID")
trello_done_list_id = os.getenv("TRELLO_DONE_LIST_ID")

# Initialize the language model
llm=ChatOpenAI(model="gpt-4o", api_key=openai_api_key)

# Define tools for the agents
composio_toolset = ComposioToolSet()
tools = composio_toolset.get_tools(apps=[App.TRELLO])

# Define the commit agent
commit_agent = Agent(
    role="Github-Trello TODO Agent",
    goal="""Take 'trello_create_trello_card' action on TRELLO via TRELLO APIs based on the Github patch.""",
    backstory="""You are an AI Agent with access to Github and Trello and want to keep the Github Code TODOs, commit messages, and TRELLO Board in Sync. Action to be performed: trello_create_trello_card""",
    verbose=True,
    tools=tools,
    llm=llm,
)

# Start a web server
app = Flask(__name__)


@app.route("/webhook", methods=["POST"])
def webhook():
    t_id = "your_trello_list_id_for_todos"  # Replace with your Trello list ID for TODOs
    d_id = "your_trello_list_id_for_done"  # Replace with your Trello list ID for done tasks

    task1 = Task(
        description=f"""Given the following Github patch: {request.json}, create a TRELLO card (trello_create_trello_card) for the TODOs from code comments in the patch. TRELLO list (id:{t_id}).
        Please read the patch carefully and create cards for the new TODOs only, avoid removed/old TODOs. Card name should reflect the todo comment present in code""",
        expected_output="A TRELLO card created for the commit",
        agent=commit_agent,
    )
    task1.execute()

    task2 = Task(
        description=f"""Given the following Github patch: {request.json}, create a TRELLO card (trello_create_trello_card) for the Commit Message in the patch. TRELLO list (id:{d_id})
        to add card. Create only if the commit message indicates that a task is completed.""",
        expected_output="A TRELLO card created for the commit",
        agent=commit_agent,
    )
    task2.execute()

    return "Payload received and processed", 200


if __name__ == "__main__":
    app.run(port=2000, debug=True)
