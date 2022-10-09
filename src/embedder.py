import torch
from transformers import BertModel, BertTokenizer
from argparse import ArgumentParser
from flask import Flask, request


def get_similarity(source, target):
    # source -> [batch_size, 768]
    # target -> [1, 768]
    source = torch.tensor(source, dtype=torch.float32)
    target = torch.tensor(target, dtype=torch.float32)

    cos = torch.nn.CosineSimilarity(dim=1)
    similarity = cos(source, target.expand(source.size()))
    return similarity


class Embedder:
    def __init__(self, max_length: int = 200):
        self.max_length = max_length
        self.tokenizer = BertTokenizer.from_pretrained('DeepPavlov/rubert-base-cased-sentence', cache_dir="./models/", device=0)
        self.model = BertModel.from_pretrained('DeepPavlov/rubert-base-cased-sentence',
                                               output_hidden_states=True).cuda()
        self.model.eval()

    def get_embedding(self, batch):
        encoded = self.tokenizer.batch_encode_plus(batch, max_length=200, padding='max_length',
                                                   truncation=True, return_tensors="pt")
        with torch.no_grad():
            outputs = self.model(**{name: tensor.cuda() for name, tensor in encoded.items()}).last_hidden_state
        values, indices = torch.max(outputs, dim=1)
        return values


if __name__ == '__main__':
    parser = ArgumentParser(description='Process text')
    parser.add_argument('--max_length', type=int, default=200)


    args = parser.parse_args()
    embed = Embedder(max_length=args.max_length)


    # Действие
    #outputs = embed.get_embedding([text])


    app = Flask(__name__)

    @app.route('/get_embeddings', methods=['POST'])
    def get_embeddings():
        """
        {
            'news': [...]
        }
        :return:
        """
        texts = request.json['news']
        outputs = embed.get_embedding(texts)
        outputs = outputs.tolist()
        return str(outputs)


    @app.route('/get_similarity', methods = ['POST'])
    def get_similarity_method():
        """
        {
            'source': [[...], [...], ...]
            'target': [...]
        }
        :return:
        """
        source = request.json['source']
        target = request.json['target']
        outputs = get_similarity(source, target)
        outputs = outputs.tolist()
        return str(outputs)




    print('run')
    app.run(host = '0.0.0.0', port = 1707, debug=True)

