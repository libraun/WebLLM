from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session
)
from werkzeug.exceptions import abort
from flaskr.db import get_db, close_db

bp = Blueprint('chat', __name__)


@bp.route('/index', methods=["GET"])
def index():
    
    return render_template("chat/index.html")

@bp.route('/send',methods=["GET","POST"])
def send():

    if request.method == "POST":

        message = request.form.get("message")

        if session.get("messages") is not None:
            session["messages"].append(message)
        else:
            session["messages"] = [message]
        session.modified = True
    
    return render_template("chat/index.html")