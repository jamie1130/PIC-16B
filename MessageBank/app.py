from flask import Flask, g, render_template, request
from flask import redirect, url_for

import sqlite3
import pandas as pd

app = Flask(__name__)

@app.route('/')
def main():
    return render_template('main.html')

@app.route("/submit/", methods=['POST', 'GET'])
def submit():
    if request.method == 'GET':
        return render_template('submit.html')
    else:
        insert_message(request)
        return render_template('submit.html', thanks = True)
    
@app.route("/view/")
def view(): 
    rdm_mesg = random_messages(5)
    length = 5
    message_tuples = []
    for i in range(length):
        message_tuples.append(tuple(rdm_mesg.iloc[i,:]))
    return render_template('view.html', message_tuples = message_tuples)

def get_message_db():
    """
    Checks whether there is a database called message_db in the g attribute of the app.
    If not, then connects to that database, ensuring that the connection is an attribute of g.
    Checks whether a table called messages exists in message_db, and creates it if not.
    Returns the connection g.message_db.
    """
    try:
        # gets datbase from `g` object
        return g.message_db
    except:
        g.message_db = sqlite3.connect("messages_db.sqlite")
        cursor = g.message_db.cursor()
        cmd = """
        CREATE TABLE IF NOT EXISTS messages(
        handle TEXT,
        message TEXT
        );
        """
        cursor.execute(cmd)
        cursor.close()
        return g.message_db
    

def insert_message(request):
    """
    Handles inserting a user message into the database of messages.
    
    Extracts the message and the handle from request.
    Inserts the message into the message database.
    
    :param request: The request object containing form data.
    :return: A tuple containing the message and the handle.
    """

    # Extract the message and the handle from request
    handle = request.form['name']
    message = request.form['message']

    # Connect to the message database
    db = get_message_db()

    # Insert message into the messages table
    cursor = db.cursor()
    cursor.execute("INSERT INTO messages (handle, message) VALUES (?, ?)", (handle, message))
    
    # Commit changes to the database
    db.commit()
    
    # Close the database connection
    db.close()
    
    # Return the message and the handle
    return message, handle

def random_messages(n):
    db = get_message_db()
    cmd = f""" SELECT * FROM messages ORDER BY RANDOM() LIMIT {n}; """
    rdm_mesg = pd.read_sql_query(cmd, db)
    db.close()
    return rdm_mesg