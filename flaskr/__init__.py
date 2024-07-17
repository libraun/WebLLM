from flask import (
    Flask, render_template, url_for, redirect, request, g, session
)
import pickle
import os
import datetime
import torch
from MyLLM import model


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )
    app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(minutes=1)
    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    with open("all_vocab.pickle", "rb") as f:
        en_vocab = pickle.load(f)
    encoder = model.Encoder(len(en_vocab),128, 0, device=torch.device('cpu'))
    decoder = model.Decoder(len(en_vocab),128, 0, device=torch.device('cpu'))

    encoder.load_state_dict(torch.load("encoder.pt"))
    decoder.load_state_dict(torch.load("decoder.pt"))


    @app.route('/index', methods=["GET"])
    def index():
        
        return render_template("chat/index.html")

    @app.route('/send',methods=["GET","POST"])
    def send():

        if request.method == "POST":

            message = request.form.get("message")

            if session.get("messages") is not None:
                session["messages"].append(("user", message))
            else:
                session["messages"] = [("user", message)]
            session["user_message"] = message
            session.modified = True
        
        return redirect(url_for('retrieve'))

    @app.route('/retrieve')
    def retrieve():
        if not session.get("user_message"):
            return render_template("chat/index.html")
        tokens = ["<BOS_IDX>"] + session["user_message"].lower().split(' ') + ["<EOS_IDX>"]
        tokens = torch.tensor([en_vocab[token] for token in tokens], dtype=torch.long).view(-1,1)

        encoder_outputs, encoder_hidden = encoder(tokens)
        decoder_outputs, _ = decoder(encoder_outputs, encoder_hidden)

        _, topi = decoder_outputs.topk(1)
        topi = topi.squeeze()
        result = []
        for idx in topi:
            token = en_vocab.lookup_token(idx.item())
            if token == "<EOS_IDX>":
                break
            elif token != "<BOS_IDX>":
                result.append(token)
        result = " ".join(result)
        if session.get("messages") is not None:
            session["messages"].append(("JetBot",result))
        else:
            session["messages"] = [("JetBot", result)]
        session.modified = True
        
 
        return render_template("chat/index.html")

    # a simple page that says hello
    app.add_url_rule('/', endpoint='index')
    return app