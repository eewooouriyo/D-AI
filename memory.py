import json
import os


MEMORY_FILE = "memory.json"


class Memory:
    def __init__(self):
        self.data = {
            "facts": {},
            "conversations": []
        }

        self.load()

    def load(self):
        if not os.path.exists(MEMORY_FILE):
            return

        try:
            with open(
                MEMORY_FILE,
                "r",
                encoding="utf-8"
            ) as file:
                saved = json.load(file)

            if isinstance(saved, dict):
                self.data.update(saved)

        except (json.JSONDecodeError, OSError):
            print("D-AI: Could not load memory.")

    def save(self):
        try:
            with open(
                MEMORY_FILE,
                "w",
                encoding="utf-8"
            ) as file:
                json.dump(
                    self.data,
                    file,
                    ensure_ascii=False,
                    indent=4
                )

        except OSError:
            print("D-AI: Could not save memory.")

    def remember_fact(self, key, value):
        key = key.lower().strip()

        self.data["facts"][key] = value
        self.save()

    def recall_fact(self, key):
        key = key.lower().strip()

        return self.data["facts"].get(key)

    def remember_conversation(self, user, assistant):
        self.data["conversations"].append({
            "user": user,
            "assistant": assistant
        })

        if len(self.data["conversations"]) > 1000:
            self.data["conversations"] = (
                self.data["conversations"][-1000:]
            )

        self.save()