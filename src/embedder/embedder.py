import torch
from transformers import BertModel, BertTokenizer


def get_similarity(source, target):
    # source -> [batch_size, 768]
    # target -> [1, 768]

    cos = torch.nn.CosineSimilarity(dim=1)
    similarity = cos(source, target.expand(source.size()))
    return similarity


class Embedder:
    def __init__(self, max_length: int = 200):
        self.max_length = max_length
        self.tokenizer = BertTokenizer.from_pretrained('DeepPavlov/rubert-base-cased-sentence')
        self.model = BertModel.from_pretrained('DeepPavlov/rubert-base-cased-sentence',
                                               output_hidden_states=True)
        self.model.eval()

    def get_embedding(self, batch):
        encoded = self.tokenizer.batch_encode_plus(batch, max_length=200, padding='max_length',
                                                   truncation=True, return_tensors="pt")
        with torch.no_grad():
            outputs = self.model(**encoded).last_hidden_state
        values, indices = torch.max(outputs, dim=1)
        return values


if __name__ == '__main__':
    embedder = Embedder()
    embeding = embedder.get_embedding(['Мой текст', 'Херня'])

    print(f'Вектор эмбеддинга имеет размерность:\n{embeding.shape}\n')

    similarity = get_similarity(embeding, embeding[1].unsqueeze(0))

    print(f'Похожесть векторов:\n{similarity}\n')