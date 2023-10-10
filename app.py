from flask import Flask, render_template, jsonify, request, redirect, url_for
from client import get_client
from dataclasses import dataclass

app = Flask(__name__)
CALL_POOL_WORKFLOW="callpool-test"

@dataclass
class RemoveAgent:
    agent: str  

@app.route("/")
def home():
    return render_template("dashboard.html")

@app.route("/data")
async def data():
    client = await get_client()
    call_pool_workflow = client.get_workflow_handle(f'{CALL_POOL_WORKFLOW}')

    # Get calls via query to pool workflow
    calls = await call_pool_workflow.query("calls")

    # Get available agents via query to pool workflow
    available_agents = await call_pool_workflow.query("available_agents")

    return jsonify({
        'calls': calls,
        'available_agents': available_agents
    })

@app.route('/add_agent', methods=['GET', 'POST'])
def add_agent():
    if request.method == 'POST':
        name = request.form.get('name')
        number = request.form.get('number')
        # Add code to send remove signal
        
        # After adding the agent, redirect to the dashboard.
        return redirect(url_for('home'))
    return render_template('add_agent.html')

@app.route("/remove_agent")
async def remove_agent():
    # Extract agent info from query parameters
    name = request.args.get("name")
    number = request.args.get("number")

    client = await get_client()
    call_pool_workflow = client.get_workflow_handle(f'{CALL_POOL_WORKFLOW}')

    # Get calls via query to pool workflow
    calls = await call_pool_workflow.query("calls")

    # Get available agents via query to pool workflow
    available_agents = await call_pool_workflow.query("available_agents")

    # Find and remove the agent from available_agents (if exists)
    available_agents = [agent for agent in available_agents if agent['name'] != name and agent['number'] != number]

    remove_agent = RemoveAgent(
        agent=name
    )    

    #await call_pool_workflow.signal("removeAgent", remove_agent)

    # Return the updated data
    return jsonify({
        'calls': calls,
        'available_agents': available_agents
    })


if __name__ == "__main__":
    app.run(debug=True)