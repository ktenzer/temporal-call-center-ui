from flask import Flask, render_template, jsonify, request, redirect, url_for
from twilio.twiml.voice_response import VoiceResponse
from twilio.rest import Client
from client import get_client
from dataclasses import dataclass
import os

CALL_POOL_WORKFLOW="call-pool"
ROUTING_METHOD = "routing-free-for-all"

app = Flask(__name__)

@dataclass
class CallInput:
    CallSid: str
    From: str
    To: str
    Routing: str
    TemporalTaskQueue: str
    isCallDelay: bool

@dataclass
class AddAgent:
    name: str
    number: str  

@dataclass
class RemoveAgent:
    name: str

# Route for the dashboard
@app.route("/")
def home():
    return render_template("dashboard.html")

# Route for querying calls and agents from call pool workflow
@app.route("/data")
async def data():
    client = await get_client()
    call_pool_workflow = client.get_workflow_handle(f'{CALL_POOL_WORKFLOW}')

    desc = await call_pool_workflow.describe()

    # Check if workflow is running
    if (desc.status == 1):  
        # Get calls via query to pool workflow
        calls = await call_pool_workflow.query("calls")

        # Get available agents via query to pool workflow
        available_agents = await call_pool_workflow.query("available_agents")

        return jsonify({
            'calls': calls,
            'available_agents': available_agents
        })
    else:
        return jsonify({
            'calls': [],
            'available_agents': []
        })

# Route to add a new agent to the call pool workflow
@app.route('/add_agent', methods=['GET', 'POST'])
async def add_agent():
    if request.method == 'POST':
        client = await get_client()
        name = request.form.get('name')
        number = request.form.get('number')     

        await client.start_workflow(
            "callPoolWorkflow",
            id=CALL_POOL_WORKFLOW,
            task_queue=os.getenv("TEMPORAL_TASK_QUEUE"),
            start_signal="addAgent",
            start_signal_args=[{'name': name,'number': number}],
        )

        return redirect(url_for('home'))
    
    return render_template('add_agent.html')

# Route to remove agent from call pool workflow
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

    # Find and remove the agent from available_agents
    available_agents = [agent for agent in available_agents if agent['name'] != name and agent['number'] != number]

    remove_agent = RemoveAgent(
        name=name
    )    

    await call_pool_workflow.signal("removeAgent", remove_agent)

    # Return the updated data
    return jsonify({
        'calls': calls,
        'available_agents': available_agents
    })

# Route for updating state of call in the workflow
@app.route("/voice-status", methods=['POST'])
async def voice_status():
    call_sid=request.form['CallSid']
    call_status=request.form['CallStatus']

    try:
        client = await get_client()
        call_workflow = client.get_workflow_handle(call_sid)
        await call_workflow.signal("updateCallStatus", call_status)
    except:
        print("Soft failure")

    return jsonify({'status': 'ok',})

# Route for providing twilio webhook to start call workflow for managing call
@app.route("/voice", methods=['POST'])
async def voice():
    call_to=request.form['To']
    call_from=request.form['From']
    call_sid=request.form['CallSid']

    response = VoiceResponse()
    response.say('Thank you for calling Temporal Support.')
    response.say('Please wait while I connect you to the next available agent.')
    response.play('https://flaky-account-8453.twil.io/assets/sample.mp3')

    input = CallInput(
        CallSid=call_sid,
        From=call_from,
        To=call_to,
        Routing=ROUTING_METHOD,
        TemporalTaskQueue=os.getenv("TEMPORAL_TASK_QUEUE"),
        isCallDelay=False
    ) 

    client = await get_client()

    await client.start_workflow(
        "taskWorkflow",
        input,
        id=call_sid,
        task_queue=os.getenv("TEMPORAL_TASK_QUEUE"),
    )

    return str(response)

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True) 