import json
from tokenizer import Tokenizer


MODEL_FILE = "model.json"


def train():

    print("================================")
    print("        ENTRENANDO D-IA")
    print("================================")

    with open(
        "data.txt",
        "r",
        encoding="utf-8"
    ) as file:

        text = file.read()

    tokenizer = Tokenizer()

    # Crear vocabulario
    tokenizer.train(text)

    print()
    print(
        "Vocabulario:",
        len(tokenizer.stoi)
    )

    vocab_size = len(tokenizer.stoi)

    # -------------------------------------------------
    # MODELO DE TRIGRAMAS
    #
    # context = (palabra1, palabra2)
    #
    # counts[context][siguiente_palabra]
    # -------------------------------------------------

    counts = {}

    lines = text.splitlines()

    for line in lines:

        line = line.strip()

        if not line:
            continue

        # IMPORTANTE:
        # Agregamos BOS/EOS directamente.
        # No los metemos al tokenizer como texto.

        tokens = tokenizer.encode(line)

        tokens = [
            tokenizer.stoi["<BOS>"]
        ] + tokens + [
            tokenizer.stoi["<EOS>"]
        ]

        # Si hay muy pocos tokens, ignoramos
        if len(tokens) < 3:
            continue

        for i in range(len(tokens) - 2):

            a = tokens[i]
            b = tokens[i + 1]
            c = tokens[i + 2]

            context = f"{a},{b}"

            if context not in counts:

                counts[context] = [
                    0
                    for _ in range(vocab_size)
                ]

            counts[context][c] += 1

    model = {
        "stoi": tokenizer.stoi,

        "itos": {
            str(k): v
            for k, v in tokenizer.itos.items()
        },

        "counts": counts
    }

    with open(
        MODEL_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            model,
            file,
            ensure_ascii=False
        )

    print()
    print("ENTRENAMIENTO TERMINADO.")
    print(
        "Contextos aprendidos:",
        len(counts)
    )
    print(
        "Modelo guardado como:",
        MODEL_FILE
    )


if __name__ == "__main__":
    train()