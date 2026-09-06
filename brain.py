# ============================================================
# D-AI
# brain.py
# BLOCK 1/4 - BRAIN CORE
# ============================================================

import json
import os
import re
import random
import time
import unicodedata
from collections import Counter, defaultdict


# ============================================================
# MAIN CONFIGURATION
# ============================================================

BRAIN_FILE = "brain.json"

BRAIN_VERSION = 1

MAX_VOCABULARY = 50000
MAX_CONVERSATIONS = 5000
MAX_ASSOCIATIONS = 100000

DEFAULT_LANGUAGE = "en"

SPECIAL_TOKENS = {
    "PAD": "<PAD>",
    "UNK": "<UNK>",
    "BOS": "<BOS>",
    "EOS": "<EOS>",
}


# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def current_timestamp():
    return time.time()


def normalize_unicode(text):
    """
    Normalizes Unicode characters without destroying letters.
    """

    if not isinstance(text, str):
        return ""

    return unicodedata.normalize(
        "NFKC",
        text
    )


def normalize_spaces(text):
    """
    Converts multiple spaces into a single space.
    """

    return re.sub(
        r"\s+",
        " ",
        text
    ).strip()


def safe_lower(text):
    """
    Safely converts text to lowercase.
    """

    if not isinstance(text, str):
        return ""

    return text.lower()


def clean_basic_text(text):
    """
    Basic text cleaning used by the brain.

    Punctuation is not completely removed because
    some systems may need it later.
    """

    if not isinstance(text, str):
        return ""

    text = normalize_unicode(text)

    text = normalize_spaces(text)

    text = safe_lower(text)

    return text


def clean_for_matching(text):
    """
    Text version intended for comparing intents.

    Example:

        "¡¡HELLO!!!"
        "hello"

    become equivalent.
    """

    text = clean_basic_text(text)

    text = re.sub(
        r"[¿?¡!.,;:]+",
        "",
        text
    )

    text = normalize_spaces(text)

    return text


def remove_accents(text):
    """
    Removes diacritics only for comparison.

    This allows:

        how
        how

    to be compared when necessary.
    """

    if not isinstance(text, str):
        return ""

    normalized = unicodedata.normalize(
        "NFD",
        text
    )

    return "".join(
        char
        for char in normalized
        if unicodedata.category(char) != "Mn"
    )


def normalize_for_search(text):
    """
    Aggressive normalization for internal searches.
    """

    text = clean_for_matching(text)

    text = remove_accents(text)

    return text


# ============================================================
# CORE TOKENIZER
# ============================================================

class Tokenizer:
    """
    Basic D-AI tokenizer.

    Its purpose is not to be a Transformer tokenizer yet.

    This version is designed for:
        - words
        - numbers
        - symbols
        - emoticons
        - simple contractions
        - unknown text
    """

    TOKEN_PATTERN = re.compile(
        r"""
        [a-záéíóúüñ]+(?:['’][a-záéíóúüñ]+)?
        |
        \d+(?:[.,]\d+)?
        |
        [!?¿¡]+
        |
        [:;=8xX][-^']?[)(DPpOo/\\]
        |
        [^\s]
        """,
        re.IGNORECASE | re.VERBOSE
    )

    def __init__(self):
        self.special_tokens = dict(
            SPECIAL_TOKENS
        )

    def normalize(self, text):
        return clean_basic_text(text)

    def tokenize(self, text):
        """
        Converts text into a list of tokens.
        """

        text = self.normalize(text)

        if not text:
            return []

        tokens = self.TOKEN_PATTERN.findall(text)

        return [
            token.strip()
            for token in tokens
            if token.strip()
        ]

    def tokenize_for_matching(self, text):
        """
        Tokenization intended for comparing phrases.
        """

        text = normalize_for_search(text)

        if not text:
            return []

        return self.TOKEN_PATTERN.findall(text)

    def detokenize(self, tokens):
        """
        Approximately reconstructs a sentence.
        """

        if not tokens:
            return ""

        result = ""

        no_space_before = {
            ".",
            ",",
            "!",
            "?",
            ";",
            ":",
            ")",
            "]",
            "}",
        }

        no_space_after = {
            "(",
            "[",
            "{",
        }

        for token in tokens:

            if not result:
                result = token
                continue

            if token in no_space_before:
                result += token

            elif result[-1:] in no_space_after:
                result += token

            else:
                result += " " + token

        return result

    def normalize_tokens(self, tokens):
        """
        Normalizes a collection of tokens.
        """

        result = []

        for token in tokens:

            if not isinstance(token, str):
                continue

            token = clean_basic_text(token)

            if token:
                result.append(token)

        return result


# ============================================================
# WORD STRUCTURE
# ============================================================

class WordInfo:
    """
    Represents statistical information about a word.
    """

    def __init__(
        self,
        word,
        first_seen=None
    ):
        self.word = word

        self.count = 0

        self.first_seen = (
            current_timestamp()
            if first_seen is None
            else first_seen
        )

        self.last_seen = self.first_seen

        self.context_count = 0

        self.response_count = 0

        self.question_count = 0

        self.command_count = 0

    def seen(
        self,
        amount=1,
        response=False,
        question=False,
        command=False
    ):
        self.count += amount

        self.last_seen = current_timestamp()

        self.context_count += amount

        if response:
            self.response_count += amount

        if question:
            self.question_count += amount

        if command:
            self.command_count += amount

    def to_dict(self):
        return {
            "word": self.word,
            "count": self.count,
            "first_seen": self.first_seen,
            "last_seen": self.last_seen,
            "context_count": self.context_count,
            "response_count": self.response_count,
            "question_count": self.question_count,
            "command_count": self.command_count,
        }

    @classmethod
    def from_dict(cls, data):
        info = cls(
            data.get(
                "word",
                ""
            ),
            data.get(
                "first_seen"
            )
        )

        info.count = int(
            data.get(
                "count",
                0
            )
        )

        info.last_seen = data.get(
            "last_seen",
            info.first_seen
        )

        info.context_count = int(
            data.get(
                "context_count",
                0
            )
        )

        info.response_count = int(
            data.get(
                "response_count",
                0
            )
        )

        info.question_count = int(
            data.get(
                "question_count",
                0
            )
        )

        info.command_count = int(
            data.get(
                "command_count",
                0
            )
        )

        return info


# ============================================================
# BRAIN STATE
# ============================================================

class BrainState:
    """
    Contains all persistent brain state.
    """

    def __init__(self):

        self.version = BRAIN_VERSION

        self.created_at = current_timestamp()

        self.updated_at = self.created_at

        # ---------------------------------------------
        # Vocabulary
        # ---------------------------------------------

        self.vocabulary = {}

        # ---------------------------------------------
        # Token frequency
        # ---------------------------------------------

        self.token_frequency = Counter()

        # ---------------------------------------------
        # Word -> word relationships
        # ---------------------------------------------

        self.associations = defaultdict(
            Counter
        )

        # ---------------------------------------------
        # Learned responses
        # ---------------------------------------------

        self.responses = defaultdict(
            Counter
        )

        # ---------------------------------------------
        # Statistics
        # ---------------------------------------------

        self.total_messages = 0

        self.total_user_messages = 0

        self.total_ai_messages = 0

        self.total_tokens = 0

        self.total_words = 0

        self.total_learning_events = 0

        # ---------------------------------------------
        # Context
        # ---------------------------------------------

        self.last_user_message = ""

        self.last_ai_message = ""

        self.conversation_turn = 0

        # ---------------------------------------------
        # State
        # ---------------------------------------------

        self.learning_enabled = True

        self.initialized = True

    def touch(self):
        self.updated_at = current_timestamp()

    def to_dict(self):

        associations = {}

        for word, counter in self.associations.items():
            associations[word] = dict(counter)

        responses = {}

        for message, counter in self.responses.items():
            responses[message] = dict(counter)

        vocabulary = {}

        for word, info in self.vocabulary.items():
            if isinstance(info, WordInfo):
                vocabulary[word] = info.to_dict()

        return {
            "version": self.version,
            "created_at": self.created_at,
            "updated_at": self.updated_at,

            "vocabulary": vocabulary,

            "token_frequency": dict(
                self.token_frequency
            ),

            "associations": associations,

            "responses": responses,

            "statistics": {
                "total_messages": self.total_messages,
                "total_user_messages": self.total_user_messages,
                "total_ai_messages": self.total_ai_messages,
                "total_tokens": self.total_tokens,
                "total_words": self.total_words,
                "total_learning_events": self.total_learning_events,
            },

            "context": {
                "last_user_message": self.last_user_message,
                "last_ai_message": self.last_ai_message,
                "conversation_turn": self.conversation_turn,
            },

            "settings": {
                "learning_enabled": self.learning_enabled,
            },
        }

    @classmethod
    def from_dict(cls, data):

        state = cls()

        state.version = data.get(
            "version",
            BRAIN_VERSION
        )

        state.created_at = data.get(
            "created_at",
            current_timestamp()
        )

        state.updated_at = data.get(
            "updated_at",
            current_timestamp()
        )

        # ---------------------------------------------
        # Vocabulary
        # ---------------------------------------------

        vocabulary = data.get(
            "vocabulary",
            {}
        )

        if isinstance(vocabulary, dict):

            for word, info in vocabulary.items():

                if isinstance(info, dict):
                    state.vocabulary[word] = (
                        WordInfo.from_dict(info)
                    )

        # ---------------------------------------------
        # Frequencies
        # ---------------------------------------------

        frequencies = data.get(
            "token_frequency",
            {}
        )

        if isinstance(frequencies, dict):

            state.token_frequency = Counter(
                {
                    str(key): int(value)
                    for key, value in frequencies.items()
                }
            )

        # ---------------------------------------------
        # Associations
        # ---------------------------------------------

        associations = data.get(
            "associations",
            {}
        )

        if isinstance(associations, dict):

            for word, related in associations.items():

                if not isinstance(related, dict):
                    continue

                state.associations[word] = Counter(
                    {
                        str(key): int(value)
                        for key, value in related.items()
                    }
                )

        # ---------------------------------------------
        # Responses
        # ---------------------------------------------

        responses = data.get(
            "responses",
            {}
        )

        if isinstance(responses, dict):

            for message, values in responses.items():

                if not isinstance(values, dict):
                    continue

                state.responses[message] = Counter(
                    {
                        str(key): int(value)
                        for key, value in values.items()
                    }
                )

        # ---------------------------------------------
        # Statistics
        # ---------------------------------------------

        statistics = data.get(
            "statistics",
            {}
        )

        if isinstance(statistics, dict):

            state.total_messages = int(
                statistics.get(
                    "total_messages",
                    0
                )
            )

            state.total_user_messages = int(
                statistics.get(
                    "total_user_messages",
                    0
                )
            )

            state.total_ai_messages = int(
                statistics.get(
                    "total_ai_messages",
                    0
                )
            )

            state.total_tokens = int(
                statistics.get(
                    "total_tokens",
                    0
                )
            )

            state.total_words = int(
                statistics.get(
                    "total_words",
                    0
                )
            )

            state.total_learning_events = int(
                statistics.get(
                    "total_learning_events",
                    0
                )
            )

        # ---------------------------------------------
        # Context
        # ---------------------------------------------

        context = data.get(
            "context",
            {}
        )

        if isinstance(context, dict):

            state.last_user_message = context.get(
                "last_user_message",
                ""
            )

            state.last_ai_message = context.get(
                "last_ai_message",
                ""
            )

            state.conversation_turn = int(
                context.get(
                    "conversation_turn",
                    0
                )
            )

        # ---------------------------------------------
        # Configuration
        # ---------------------------------------------

        settings = data.get(
            "settings",
            {}
        )

        if isinstance(settings, dict):

            state.learning_enabled = bool(
                settings.get(
                    "learning_enabled",
                    True
                )
            )

        return state


# ============================================================
# MAIN BRAIN CLASS
# ============================================================

class Brain:

    def __init__(
        self,
        brain_file=BRAIN_FILE
    ):

        self.brain_file = brain_file

        self.tokenizer = Tokenizer()

        self.state = BrainState()

        self.random = random.Random()

        self.load()

    # ========================================================
    # LOAD
    # ========================================================

    def load(self):

        if not os.path.exists(
            self.brain_file
        ):
            return False

        try:

            with open(
                self.brain_file,
                "r",
                encoding="utf-8"
            ) as file:

                data = json.load(file)

            if not isinstance(
                data,
                dict
            ):
                return False

            self.state = BrainState.from_dict(
                data
            )

            return True

        except (
            OSError,
            json.JSONDecodeError,
            ValueError,
            TypeError
        ):

            return False

    # ========================================================
    # SAVE
    # ========================================================

    def save(self):

        self.state.touch()

        data = self.state.to_dict()

        temporary_file = (
            self.brain_file + ".tmp"
        )

        try:

            with open(
                temporary_file,
                "w",
                encoding="utf-8"
            ) as file:

                json.dump(
                    data,
                    file,
                    ensure_ascii=False,
                    indent=4
                )

            os.replace(
                temporary_file,
                self.brain_file
            )

            return True

        except OSError:

            try:

                if os.path.exists(
                    temporary_file
                ):
                    os.remove(
                        temporary_file
                    )

            except OSError:
                pass

            return False

    # ========================================================
    # VOCABULARY
    # ========================================================

    def ensure_word(
        self,
        word
    ):

        word = clean_basic_text(
            word
        )

        if not word:
            return None

        if word not in self.state.vocabulary:

            if (
                len(self.state.vocabulary)
                >= MAX_VOCABULARY
            ):
                return None

            self.state.vocabulary[word] = WordInfo(
                word
            )

        return self.state.vocabulary[word]

    def register_word(
        self,
        word,
        response=False,
        question=False,
        command=False
    ):

        info = self.ensure_word(
            word
        )

        if info is None:
            return False

        info.seen(
            response=response,
            question=question,
            command=command
        )

        self.state.token_frequency[word] += 1

        self.state.total_words += 1

        return True

    # ========================================================
    # PUBLIC TOKENIZATION
    # ========================================================

    def tokenize(
        self,
        text
    ):

        return self.tokenizer.tokenize(
            text
        )

    def normalize(
        self,
        text
    ):

        return clean_basic_text(
            text
        )

    def normalize_for_matching(
        self,
        text
    ):

        return clean_for_matching(
            text
        )

    # ========================================================
    # BRAIN INFORMATION
    # ========================================================

    def get_vocabulary_size(self):

        return len(
            self.state.vocabulary
        )

    def get_total_words(self):

        return self.state.total_words

    def get_total_messages(self):

        return self.state.total_messages

    def get_statistics(self):

        return {
            "version": self.state.version,
            "vocabulary": self.get_vocabulary_size(),
            "words": self.state.total_words,
            "messages": self.state.total_messages,
            "user_messages": self.state.total_user_messages,
            "ai_messages": self.state.total_ai_messages,
            "learning_events": self.state.total_learning_events,
            "conversation_turn": self.state.conversation_turn,
        }

    # ========================================================
    # KNOWN WORDS
    # ========================================================

    def knows_word(
        self,
        word
    ):

        word = clean_basic_text(
            word
        )

        return word in self.state.vocabulary

    def get_word_info(
        self,
        word
    ):

        word = clean_basic_text(
            word
        )

        return self.state.vocabulary.get(
            word
        )

    # ========================================================
    # CONTROLLED RESET
    # ========================================================

    def clear_runtime_context(self):

        self.state.last_user_message = ""

        self.state.last_ai_message = ""

        self.state.conversation_turn = 0

        self.state.touch()

    # ========================================================
    # BASE LEARNING
    # ========================================================

    def learn_text(
        self,
        text,
        response=False,
        question=False,
        command=False
    ):

        if not self.state.learning_enabled:
            return 0

        tokens = self.tokenize(
            text
        )

        learned = 0

        for token in tokens:

            if self.register_word(
                token,
                response=response,
                question=question,
                command=command
            ):
                learned += 1

        self.state.total_tokens += len(
            tokens
        )

        self.state.total_learning_events += 1

        self.state.touch()

        return learned


# ============================================================
# END OF BLOCK 1
# ============================================================

# ============================================================
# D-AI
# brain.py
# BLOCK 2/4 - LEARNING AND ASSOCIATIONS
# ============================================================

    # ========================================================
    # LEARN RELATIONSHIPS BETWEEN TOKENS
    # ========================================================

    def learn_associations(
        self,
        text,
        window=2
    ):
        """
        Learns relationships between nearby words.

        Example:

            "I like programming"

        can produce relationships such as:

            I -> like
            I -> programming
            like -> I
            like -> programming
            programming -> I
            programming -> like

        The more often a relationship appears,
        the higher its weight.
        """

        if not self.state.learning_enabled:
            return 0

        tokens = self.tokenize(text)

        if not tokens:
            return 0

        learned = 0

        for index, token in enumerate(tokens):

            if token not in self.state.associations:
                self.state.associations[token] = Counter()

            start = max(
                0,
                index - window
            )

            end = min(
                len(tokens),
                index + window + 1
            )

            for other_index in range(
                start,
                end
            ):

                if other_index == index:
                    continue

                other = tokens[other_index]

                if not other:
                    continue

                self.state.associations[
                    token
                ][other] += 1

                learned += 1

        self.state.total_learning_events += 1

        self.state.touch()

        return learned

    # ========================================================
    # LEARN WORD ORDER
    # ========================================================

    def learn_sequence(
        self,
        text
    ):
        """
        Learns which word usually appears
        after another word.

        This will later be used
        by the text generator.
        """

        if not self.state.learning_enabled:
            return 0

        tokens = self.tokenize(text)

        if len(tokens) < 2:
            return 0

        learned = 0

        for index in range(
            len(tokens) - 1
        ):

            current = tokens[index]

            next_token = tokens[
                index + 1
            ]

            if current not in self.state.associations:
                self.state.associations[
                    current
                ] = Counter()

            self.state.associations[
                current
            ][next_token] += 1

            learned += 1

        self.state.total_learning_events += 1

        self.state.touch()

        return learned

    # ========================================================
    # LEARN RESPONSE
    # ========================================================

    def learn_response(
        self,
        message,
        response
    ):
        """
        Associates a user input
        with a D-AI response.

        Repeated responses receive
        a higher score.
        """

        if not self.state.learning_enabled:
            return False

        message_key = self.normalize_for_matching(
            message
        )

        response = str(
            response
        ).strip()

        if not message_key or not response:
            return False

        if message_key not in self.state.responses:
            self.state.responses[
                message_key
            ] = Counter()

        self.state.responses[
            message_key
        ][response] += 1

        self.state.total_learning_events += 1

        self.state.touch()

        return True

    # ========================================================
    # GET LEARNED RESPONSES
    # ========================================================

    def get_learned_responses(
        self,
        message
    ):
        """
        Returns known responses
        for a message.
        """

        message_key = self.normalize_for_matching(
            message
        )

        responses = self.state.responses.get(
            message_key
        )

        if not responses:
            return []

        return [
            {
                "response": response,
                "score": score
            }
            for response, score
            in responses.items()
        ]

    # ========================================================
    # BEST LEARNED RESPONSE
    # ========================================================

    def get_best_learned_response(
        self,
        message
    ):
        """
        Finds the response that has been
        associated with an input the most times.
        """

        message_key = self.normalize_for_matching(
            message
        )

        responses = self.state.responses.get(
            message_key
        )

        if not responses:
            return None

        best_response = max(
            responses,
            key=responses.get
        )

        return best_response

    # ========================================================
    # ASSOCIATION STRENGTH
    # ========================================================

    def association_strength(
        self,
        first,
        second
    ):
        """
        Returns how many times two words
        have appeared together.
        """

        first = clean_basic_text(
            first
        )

        second = clean_basic_text(
            second
        )

        if not first or not second:
            return 0

        relations = self.state.associations.get(
            first
        )

        if not relations:
            return 0

        return relations.get(
            second,
            0
        )

    # ========================================================
    # RELATED WORDS
    # ========================================================

    def get_related_words(
        self,
        word,
        limit=10
    ):
        """
        Returns the words most strongly related
        to a given word.
        """

        word = clean_basic_text(
            word
        )

        relations = self.state.associations.get(
            word
        )

        if not relations:
            return []

        ordered = relations.most_common(
            limit
        )

        return [
            {
                "word": related,
                "score": score
            }
            for related, score
            in ordered
        ]

    # ========================================================
    # MOST FREQUENT WORDS
    # ========================================================

    def get_most_common_words(
        self,
        limit=20
    ):
        """
        Returns the words that D-AI
        has seen most frequently.
        """

        return [
            {
                "word": word,
                "count": count
            }
            for word, count
            in self.state.token_frequency.most_common(
                limit
            )
        ]

    # ========================================================
    # LEARN A CONVERSATION
    # ========================================================

    def learn_conversation(
        self,
        user_message,
        ai_response
    ):
        """
        Registers a complete conversation turn.

        Learns:

            - vocabulary
            - associations
            - sequences
            - input/response relationship
            - statistics
            - context
        """

        if not self.state.learning_enabled:
            return False

        user_message = str(
            user_message
        ).strip()

        ai_response = str(
            ai_response
        ).strip()

        if not user_message:
            return False

        # ----------------------------------------------------
        # Detect whether this is a question
        # ----------------------------------------------------

        normalized = self.normalize(
            user_message
        )

        is_question = (
            "?" in user_message
            or normalized.startswith(
                (
                    "what ",
                    "how ",
                    "when ",
                    "where ",
                    "why ",
                    "who ",
                )
            )
        )

        # ----------------------------------------------------
        # Learn user message
        # ----------------------------------------------------

        self.learn_text(
            user_message,
            response=False,
            question=is_question
        )

        self.learn_associations(
            user_message
        )

        self.learn_sequence(
            user_message
        )

        # ----------------------------------------------------
        # Learn response
        # ----------------------------------------------------

        self.learn_text(
            ai_response,
            response=True
        )

        self.learn_associations(
            ai_response
        )

        self.learn_sequence(
            ai_response
        )

        # ----------------------------------------------------
        # Associate input with response
        # ----------------------------------------------------

        self.learn_response(
            user_message,
            ai_response
        )

        # ----------------------------------------------------
        # Update statistics
        # ----------------------------------------------------

        self.state.total_messages += 1

        self.state.total_user_messages += 1

        self.state.total_ai_messages += 1

        self.state.conversation_turn += 1

        self.state.last_user_message = (
            user_message
        )

        self.state.last_ai_message = (
            ai_response
        )

        self.state.touch()

        self.save()

        return True

    # ========================================================
    # LEARN TEXT ONLY
    # ========================================================

    def learn(
        self,
        text
    ):
        """
        Public learning method.

        Allows text to be taught to D-AI
        without needing to generate a response.
        """

        if not isinstance(
            text,
            str
        ):
            return False

        text = text.strip()

        if not text:
            return False

        self.learn_text(
            text
        )

        self.learn_associations(
            text
        )

        self.learn_sequence(
            text
        )

        self.save()

        return True

    # ========================================================
    # SIMPLE TEXT SIMILARITY
    # ========================================================

    def text_similarity(
        self,
        first,
        second
    ):
        """
        Calculates basic similarity between two texts.

        Does not use external artificial intelligence.
        """

        first_tokens = set(
            self.tokenizer.tokenize_for_matching(
                first
            )
        )

        second_tokens = set(
            self.tokenizer.tokenize_for_matching(
                second
            )
        )

        if not first_tokens or not second_tokens:
            return 0.0

        intersection = (
            first_tokens
            & second_tokens
        )

        union = (
            first_tokens
            | second_tokens
        )

        if not union:
            return 0.0

        return len(
            intersection
        ) / len(
            union
        )

    # ========================================================
    # FIND SIMILAR MESSAGES
    # ========================================================

    def find_similar_messages(
        self,
        message,
        limit=5,
        minimum_similarity=0.15
    ):
        """
        Searches for previous messages that are
        similar to the current message.
        """

        results = []

        message = str(
            message
        )

        for known_message in self.state.responses:

            similarity = self.text_similarity(
                message,
                known_message
            )

            if similarity < minimum_similarity:
                continue

            results.append(
                {
                    "message": known_message,
                    "similarity": similarity,
                    "responses": self.get_learned_responses(
                        known_message
                    )
                }
            )

        results.sort(
            key=lambda item: item["similarity"],
            reverse=True
        )

        return results[:limit]

    # ========================================================
    # RESPONSE BY SIMILARITY
    # ========================================================

    def response_from_similarity(
        self,
        message,
        minimum_similarity=0.30
    ):
        """
        Attempts to find a response
        using similar previous messages.
        """

        results = self.find_similar_messages(
            message,
            limit=5,
            minimum_similarity=minimum_similarity
        )

        if not results:
            return None

        best = results[0]

        responses = best.get(
            "responses",
            []
        )

        if not responses:
            return None

        responses = sorted(
            responses,
            key=lambda item: item["score"],
            reverse=True
        )

        return responses[0]["response"]

    # ========================================================
    # RESPONSE CONFIDENCE
    # ========================================================

    def response_confidence(
        self,
        message
    ):
        """
        Estimates how confident the brain is
        that it knows the message.

        The result is between 0 and 1.
        """

        exact = self.get_best_learned_response(
            message
        )

        if exact:
            return 1.0

        similar = self.find_similar_messages(
            message,
            limit=1,
            minimum_similarity=0.0
        )

        if not similar:
            return 0.0

        similarity = similar[0][
            "similarity"
        ]

        return max(
            0.0,
            min(
                1.0,
                similarity
            )
        )

    # ========================================================
    # LEARN VARIATIONS
    # ========================================================

    def learn_variation(
        self,
        original,
        variation
    ):
        """
        Associates two phrases that represent
        a similar idea.

        Example:

            hello
            hello!!!
            helloo

        """

        original = self.normalize_for_matching(
            original
        )

        variation = self.normalize_for_matching(
            variation
        )

        if not original or not variation:
            return False

        if original == variation:
            return False

        if original not in self.state.responses:
            self.state.responses[
                original
            ] = Counter()

        known = self.state.responses.get(
            variation
        )

        if known:

            for response, score in known.items():

                self.state.responses[
                    original
                ][response] += score

        self.state.total_learning_events += 1

        self.save()

        return True

    # ========================================================
    # FORGET A LEARNED RESPONSE
    # ========================================================

    def forget_response(
        self,
        message,
        response=None
    ):
        """
        Removes a specific response
        or all responses associated
        with a message.
        """

        message_key = self.normalize_for_matching(
            message
        )

        if message_key not in self.state.responses:
            return False

        if response is None:

            del self.state.responses[
                message_key
            ]

            self.save()

            return True

        responses = self.state.responses[
            message_key
        ]

        if response not in responses:
            return False

        del responses[
            response
        ]

        if not responses:

            del self.state.responses[
                message_key
            ]

        self.save()

        return True

    # ========================================================
    # CLEAR WORD ASSOCIATIONS
    # ========================================================

    def clear_word_associations(
        self,
        word
    ):
        """
        Removes the outgoing associations
        of a word.
        """

        word = clean_basic_text(
            word
        )

        if word not in self.state.associations:
            return False

        del self.state.associations[
            word
        ]

        self.save()

        return True

    # ========================================================
    # GET LEARNING STATUS
    # ========================================================

    def get_learning_status(self):

        return {
            "enabled": self.state.learning_enabled,
            "vocabulary": self.get_vocabulary_size(),
            "messages": self.state.total_messages,
            "words": self.state.total_words,
            "events": self.state.total_learning_events,
            "associations": sum(
                len(values)
                for values
                in self.state.associations.values()
            ),
            "learned_inputs": len(
                self.state.responses
            ),
        }

    # ========================================================
    # ENABLE LEARNING
    # ========================================================

    def enable_learning(self):

        self.state.learning_enabled = True

        self.state.touch()

        self.save()

    # ========================================================
    # DISABLE LEARNING
    # ========================================================

    def disable_learning(self):

        self.state.learning_enabled = False

        self.state.touch()

        self.save()

    # ========================================================
    # SET LEARNING STATE
    # ========================================================

    def set_learning(
        self,
        enabled
    ):

        self.state.learning_enabled = bool(
            enabled
        )

        self.state.touch()

        self.save()


# ============================================================
# END OF BLOCK 2
# ============================================================

# ============================================================
# D-AI
# brain.py
# BLOCK 3/4 - THINKING AND CONTEXT
# ============================================================

    # ========================================================
    # CONVERSATION CONTEXT
    # ========================================================

    def get_context(self):
        """
        Returns the current conversation context.
        """

        return {
            "last_user_message":
                self.state.last_user_message,

            "last_ai_message":
                self.state.last_ai_message,

            "conversation_turn":
                self.state.conversation_turn,
        }

    # ========================================================
    # UPDATE CONTEXT
    # ========================================================

    def update_context(
        self,
        user_message,
        ai_response
    ):
        """
        Updates the context after a conversation turn.
        """

        self.state.last_user_message = (
            str(user_message).strip()
        )

        self.state.last_ai_message = (
            str(ai_response).strip()
        )

        self.state.conversation_turn += 1

        self.state.touch()

    # ========================================================
    # DETECT QUESTION
    # ========================================================

    def is_question(
        self,
        text
    ):
        """
        Determines whether a message appears to be a question.
        """

        if not isinstance(text, str):
            return False

        stripped = text.strip()

        if "?" in stripped:
            return True

        normalized = self.normalize_for_matching(
            stripped
        )

        question_starters = (
            "what ",
            "how ",
            "when ",
            "where ",
            "why ",
            "who ",
            "which ",
            "how much ",
            "how many ",
            "can you ",
            "can i ",
            "is ",
            "are ",
            "do you ",
            "do i ",
            "does ",
            "did ",
            "have you ",
        )

        return normalized.startswith(
            question_starters
        )

    # ========================================================
    # DETECT INTENT
    # ========================================================

    def detect_intent(
        self,
        text
    ):
        """
        Detects the main intent of a message.
        """

        normalized = self.normalize_for_matching(
            text
        )

        if not normalized:
            return "empty"

        tokens = set(
            self.tokenizer.tokenize_for_matching(
                normalized
            )
        )

        # ----------------------------------------------------
        # Greeting
        # ----------------------------------------------------

        greetings = {
            "hello",
            "hi",
            "hey",
            "hola",
            "yo",
            "sup",
            "heyy",
            "helloo",
        }

        if tokens & greetings:
            return "greeting"

        # ----------------------------------------------------
        # Goodbye
        # ----------------------------------------------------

        goodbyes = {
            "goodbye",
            "bye",
            "cya",
            "see",
            "later",
        }

        if tokens & goodbyes:
            return "goodbye"

        # ----------------------------------------------------
        # Status
        # ----------------------------------------------------

        status_patterns = [
            "how are you",
            "how are you doing",
            "how do you feel",
            "how have you been",
            "are you okay",
        ]

        if any(
            pattern in normalized
            for pattern in status_patterns
        ):
            return "status"

        # ----------------------------------------------------
        # User name
        # ----------------------------------------------------

        name_patterns = [
            "what is my name",
            "whats my name",
            "what's my name",
            "do you remember my name",
            "do you know my name",
            "what do you call me",
        ]

        if any(
            pattern in normalized
            for pattern in name_patterns
        ):
            return "user_name"

        # ----------------------------------------------------
        # D-AI name
        # ----------------------------------------------------

        ai_name_patterns = [
            "what is your name",
            "whats your name",
            "what's your name",
            "what are you called",
            "what is the ai called",
            "what is this ai called",
        ]

        if any(
            pattern in normalized
            for pattern in ai_name_patterns
        ):
            return "ai_name"

        # ----------------------------------------------------
        # General question
        # ----------------------------------------------------

        if self.is_question(text):
            return "question"

        # ----------------------------------------------------
        # Positive statement
        # ----------------------------------------------------

        positive = {
            "good",
            "great",
            "perfect",
            "excellent",
            "amazing",
            "awesome",
            "fantastic",
            "nice",
            "okay",
            "ok",
            "yes",
            "yeah",
            "yep",
            "fine",
        }

        if tokens & positive:
            return "positive"

        # ----------------------------------------------------
        # Negative statement
        # ----------------------------------------------------

        negative = {
            "no",
            "bad",
            "never",
            "neither",
            "nope",
            "nah",
            "not",
        }

        if tokens & negative:
            return "negative"

        # ----------------------------------------------------
        # Thanks
        # ----------------------------------------------------

        thanks = {
            "thanks",
            "thank",
            "thx",
            "ty",
        }

        if tokens & thanks:
            return "thanks"

        return "unknown"

    # ========================================================
    # GET BASIC SEMANTIC MEMORY
    # ========================================================

    def get_known_information(
        self,
        text
    ):
        """
        Searches for known words inside a message.
        """

        tokens = self.tokenizer.tokenize(
            text
        )

        result = []

        for token in tokens:

            if self.knows_word(token):

                info = self.get_word_info(
                    token
                )

                if info is not None:

                    result.append(
                        {
                            "word": token,
                            "count": info.count,
                            "response_count":
                                info.response_count,
                            "question_count":
                                info.question_count,
                        }
                    )

        return result

    # ========================================================
    # GET IMPORTANT WORDS
    # ========================================================

    def get_important_words(
        self,
        text
    ):
        """
        Filters common words to find
        potentially important concepts.
        """

        stopwords = {
            "a",
            "an",
            "the",
            "of",
            "to",
            "in",
            "on",
            "at",
            "for",
            "from",
            "with",
            "without",
            "and",
            "or",
            "but",
            "if",
            "then",
            "than",
            "that",
            "this",
            "these",
            "those",
            "what",
            "how",
            "when",
            "where",
            "why",
            "who",
            "which",
            "my",
            "your",
            "you",
            "i",
            "me",
            "we",
            "us",
            "they",
            "them",
            "is",
            "am",
            "are",
            "was",
            "were",
            "be",
            "been",
            "being",
            "do",
            "does",
            "did",
            "can",
            "could",
            "will",
            "would",
            "should",
            "have",
            "has",
            "had",
        }

        tokens = self.tokenizer.tokenize(
            text
        )

        return [
            token
            for token in tokens
            if token not in stopwords
            and len(token) > 1
        ]

    # ========================================================
    # FIND MAIN CONCEPT
    # ========================================================

    def find_main_concept(
        self,
        text
    ):
        """
        Attempts to find the main concept
        of a sentence.
        """

        important = self.get_important_words(
            text
        )

        if not important:
            return None

        scored = []

        for word in important:

            frequency = (
                self.state.token_frequency.get(
                    word,
                    0
                )
            )

            association_count = sum(
                self.state.associations.get(
                    word,
                    {}
                ).values()
            )

            score = (
                frequency
                + association_count
            )

            scored.append(
                (
                    word,
                    score
                )
            )

        scored.sort(
            key=lambda item: item[1],
            reverse=True
        )

        return scored[0][0]

    # ========================================================
    # RESPONSE FOR USER NAME
    # ========================================================

    def answer_user_name(
        self
    ):
        """
        Looks up the user's name stored
        in the knowledge system.
        """

        # Compatibility with the previous
        # memory system if it exists.
        memory = getattr(
            self,
            "memory",
            None
        )

        if memory is not None:

            try:

                name = memory.recall_fact(
                    "user_name"
                )

                if name:
                    return (
                        f"Your name is {name}."
                    )

            except Exception:
                pass

        # Search learned responses
        candidates = [
            "user_name",
            "name",
        ]

        for key in candidates:

            if key in self.state.vocabulary:

                return (
                    "I remember that you "
                    "told me your name before."
                )

        return (
            "I don't know your name yet."
        )

    # ========================================================
    # RESPONSE FOR D-AI NAME
    # ========================================================

    def answer_ai_name(
        self
    ):
        """
        Basic D-AI identity.
        """

        return (
            "My name is D-AI."
        )

    # ========================================================
    # GREETING RESPONSE
    # ========================================================

    def answer_greeting(
        self,
        text
    ):
        """
        Responds to greetings.
        """

        variations = [
            "Hello! How are you?",
            "Hello! 😎",
            "Hey! What's up?",
            "Hey! How's it going?",
        ]

        # If we already know the exact greeting,
        # prioritize a learned response.
        learned = self.get_best_learned_response(
            text
        )

        if learned:
            return learned

        return self.random.choice(
            variations
        )

    # ========================================================
    # POSITIVE RESPONSE
    # ========================================================

    def answer_positive(
        self,
        text
    ):
        """
        Responds to positive expressions.
        """

        variations = [
            "Great! 😎",
            "I'm glad!",
            "Perfect!",
            "That sounds good 😎",
            "Excellent!",
        ]

        learned = self.get_best_learned_response(
            text
        )

        if learned:
            return learned

        return self.random.choice(
            variations
        )

    # ========================================================
    # STATUS RESPONSE
    # ========================================================

    def answer_status(
        self
    ):
        return (
            "I'm doing well. I'm still learning."
        )

    # ========================================================
    # GOODBYE RESPONSE
    # ========================================================

    def answer_goodbye(
        self
    ):
        return self.random.choice(
            [
                "See you later!",
                "See you!",
                "Bye!",
            ]
        )

    # ========================================================
    # THANKS RESPONSE
    # ========================================================

    def answer_thanks(
        self
    ):
        return self.random.choice(
            [
                "You're welcome!",
                "No problem!",
                "That's what I'm here for!",
            ]
        )

    # ========================================================
    # UNKNOWN MESSAGE RESPONSE
    # ========================================================

    def answer_unknown(
        self,
        text
    ):
        """
        Attempts to use existing knowledge
        before giving up.
        """

        learned = self.get_best_learned_response(
            text
        )

        if learned:
            return learned

        similar = self.response_from_similarity(
            text,
            minimum_similarity=0.45
        )

        if similar:
            return similar

        concept = self.find_main_concept(
            text
        )

        if concept:

            related = self.get_related_words(
                concept,
                limit=5
            )

            if related:

                related_words = [
                    item["word"]
                    for item in related
                ]

                preview = ", ".join(
                    related_words[:3]
                )

                return (
                    f"I'm learning about "
                    f"'{concept}'. "
                    f"I associate it with: {preview}."
                )

        return (
            "I don't know that yet. "
            "You can teach me."
        )

    # ========================================================
    # THINKING ENGINE
    # ========================================================

    def think_message(
        self,
        message
    ):
        """
        Main basic reasoning engine.

        Order:

            1. learned memory
            2. intent
            3. special responses
            4. similarity
            5. knowledge
            6. unknown
        """

        if not isinstance(
            message,
            str
        ):
            return (
                "I couldn't process that message."
            )

        message = message.strip()

        if not message:
            return (
                "I didn't receive a message."
            )

        # ----------------------------------------------------
        # Exact learned response
        # ----------------------------------------------------

        exact = self.get_best_learned_response(
            message
        )

        if exact:
            return exact

        # ----------------------------------------------------
        # Detect intent
        # ----------------------------------------------------

        intent = self.detect_intent(
            message
        )

        # ----------------------------------------------------
        # Process intent
        # ----------------------------------------------------

        if intent == "greeting":
            return self.answer_greeting(
                message
            )

        if intent == "goodbye":
            return self.answer_goodbye()

        if intent == "status":
            return self.answer_status()

        if intent == "user_name":
            return self.answer_user_name()

        if intent == "ai_name":
            return self.answer_ai_name()

        if intent == "positive":
            return self.answer_positive(
                message
            )

        if intent == "thanks":
            return self.answer_thanks()

        # ----------------------------------------------------
        # Question
        # ----------------------------------------------------

        if intent == "question":

            similar = self.response_from_similarity(
                message,
                minimum_similarity=0.50
            )

            if similar:
                return similar

        # ----------------------------------------------------
        # Unknown
        # ----------------------------------------------------

        return self.answer_unknown(
            message
        )

    # ========================================================
    # RESPOND AND LEARN
    # ========================================================

    def respond(
        self,
        message
    ):
        """
        Processes a complete message.

        First it thinks.
        Then it learns the conversation turn.
        Finally it updates the context.
        """

        response = self.think_message(
            message
        )

        self.update_context(
            message,
            response
        )

        self.learn_conversation(
            message,
            response
        )

        return response

    # ========================================================
    # DIAGNOSTIC MODE
    # ========================================================

    def diagnose(
        self,
        message
    ):
        """
        Returns detailed information about the processing
        so the Thinker can display it.
        """

        tokens = self.tokenize(
            message
        )

        normalized = self.normalize(
            message
        )

        matching = self.normalize_for_matching(
            message
        )

        intent = self.detect_intent(
            message
        )

        concept = self.find_main_concept(
            message
        )

        confidence = self.response_confidence(
            message
        )

        known_words = self.get_known_information(
            message
        )

        similar = self.find_similar_messages(
            message,
            limit=5,
            minimum_similarity=0.0
        )

        return {
            "input": message,
            "normalized": normalized,
            "matching": matching,
            "tokens": tokens,
            "intent": intent,
            "main_concept": concept,
            "confidence": confidence,
            "known_words": known_words,
            "similar_messages": similar,
            "context": self.get_context(),
        }

    # ========================================================
    # THINKING FOR THINKER
    # ========================================================

    def thinker_process(
        self,
        message
    ):
        """
        Executes diagnosis + response.
        """

        diagnosis = self.diagnose(
            message
        )

        response = self.think_message(
            message
        )

        diagnosis["response"] = response

        return diagnosis


# ============================================================
# END OF BLOCK 3
# ============================================================
# ============================================================
# D-AI
# brain.py
# BLOCK 4/4 - ADVANCED MEMORY AND RESPONSE ENGINE
# ============================================================

    # ========================================================
    # EXTERNAL MEMORY
    # ========================================================

    def _get_external_memory(
        self
    ):
        """
        Lazily loads memory.py.

        This allows Brain to work even if the
        memory module is not available yet.
        """

        memory = getattr(
            self,
            "_external_memory",
            None
        )

        if memory is not None:
            return memory

        try:

            from memory import Memory

            memory = Memory()

            self._external_memory = memory

            return memory

        except Exception:

            self._external_memory = None

            return None

    # ========================================================
    # SAVE A FACT
    # ========================================================

    def _remember_fact(
        self,
        key,
        value
    ):
        """
        Saves a fact to memory.py.
        """

        if not key:
            return False

        if value is None:
            return False

        value = str(value).strip()

        if not value:
            return False

        memory = self._get_external_memory()

        if memory is None:
            return False

        try:

            memory.remember_fact(
                str(key).strip(),
                value
            )

            return True

        except Exception:

            return False

    # ========================================================
    # READ A FACT
    # ========================================================

    def _recall_fact(
        self,
        key
    ):
        """
        Retrieves a fact from memory.py.
        """

        memory = self._get_external_memory()

        if memory is None:
            return None

        try:

            value = memory.recall_fact(
                str(key).strip()
            )

            if value is None:
                return None

            return str(value).strip()

        except Exception:

            return None

    # ========================================================
    # SAVE EXTERNAL CONVERSATION
    # ========================================================

    def _remember_external_conversation(
        self,
        user_message,
        ai_response
    ):
        """
        Saves the conversation turn to memory.py.
        """

        memory = self._get_external_memory()

        if memory is None:
            return False

        try:

            memory.remember_conversation(
                str(user_message),
                str(ai_response)
            )

            return True

        except Exception:

            return False

    # ========================================================
    # EXTRACT NAME
    # ========================================================

    def extract_name(
        self,
        text
    ):
        """
        Detects phrases such as:

        my name is Daniel
        I am Daniel
        I'm Daniel
        you can call me Daniel
        call me Daniel
        """

        if not isinstance(
            text,
            str
        ):
            return None

        original = normalize_spaces(
            text
        )

        normalized = normalize_for_search(
            original
        )

        patterns = [
            r"\bmy name is ([a-záéíóúüñ0-9_-]+)",
            r"\bi am ([a-záéíóúüñ0-9_-]+)",
            r"\bi'm ([a-záéíóúüñ0-9_-]+)",
            r"\byou can call me ([a-záéíóúüñ0-9_-]+)",
            r"\bcall me ([a-záéíóúüñ0-9_-]+)",
        ]

        for pattern in patterns:

            match = re.search(
                pattern,
                normalized,
                re.IGNORECASE
            )

            if match:

                name = match.group(
                    1
                ).strip()

                if name:

                    return name

        return None

    # ========================================================
    # LEARN NAME
    # ========================================================

    def learn_name(
        self,
        text
    ):
        """
        Attempts to automatically learn
        the user's name.
        """

        name = self.extract_name(
            text
        )

        if not name:
            return False

        self._remember_fact(
            "user_name",
            name
        )

        self.learn_text(
            name
        )

        return True

    # ========================================================
    # EXTRACT SIMPLE FACTS
    # ========================================================

    def extract_fact(
        self,
        text
    ):
        """
        Detects simple facts that the user
        can teach D-AI.

        Returns:
            (key, value)
        """

        if not isinstance(
            text,
            str
        ):
            return None

        normalized = normalize_for_search(
            text
        )

        patterns = [

            (
                "favorite_color",
                r"\bmy favorite color is (.+)"
            ),

            (
                "favorite_game",
                r"\bmy favorite game is (.+)"
            ),

            (
                "favorite_language",
                r"\bmy favorite language is (.+)"
            ),

            (
                "current_project",
                r"\bi am working on (.+)"
            ),

            (
                "current_project",
                r"\bmy project is (.+)"
            ),

            (
                "favorite_program",
                r"\bmy favorite program is (.+)"
            ),

            (
                "favorite_system",
                r"\bmy favorite system is (.+)"
            ),
        ]

        for key, pattern in patterns:

            match = re.search(
                pattern,
                normalized,
                re.IGNORECASE
            )

            if match:

                value = match.group(
                    1
                ).strip()

                value = re.sub(
                    r"[.!?]+$",
                    "",
                    value
                )

                if value:

                    return (
                        key,
                        value
                    )

        return None

    # ========================================================
    # LEARN FACT
    # ========================================================

    def learn_fact(
        self,
        text
    ):
        """
        Automatically learns a detected fact.
        """

        result = self.extract_fact(
            text
        )

        if result is None:
            return False

        key, value = result

        return self._remember_fact(
            key,
            value
        )

    # ========================================================
    # GET FACT
    # ========================================================

    def answer_fact(
        self,
        key,
        label
    ):
        """
        Responds using a stored fact.
        """

        value = self._recall_fact(
            key
        )

        if value:

            return (
                f"Your {label} is {value}."
            )

        return (
            f"I don't know your {label} yet."
        )

    # ========================================================
    # QUERY PERSONAL DATA
    # ========================================================

    def answer_stored_fact(
        self,
        text
    ):
        """
        Detects questions about previously
        learned data.
        """

        normalized = normalize_for_search(
            text
        )

        if (
            "what is my favorite color"
            in normalized
            or
            "what is your favorite color"
            in normalized
        ):

            value = self._recall_fact(
                "favorite_color"
            )

            if value:
                return (
                    f"Your favorite color is {value}."
                )

        if (
            "what is my favorite game"
            in normalized
        ):

            value = self._recall_fact(
                "favorite_game"
            )

            if value:
                return (
                    f"Your favorite game is {value}."
                )

        if (
            "what am i working on"
            in normalized
            or
            "what am i working"
            in normalized
        ):

            value = self._recall_fact(
                "current_project"
            )

            if value:
                return (
                    f"You are working on {value}."
                )

        if (
            "what is my favorite language"
            in normalized
        ):

            value = self._recall_fact(
                "favorite_language"
            )

            if value:
                return (
                    f"Your favorite language is {value}."
                )

        return None

    # ========================================================
    # REFERENCE TO PREVIOUS TURN
    # ========================================================

    def handle_context_reference(
        self,
        text
    ):
        """
        Handles short expressions that depend
        on the conversation context, such as:

        and you
        me too
        that
        sure
        exactly
        """

        normalized = normalize_for_search(
            text
        )

        previous = self.state.last_ai_message

        if not previous:
            return None

        if normalized in {
            "and you",
            "and you?",
        }:

            return (
                "I'm doing well too 😎"
            )

        if normalized in {
            "me too",
            "me neither",
        }:

            return (
                "😎"
            )

        if normalized in {
            "sure",
            "exactly",
            "i understand",
            "understood",
        }:

            return (
                "Yes, exactly."
            )

        return None

    # ========================================================
    # NEGATIVE RESPONSE
    # ========================================================

    def answer_negative(
        self,
        text
    ):
        return self.random.choice(
            [
                "I understand.",
                "Alright.",
                "That's okay.",
                "Understood.",
            ]
        )

    # ========================================================
    # COMMAND RESPONSES
    # ========================================================

    def command_response(
        self,
        text
    ):
        """
        Processes special D-AI commands.

        Examples:

        learn: hello world
        remember: favorite_color=blue
        statistics
        vocabulary
        save
        """

        if not isinstance(
            text,
            str
        ):
            return None

        normalized = normalize_for_search(
            text
        )

        if normalized == "statistics":

            stats = self.get_statistics()

            return (
                "D-AI Statistics:\n"
                f"Vocabulary: {stats['vocabulary']}\n"
                f"Words: {stats['words']}\n"
                f"Messages: {stats['messages']}\n"
                f"User messages: "
                f"{stats['user_messages']}\n"
                f"D-AI messages: "
                f"{stats['ai_messages']}\n"
                f"Learning events: "
                f"{stats['learning_events']}"
            )

        if normalized == "vocabulary":

            words = self.get_most_common_words(
                limit=20
            )

            if not words:

                return (
                    "My vocabulary is still empty."
                )

            names = [
                item["word"]
                for item in words
            ]

            return (
                "Most known words: "
                + ", ".join(names)
            )

        if normalized == "save":

            if self.save():

                return (
                    "Brain saved successfully."
                )

            return (
                "I could not save the brain."
            )

        if normalized == "clear context":

            self.clear_runtime_context()

            return (
                "Conversation context cleared."
            )

        if normalized == "learning on":

            self.enable_learning()

            return (
                "Learning enabled."
            )

        if normalized == "learning off":

            self.disable_learning()

            return (
                "Learning disabled."
            )

        if normalized.startswith(
            "learn:"
        ):

            content = text.split(
                ":",
                1
            )[1].strip()

            if not content:

                return (
                    "There is nothing to learn."
                )

            learned = self.learn(
                content
            )

            return (
                f"I learned {learned} "
                f"new elements."
            )

        if normalized.startswith(
            "remember:"
        ):

            content = text.split(
                ":",
                1
            )[1].strip()

            if "=" not in content:

                return (
                    "Use the format: "
                    "remember: key=value"
                )

            key, value = content.split(
                "=",
                1
            )

            key = key.strip()
            value = value.strip()

            if not key or not value:

                return (
                    "The key or value is empty."
                )

            if self._remember_fact(
                key,
                value
            ):

                return (
                    f"I'll remember '{key}'."
                )

            return (
                "I could not save that memory."
            )

        return None

    # ========================================================
    # GENERATION BY ASSOCIATIONS
    # ========================================================

    def generate_from_associations(
        self,
        text,
        max_words=18
    ):
        """
        Generates a small response using
        learned associations.

        This is not a neural network yet.
        It is a simple statistical generator.
        """

        important = self.get_important_words(
            text
        )

        if not important:
            return None

        candidates = Counter()

        for word in important:

            related = self.state.associations.get(
                word,
                {}
            )

            for candidate, count in related.items():

                if candidate == word:
                    continue

                candidates[
                    candidate
                ] += count

        if not candidates:
            return None

        result = []

        current = max(
            candidates,
            key=candidates.get
        )

        result.append(
            current
        )

        used = set(
            result
        )

        for _ in range(
            max_words - 1
        ):

            related = self.state.associations.get(
                current,
                {}
            )

            if not related:
                break

            ranked = sorted(
                related.items(),
                key=lambda item: item[1],
                reverse=True
            )

            next_word = None

            for candidate, count in ranked:

                if candidate in used:
                    continue

                if count <= 0:
                    continue

                next_word = candidate
                break

            if next_word is None:
                break

            result.append(
                next_word
            )

            used.add(
                next_word
            )

            current = next_word

        if len(result) < 2:
            return None

        sentence = self.tokenizer.detokenize(
            result
        )

        if not sentence:
            return None

        return (
            sentence[0].upper()
            + sentence[1:]
            + "."
        )

    # ========================================================
    # EVALUATE GENERATION
    # ========================================================

    def generation_is_useful(
        self,
        text,
        generated
    ):
        """
        Checks whether a statistical generation
        has enough relation to the input.
        """

        if not generated:
            return False

        source = set(
            self.get_important_words(
                text
            )
        )

        output = set(
            self.get_important_words(
                generated
            )
        )

        if not source:
            return False

        if not output:
            return False

        overlap = (
            len(source & output)
            / max(
                1,
                len(source)
            )
        )

        return overlap >= 0.15

    # ========================================================
    # LEARNING RESPONSE
    # ========================================================

    def answer_learning(
        self,
        text
    ):
        """
        Explains that D-AI learned something.
        """

        name = self.extract_name(
            text
        )

        if name:

            return (
                f"Got it! I'll remember that "
                f"your name is {name}."
            )

        fact = self.extract_fact(
            text
        )

        if fact:

            key, value = fact

            labels = {
                "favorite_color":
                    "your favorite color",

                "favorite_game":
                    "your favorite game",

                "favorite_language":
                    "your favorite language",

                "current_project":
                    "your current project",

                "favorite_program":
                    "your favorite program",

                "favorite_system":
                    "your favorite system",
            }

            label = labels.get(
                key,
                key
            )

            return (
                f"Got it! I'll remember that "
                f"{label} is {value}."
            )

        return None

    # ========================================================
    # SMART RESPONSE
    # ========================================================

    def smart_response(
        self,
        message
    ):
        """
        Main response engine.

        Order matters:
        1. commands
        2. explicit learning
        3. memory
        4. context
        5. intent
        6. learned responses
        7. similarity
        8. associations
        9. unknown
        """

        if not isinstance(
            message,
            str
        ):
            return (
                "I could not process that message."
            )

        message = message.strip()

        if not message:

            return (
                "I did not receive a message."
            )

        command = self.command_response(
            message
        )

        if command is not None:
            return command

        learned = self.answer_learning(
            message
        )

        if learned is not None:

            self.learn_name(
                message
            )

            self.learn_fact(
                message
            )

            return learned

        stored = self.answer_stored_fact(
            message
        )

        if stored is not None:
            return stored

        context_response = (
            self.handle_context_reference(
                message
            )
        )

        if context_response is not None:
            return context_response

        intent = self.detect_intent(
            message
        )

        if intent == "greeting":

            return self.answer_greeting(
                message
            )

        if intent == "goodbye":

            return self.answer_goodbye()

        if intent == "status":

            return self.answer_status()

        if intent == "user_name":

            return self.answer_user_name()

        if intent == "ai_name":

            return self.answer_ai_name()

        if intent == "positive":

            return self.answer_positive(
                message
            )

        if intent == "negative":

            return self.answer_negative(
                message
            )

        if intent == "thanks":

            return self.answer_thanks()

        learned = (
            self.get_best_learned_response(
                message
            )
        )

        if learned:

            return learned

        if intent == "question":

            similar = (
                self.response_from_similarity(
                    message,
                    minimum_similarity=0.50
                )
            )

            if similar:
                return similar

        similar = (
            self.response_from_similarity(
                message,
                minimum_similarity=0.65
            )
        )

        if similar:

            return similar

        generated = (
            self.generate_from_associations(
                message
            )
        )

        if self.generation_is_useful(
            message,
            generated
        ):

            return generated

        return self.answer_unknown(
            message
        )

    # ========================================================
    # MODIFIED RESPOND
    # ========================================================

    def respond(
        self,
        message
    ):
        """
        Processes a complete conversation turn.

        This connects:

        - memory
        - learning
        - brain
        - context
        - response
        """

        if not isinstance(
            message,
            str
        ):
            return (
                "I could not process that message."
            )

        message = message.strip()

        if not message:

            return (
                "I did not receive a message."
            )

        response = self.smart_response(
            message
        )

        self.update_context(
            message,
            response
        )

        if self.state.learning_enabled:

            self.learn_conversation(
                message,
                response
            )

            self.learn_name(
                message
            )

            self.learn_fact(
                message
            )

        self._remember_external_conversation(
            message,
            response
        )

        return response

    # ========================================================
    # LEARN MANY MESSAGES
    # ========================================================

    def learn_batch(
        self,
        messages
    ):
        """
        Learns a list of texts.
        """

        if messages is None:
            return 0

        learned = 0

        for message in messages:

            if not isinstance(
                message,
                str
            ):
                continue

            message = message.strip()

            if not message:
                continue

            learned += self.learn(
                message
            )

        self.save()

        return learned

    # ========================================================
    # VOCABULARY CLEANUP
    # ========================================================

    def prune_vocabulary(
        self,
        minimum_count=1
    ):
        """
        Removes low-frequency words.

        This prevents the brain from growing
        indefinitely with useless data.
        """

        if minimum_count < 1:

            minimum_count = 1

        to_remove = []

        for word, info in (
            self.state.vocabulary.items()
        ):

            if info.count < minimum_count:

                to_remove.append(
                    word
                )

        for word in to_remove:

            self.state.vocabulary.pop(
                word,
                None
            )

            self.state.token_frequency.pop(
                word,
                None
            )

            self.state.associations.pop(
                word,
                None
            )

        for word in list(
            self.state.associations.keys()
        ):

            counter = (
                self.state.associations[
                    word
                ]
            )

            for candidate in list(
                counter.keys()
            ):

                if candidate in to_remove:

                    counter.pop(
                        candidate,
                        None
                    )

        self.save()

        return len(
            to_remove
        )

    # ========================================================
    # CLEAN RESPONSES
    # ========================================================

    def prune_responses(
        self,
        maximum=5000
    ):
        """
        Limits the number of messages stored
        in statistical memory.
        """

        if maximum < 1:

            maximum = 1

        if len(
            self.state.responses
        ) <= maximum:

            return 0

        items = sorted(
            self.state.responses.items(),
            key=lambda item: sum(
                item[1].values()
            ),
            reverse=True
        )

        keep = dict(
            items[:maximum]
        )

        removed = (
            len(self.state.responses)
            - len(keep)
        )

        self.state.responses = (
            defaultdict(
                Counter,
                keep
            )
        )

        self.save()

        return removed

    # ========================================================
    # VALIDATE BRAIN
    # ========================================================

    def validate_state(
        self
    ):
        """
        Checks whether the internal state is valid.
        """

        problems = []

        if not isinstance(
            self.state.vocabulary,
            dict
        ):

            problems.append(
                "vocabulary is not a dict"
            )

        if not isinstance(
            self.state.associations,
            dict
        ):

            problems.append(
                "associations is not a dict"
            )

        if not isinstance(
            self.state.responses,
            dict
        ):

            problems.append(
                "responses is not a dict"
            )

        if self.state.total_words < 0:

            problems.append(
                "total_words is negative"
            )

        if self.state.total_messages < 0:

            problems.append(
                "total_messages is negative"
            )

        if self.state.conversation_turn < 0:

            problems.append(
                "conversation_turn is negative"
            )

        return {
            "valid": len(
                problems
            ) == 0,

            "problems": problems,
        }

    # ========================================================
    # REPAIR STATE
    # ========================================================

    def repair_state(
        self
    ):
        """
        Repairs basic corrupted values.
        """

        if not isinstance(
            self.state.vocabulary,
            dict
        ):

            self.state.vocabulary = {}

        if not isinstance(
            self.state.associations,
            defaultdict
        ):

            self.state.associations = (
                defaultdict(
                    Counter,
                    self.state.associations
                )
            )

        if not isinstance(
            self.state.responses,
            defaultdict
        ):

            self.state.responses = (
                defaultdict(
                    Counter,
                    self.state.responses
                )
            )

        self.state.total_words = max(
            0,
            int(
                self.state.total_words
            )
        )

        self.state.total_messages = max(
            0,
            int(
                self.state.total_messages
            )
        )

        self.state.total_user_messages = max(
            0,
            int(
                self.state.total_user_messages
            )
        )

        self.state.total_ai_messages = max(
            0,
            int(
                self.state.total_ai_messages
            )
        )

        self.state.total_learning_events = max(
            0,
            int(
                self.state.total_learning_events
            )
        )

        self.state.conversation_turn = max(
            0,
            int(
                self.state.conversation_turn
            )
        )

        self.state.touch()

        self.save()

        return self.validate_state()

    # ========================================================
    # EXPORT BRAIN INFORMATION
    # ========================================================

    def export_summary(
        self
    ):
        """
        Returns a summarized representation
        of the brain.
        """

        stats = self.get_statistics()

        common = (
            self.get_most_common_words(
                limit=10
            )
        )

        related = {}

        for item in common:

            word = item["word"]

            related[word] = (
                self.get_related_words(
                    word,
                    limit=5
                )
            )

        return {
            "statistics": stats,
            "common_words": common,
            "related_words": related,
            "context": self.get_context(),
            "learning": (
                self.get_learning_status()
            ),
        }

    # ========================================================
    # DEBUG MODE
    # ========================================================

    def debug_response(
        self,
        message
    ):
        """
        Returns detailed information about how
        D-AI processes an input.
        """

        diagnosis = self.diagnose(
            message
        )

        diagnosis["external_memory"] = (
            self._get_external_memory()
            is not None
        )

        diagnosis["stored_name"] = (
            self._recall_fact(
                "user_name"
            )
        )

        diagnosis["stored_color"] = (
            self._recall_fact(
                "favorite_color"
            )
        )

        diagnosis["stored_game"] = (
            self._recall_fact(
                "favorite_game"
            )
        )

        return diagnosis

    # ========================================================
    # THINKER STATE
    # ========================================================

    def thinker_state(
        self,
        message
    ):
        """
        Generates data for the Thinker window.
        """

        diagnosis = self.debug_response(
            message
        )

        return {
            "input": diagnosis.get(
                "input",
                ""
            ),

            "tokens": diagnosis.get(
                "tokens",
                []
            ),

            "intent": diagnosis.get(
                "intent",
                "unknown"
            ),

            "concept": diagnosis.get(
                "main_concept",
                None
            ),

            "confidence": diagnosis.get(
                "confidence",
                0.0
            ),

            "known_words": diagnosis.get(
                "known_words",
                []
            ),

            "similar": diagnosis.get(
                "similar_messages",
                []
            ),

            "response": diagnosis.get(
                "response",
                ""
            ),

            "memory": {
                "name": self._recall_fact(
                    "user_name"
                ),

                "color": self._recall_fact(
                    "favorite_color"
                ),

                "game": self._recall_fact(
                    "favorite_game"
                ),

                "project": self._recall_fact(
                    "current_project"
                ),
            },
        }

    # ========================================================
    # AUTOSAVE
    # ========================================================

    def autosave(
        self
    ):
        """
        Saves the brain and returns whether it worked.
        """

        return self.save()

    # ========================================================
    # COMPLETE RESET
    # ========================================================

    def reset_brain(
        self
    ):
        """
        Resets the statistical brain.

        Does NOT delete memory.json.
        """

        self.state = BrainState()

        self.save()

        return True

    # ========================================================
    # DELETE EXTERNAL MEMORY
    # ========================================================

    def forget_fact(
        self,
        key
    ):
        """
        Attempts to delete a fact from memory.py.
        """

        memory = self._get_external_memory()

        if memory is None:
            return False

        try:

            key = str(
                key
            ).lower().strip()

            if key in memory.data.get(
                "facts",
                {}
            ):

                del memory.data[
                    "facts"
                ][key]

                memory.save()

                return True

        except Exception:
            pass

        return False

    # ========================================================
    # FORGET COMMAND
    # ========================================================

    def handle_forget_command(
        self,
        text
    ):
        """
        Processes:

        forget: user_name
        """

        normalized = normalize_for_search(
            text
        )

        if not normalized.startswith(
            "forget:"
        ):

            return None

        key = text.split(
            ":",
            1
        )[1].strip()

        if not key:

            return (
                "Tell me which memory I should forget."
            )

        if self.forget_fact(
            key
        ):

            return (
                f"I forgot '{key}'."
            )

        return (
            f"I could not find a memory called "
            f"'{key}'."
        )

    # ========================================================
    # FINAL THINKER
    # ========================================================

    def process_with_thinker(
        self,
        message
    ):
        """
        Processes an input and returns both the response
        and the internal information required by the
        Thinker GUI.
        """

        response = self.respond(
            message
        )

        diagnosis = self.debug_response(
            message
        )

        diagnosis["response"] = response

        return diagnosis

    # ========================================================
    # BRAIN INFORMATION
    # ========================================================

    def brain_info(
        self
    ):
        """
        General information about D-AI.
        """

        stats = self.get_statistics()

        return {
            "name": "D-AI",

            "type":
                "statistical conversational "
                "engine with memory",

            "version":
                stats["version"],

            "vocabulary":
                stats["vocabulary"],

            "words":
                stats["words"],

            "messages":
                stats["messages"],

            "learning_enabled":
                self.state.learning_enabled,

            "memory_available":
                self._get_external_memory()
                is not None,
        }


    # ========================================================
    # END OF BLOCK 4
    # ========================================================

    # ========================================================
    # DEBUG BLOCK
    # ========================================================

    # ============================================================
    # PATCH - USER NAME MEMORY
    # ============================================================

    def answer_user_name(self):
        name = self._recall_fact("user_name")

        if name:
            return f"Your name is {name}."

        return "I don't know your name yet."

    #====================
    # END OF PATCH
    #====================

#====================
# END OF BRAIN.PY
#====================