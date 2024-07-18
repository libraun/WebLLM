import pickle
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session
)
from werkzeug.exceptions import abort
from flaskr.db import get_db, close_db
from MyLLM import model
bp = Blueprint('chat', __name__)

with open("MyLLM/all_vocab.pickle", "rb") as f:
    en_vocab = pickle.load(f)
encoder = model.Encoder(len(en_vocab),256, 1)
decoder = model.Decoder(len(en_vocab),256, 1)

encoder.load_state_dict(torch.load("../encoder"))
decoder.load_state_dict(torch.load(DECODER_PATH))


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

@bp.route('/retrieve')
def retrieve():
