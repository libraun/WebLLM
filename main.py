
from flask import Flask
import torch
import pickle

from MyLLM import model

app = Flask(__name__)

ENCODER_PATH = "./MyLLM/encoder.pt"
DECODER_PATH = "./MyLLM/decoder.pt"

@app.route
def predict(input_sent: str):
    global encoder, decoder, en_vocab
    input_tensor = torch.tensor([en_vocab[token] for token in input_sent.split(' ')],
                                dtype=torch.long).view(-1,1)
    
    input_tensor = torch.cat([
        torch.tensor([en_vocab["<BOS_IDX>"]], dtype=torch.long),
        input_tensor,
        torch.tensor([en_vocab["<EOS_IDX>"]], dtype=torch.long)
    ], dim=-1).view(-1,1)

    pred, hidden = encoder(input_tensor)
    decoder_outputs, hidden = decoder(pred, hidden)

    _, topi = decoder_outputs.topk(1)
    topi = topi.squeeze()

    result = [en_vocab.lookup_token(i.item()) for i in topi]
    result = " ".join(result)

    return result

if __name__ == "__main__":

    with open("MyLLM/all_vocab.pickle", "rb") as f:
        en_vocab = pickle.load(f)
    encoder = model.Encoder(len(en_vocab),256, 1)
    decoder = model.Decoder(len(en_vocab),256, 1)

    encoder.load_state_dict(torch.load(ENCODER_PATH))
    decoder.load_state_dict(torch.load(DECODER_PATH))

    exit(0)