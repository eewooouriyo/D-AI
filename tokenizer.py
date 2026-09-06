import re
from collections import Counter


class Tokenizer:
    def __init__(self):
        self.stoi = {
            "<PAD>": 0,
            "<UNK>": 1,
            "<BOS>": 2,
            "<EOS>": 3
        }

        self.itos = {
            0: "<PAD>",
            1: "<UNK>",
            2: "<BOS>",
            3: "<EOS>"
        }

    def split(self, text):
        return re.findall(
            r"\w+|[^\w\s]",
            text.lower(),
            re.UNICODE
        )

    def train(self, text):
        tokens = self.split(text)
        counter = Counter(tokens)

        for token, _ in counter.most_common():

            if token not in self.stoi:

                index = len(self.stoi)

                self.stoi[token] = index
                self.itos[index] = token

    def encode(self, text):
        tokens = self.split(text)

        return [
            self.stoi.get(
                token,
                self.stoi["<UNK>"]
            )
            for token in tokens
        ]

    def decode(self, ids):
        result = ""

        for token_id in ids:

            token = self.itos.get(
                token_id,
                "<UNK>"
            )

            # Never display internal tokens
            if token in {
                "<PAD>",
                "<BOS>",
                "<EOS>"
            }:
                continue

            if not result:
                result = token

            elif re.match(
                r"[.,!?;:%)\]}]",
                token
            ):
                result += token

            else:
                result += " " + token

        return result