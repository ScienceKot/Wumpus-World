# Importing all needed modules.
from flask import Flask, request, jsonify, render_template, Blueprint, redirect, url_for,flash, session
from utils import matrix2json
from cave import Cave
from agent import Agent


app = Flask(__name__, template_folder = 'templates')
app.static_folder = 'static'

# Setting up the agent and environment.
history = {}
cave = Cave()
agent = Agent()
action = None

sent, agent_position, gold, dead = None, None, None, None

@app.route("/game/<int:id>", methods = ["POST", "GET"])
def game(id):
    global sent, agent_position, gold, dead, agent, cave, history
    if request.method == "GET":
        # Checking if the index is present in history.
        if id in history:
            # Returning the state of the environment at id.
            matrix = history[id]
            action = matrix["action"]
        elif id == 0:
            # If the id is 0 then the environment is generated from nothing.
            sent, agent_position, gold, dead = cave.get_initial_date()
            matrix = matrix2json(cave.cave, agent_position)
            action = ""
        else:
            # Getting the action of the agent.
            action = agent.get_action(sent, agent_position, gold, dead)
            if action == "win":
                print("WIN")
            elif action == "dead":
                print("GAME OVER")
            else:
                sent, agent_position, gold, dead = cave.action(action)
            matrix = matrix2json(cave.cave, agent_position)
        # Creating the json for the front end.
        history[id] = matrix
        matrix["next"] = id+1
        matrix["prev"] = id-1
        matrix["action"] = action
        return render_template("index.html", matrix=matrix)

@app.route("/restart", methods=['GET'])
def restart():
    # This function regenerates the environment.
    global agent, cave, history
    agent = Agent()
    cave = Cave()
    history = {}
    return redirect(url_for("game", id=0))

@app.route("/", methods=["GET"])
def main():
    return render_template("main.html")


app.run()
