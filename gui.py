# ============================================================
# D-AI
# gui.py
# BLOCK 1/2 - MAIN GRAPHICAL INTERFACE
# ============================================================

import tkinter as tk
from tkinter import scrolledtext
from tkinter import messagebox
from tkinter import filedialog
import threading
import time
import json
import os

from brain import Brain


# ============================================================
# CONFIGURATION
# ============================================================

APP_NAME = "D-AI"

WINDOW_WIDTH = 900
WINDOW_HEIGHT = 650

THINKER_WIDTH = 700
THINKER_HEIGHT = 600

FONT_NAME = "Segoe UI"

CHAT_FONT_SIZE = 11
INPUT_FONT_SIZE = 11
THINKER_FONT_SIZE = 10

MAX_CHAT_LINES = 5000
MAX_THINKER_LINES = 10000


# ============================================================
# UTILITIES
# ============================================================

def safe_text(value):
    """
    Converts any value into safe text.
    """

    if value is None:
        return ""

    try:
        return str(value)
    except Exception:
        return ""


def current_time():
    """
    Returns the current time.
    """

    return time.strftime(
        "%H:%M:%S"
    )


def current_date():
    """
    Returns the current date.
    """

    return time.strftime(
        "%Y-%m-%d"
    )


# ============================================================
# MAIN CLASS
# ============================================================

class DIAWindow:

    # ========================================================
    # CONSTRUCTOR
    # ========================================================

    def __init__(
        self,
        thinker=False
    ):
        """
        Initializes the main D-AI window.
        """

        self.thinker_enabled = bool(
            thinker
        )

        self.brain = Brain()

        self.root = tk.Tk()

        self.root.title(
            APP_NAME
        )

        self.root.geometry(
            f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}"
        )

        self.root.minsize(
            650,
            450
        )

        self.root.protocol(
            "WM_DELETE_WINDOW",
            self.close_application
        )

        # ----------------------------------------------------
        # VARIABLES
        # ----------------------------------------------------

        self.running = True

        self.message_count = 0

        self.user_message_count = 0

        self.ai_message_count = 0

        self.thinker_window = None

        self.thinker_log = None

        self.status_label = None

        self.entry = None

        self.chat = None

        self.send_button = None

        self.clear_button = None

        self.menu = None

        self.typing = False

        self.last_message = ""

        self.last_response = ""

        # ----------------------------------------------------
        # BUILD INTERFACE
        # ----------------------------------------------------

        self.create_menu()

        self.create_main_interface()

        if self.thinker_enabled:

            self.create_thinker()

        # ----------------------------------------------------
        # INITIAL MESSAGE
        # ----------------------------------------------------

        self.write_message(
            "D-AI",
            "Hello! I'm D-AI."
        )

        self.write_system_message(
            "Brain loaded successfully."
        )

        if self.thinker_enabled:

            self.thinker_write(
                "THINKER started."
            )

            self.thinker_write(
                f"Date: {current_date()}"
            )

            self.thinker_write(
                f"Time: {current_time()}"
            )

        self.entry.focus_set()


    # ========================================================
    # CREATE MENU
    # ========================================================

    def create_menu(
        self
    ):
        """
        Creates the menu bar.
        """

        self.menu = tk.Menu(
            self.root
        )

        # ----------------------------------------------------
        # FILE MENU
        # ----------------------------------------------------

        file_menu = tk.Menu(
            self.menu,
            tearoff=0
        )

        file_menu.add_command(
            label="Save brain",
            command=self.save_brain
        )

        file_menu.add_command(
            label="Export conversation",
            command=self.export_chat
        )

        file_menu.add_separator()

        file_menu.add_command(
            label="Exit",
            command=self.close_application
        )

        self.menu.add_cascade(
            label="File",
            menu=file_menu
        )

        # ----------------------------------------------------
        # BRAIN MENU
        # ----------------------------------------------------

        brain_menu = tk.Menu(
            self.menu,
            tearoff=0
        )

        brain_menu.add_command(
            label="Statistics",
            command=self.show_statistics
        )

        brain_menu.add_command(
            label="Status",
            command=self.show_brain_status
        )

        brain_menu.add_command(
            label="Vocabulary",
            command=self.show_vocabulary
        )

        brain_menu.add_separator()

        brain_menu.add_command(
            label="Enable learning",
            command=self.enable_learning
        )

        brain_menu.add_command(
            label="Disable learning",
            command=self.disable_learning
        )

        self.menu.add_cascade(
            label="Brain",
            menu=brain_menu
        )

        # ----------------------------------------------------
        # CONVERSATION MENU
        # ----------------------------------------------------

        conversation_menu = tk.Menu(
            self.menu,
            tearoff=0
        )

        conversation_menu.add_command(
            label="Clear chat",
            command=self.clear_chat
        )

        conversation_menu.add_command(
            label="Clear context",
            command=self.clear_context
        )

        self.menu.add_cascade(
            label="Conversation",
            menu=conversation_menu
        )

        # ----------------------------------------------------
        # THINKER MENU
        # ----------------------------------------------------

        thinker_menu = tk.Menu(
            self.menu,
            tearoff=0
        )

        thinker_menu.add_command(
            label="Open Thinker",
            command=self.open_thinker
        )

        thinker_menu.add_command(
            label="Clear Thinker",
            command=self.clear_thinker
        )

        self.menu.add_cascade(
            label="Thinker",
            menu=thinker_menu
        )

        self.root.config(
            menu=self.menu
        )


    # ========================================================
    # MAIN INTERFACE
    # ========================================================

    def create_main_interface(
        self
    ):
        """
        Builds all elements of the main window.
        """

        # ----------------------------------------------------
        # MAIN CONTAINER
        # ----------------------------------------------------

        main_frame = tk.Frame(
            self.root
        )

        main_frame.pack(
            fill=tk.BOTH,
            expand=True
        )

        # ----------------------------------------------------
        # HEADER
        # ----------------------------------------------------

        header = tk.Frame(
            main_frame
        )

        header.pack(
            fill=tk.X,
            padx=10,
            pady=(10, 5)
        )

        title = tk.Label(
            header,
            text="D-AI",
            font=(
                FONT_NAME,
                18,
                "bold"
            )
        )

        title.pack(
            side=tk.LEFT
        )

        self.status_label = tk.Label(
            header,
            text="● READY",
            font=(
                FONT_NAME,
                9
            )
        )

        self.status_label.pack(
            side=tk.RIGHT
        )

        # ----------------------------------------------------
        # CHAT
        # ----------------------------------------------------

        chat_frame = tk.Frame(
            main_frame
        )

        chat_frame.pack(
            fill=tk.BOTH,
            expand=True,
            padx=10,
            pady=5
        )

        self.chat = scrolledtext.ScrolledText(
            chat_frame,
            wrap=tk.WORD,
            font=(
                FONT_NAME,
                CHAT_FONT_SIZE
            ),
            state=tk.DISABLED
        )

        self.chat.pack(
            fill=tk.BOTH,
            expand=True
        )

        # ----------------------------------------------------
        # INPUT AREA
        # ----------------------------------------------------

        input_frame = tk.Frame(
            main_frame
        )

        input_frame.pack(
            fill=tk.X,
            padx=10,
            pady=(5, 10)
        )

        self.entry = tk.Entry(
            input_frame,
            font=(
                FONT_NAME,
                INPUT_FONT_SIZE
            )
        )

        self.entry.pack(
            side=tk.LEFT,
            fill=tk.X,
            expand=True,
            padx=(0, 5)
        )

        self.entry.bind(
            "<Return>",
            self.send_message
        )

        self.send_button = tk.Button(
            input_frame,
            text="Send",
            command=self.send_message
        )

        self.send_button.pack(
            side=tk.LEFT
        )

        self.clear_button = tk.Button(
            input_frame,
            text="Clear",
            command=self.clear_chat
        )

        self.clear_button.pack(
            side=tk.LEFT,
            padx=(5, 0)
        )


    # ========================================================
    # WRITE TO CHAT
    # ========================================================

    def write_message(
        self,
        sender,
        message
    ):
        """
        Writes a message to the chat.
        """

        if self.chat is None:
            return

        sender = safe_text(
            sender
        )

        message = safe_text(
            message
        )

        timestamp = current_time()

        formatted = (
            f"[{timestamp}] "
            f"{sender}: "
            f"{message}\n\n"
        )

        self.chat.config(
            state=tk.NORMAL
        )

        self.chat.insert(
            tk.END,
            formatted
        )

        self.chat.config(
            state=tk.DISABLED
        )

        self.chat.see(
            tk.END
        )

        self.message_count += 1

        if sender == "You":

            self.user_message_count += 1

        elif sender == "D-AI":

            self.ai_message_count += 1

        self.trim_chat()


    # ========================================================
    # SYSTEM MESSAGE
    # ========================================================

    def write_system_message(
        self,
        message
    ):
        """
        Writes internal application information.
        """

        if self.chat is None:
            return

        formatted = (
            f"[{current_time()}] "
            f"[SYSTEM] "
            f"{safe_text(message)}\n\n"
        )

        self.chat.config(
            state=tk.NORMAL
        )

        self.chat.insert(
            tk.END,
            formatted
        )

        self.chat.config(
            state=tk.DISABLED
        )

        self.chat.see(
            tk.END
        )

        self.trim_chat()


    # ========================================================
    # LIMIT CHAT
    # ========================================================

    def trim_chat(
        self
    ):
        """
        Prevents the widget from growing indefinitely.
        """

        if self.chat is None:
            return

        try:

            line_count = int(
                self.chat.index(
                    "end-1c"
                ).split(
                    "."
                )[0]
            )

        except Exception:

            return

        if line_count <= MAX_CHAT_LINES:
            return

        self.chat.config(
            state=tk.NORMAL
        )

        delete_lines = (
            line_count
            - MAX_CHAT_LINES
        )

        self.chat.delete(
            "1.0",
            f"{delete_lines + 1}.0"
        )

        self.chat.config(
            state=tk.DISABLED
        )


    # ========================================================
    # SEND MESSAGE
    # ========================================================

    def send_message(
        self,
        event=None
    ):
        """
        Processes the message entered by the user.
        """

        if self.typing:

            return "break"

        if self.entry is None:

            return "break"

        message = self.entry.get().strip()

        if not message:

            return "break"

        self.entry.delete(
            0,
            tk.END
        )

        self.last_message = message

        self.write_message(
            "You",
            message
        )

        if self.thinker_enabled:

            self.thinker_write(
                "================================================"
            )

            self.thinker_write(
                f"INPUT: {message}"
            )

        self.set_typing(
            True
        )

        thread = threading.Thread(
            target=self.process_message,
            args=(message,),
            daemon=True
        )

        thread.start()

        return "break"


    # ========================================================
    # PROCESS MESSAGE
    # ========================================================

    def process_message(
        self,
        message
    ):
        """
        Executes the brain outside the GUI thread.
        """

        try:

            if self.thinker_enabled:

                try:

                    diagnosis = (
                        self.brain.debug_response(
                            message
                        )
                    )

                    self.update_thinker_diagnosis(
                        diagnosis
                    )

                except Exception as error:

                    self.thinker_write(
                        f"Diagnostic error: {error}"
                    )

            response = self.brain.respond(
                message
            )

            self.last_response = response

            self.root.after(
                0,
                self.finish_response,
                response
            )

        except Exception as error:

            error_text = (
                f"Brain error: {error}"
            )

            self.root.after(
                0,
                self.finish_response,
                error_text
            )


    # ========================================================
    # FINISH RESPONSE
    # ========================================================

    def finish_response(
        self,
        response
    ):
        """
        Returns the result to the Tkinter thread.
        """

        self.set_typing(
            False
        )

        self.write_message(
            "D-AI",
            response
        )

        if self.thinker_enabled:

            self.thinker_write(
                f"RESPONSE: {response}"
            )

            self.thinker_write(
                "================================================"
            )

        self.entry.focus_set()


    # ========================================================
    # TYPING STATE
    # ========================================================

    def set_typing(
        self,
        value
    ):
        """
        Changes the processing state.
        """

        self.typing = bool(
            value
        )

        if self.typing:

            if self.status_label:

                self.status_label.config(
                    text="● THINKING..."
                )

            if self.send_button:

                self.send_button.config(
                    state=tk.DISABLED
                )

        else:

            if self.status_label:

                self.status_label.config(
                    text="● READY"
                )

            if self.send_button:

                self.send_button.config(
                    state=tk.NORMAL
                )


    # ========================================================
    # SAVE BRAIN
    # ========================================================

    def save_brain(
        self
    ):
        """
        Saves brain.json.
        """

        try:

            success = self.brain.save()

        except Exception:

            success = False

        if success:

            self.write_system_message(
                "Brain saved."
            )

        else:

            self.write_system_message(
                "Could not save the brain."
            )


    # ========================================================
    # STATISTICS
    # ========================================================

    def show_statistics(
        self
    ):
        """
        Displays brain statistics.
        """

        try:

            stats = (
                self.brain.get_statistics()
            )

        except Exception as error:

            messagebox.showerror(
                "D-AI",
                f"Could not get statistics:\n{error}"
            )

            return

        text = (
            "D-AI STATISTICS\n\n"
            f"Vocabulary: "
            f"{stats.get('vocabulary', 0)}\n"
            f"Words: "
            f"{stats.get('words', 0)}\n"
            f"Messages: "
            f"{stats.get('messages', 0)}\n"
            f"User messages: "
            f"{stats.get('user_messages', 0)}\n"
            f"D-AI messages: "
            f"{stats.get('ai_messages', 0)}\n"
            f"Learning events: "
            f"{stats.get('learning_events', 0)}\n"
            f"Current turn: "
            f"{stats.get('conversation_turn', 0)}"
        )

        messagebox.showinfo(
            "Statistics",
            text
        )


    # ========================================================
    # BRAIN STATUS
    # ========================================================

    def show_brain_status(
        self
    ):
        """
        Displays the internal state of D-AI.
        """

        try:

            info = self.brain.brain_info()

        except Exception as error:

            messagebox.showerror(
                "D-AI",
                f"Error:\n{error}"
            )

            return

        text = (
            f"Name: {info.get('name')}\n"
            f"Type: {info.get('type')}\n"
            f"Version: {info.get('version')}\n"
            f"Vocabulary: {info.get('vocabulary')}\n"
            f"Words: {info.get('words')}\n"
            f"Messages: {info.get('messages')}\n"
            f"Learning: "
            f"{info.get('learning_enabled')}\n"
            f"Memory: "
            f"{info.get('memory_available')}"
        )

        messagebox.showinfo(
            "D-AI Status",
            text
        )


    # ========================================================
    # VOCABULARY
    # ========================================================

    def show_vocabulary(
        self
    ):
        """
        Displays the most frequent words.
        """

        try:

            words = (
                self.brain.get_most_common_words(
                    limit=50
                )
            )

        except Exception as error:

            messagebox.showerror(
                "D-AI",
                f"Error:\n{error}"
            )

            return

        if not words:

            messagebox.showinfo(
                "Vocabulary",
                "There are no words yet."
            )

            return

        text = (
            "MOST FREQUENT WORDS\n\n"
        )

        for index, item in enumerate(
            words,
            start=1
        ):

            word = item.get(
                "word",
                ""
            )

            count = item.get(
                "count",
                0
            )

            text += (
                f"{index}. "
                f"{word} "
                f"({count})\n"
            )

        self.show_text_window(
            "Vocabulary",
            text
        )


    # ========================================================
    # ENABLE LEARNING
    # ========================================================

    def enable_learning(
        self
    ):
        """
        Enables learning.
        """

        try:

            self.brain.enable_learning()

            self.write_system_message(
                "Learning enabled."
            )

        except Exception as error:

            self.write_system_message(
                f"Error enabling learning: {error}"
            )


    # ========================================================
    # DISABLE LEARNING
    # ========================================================

    def disable_learning(
        self
    ):
        """
        Disables learning.
        """

        try:

            self.brain.disable_learning()

            self.write_system_message(
                "Learning disabled."
            )

        except Exception as error:

            self.write_system_message(
                f"Error disabling learning: {error}"
            )


    # ========================================================
    # CLEAR CHAT
    # ========================================================

    def clear_chat(
        self
    ):
        """
        Visually clears the conversation.
        """

        if self.chat is None:
            return

        self.chat.config(
            state=tk.NORMAL
        )

        self.chat.delete(
            "1.0",
            tk.END
        )

        self.chat.config(
            state=tk.DISABLED
        )

        self.write_system_message(
            "Chat cleared."
        )


    # ========================================================
    # CLEAR CONTEXT
    # ========================================================

    def clear_context(
        self
    ):
        """
        Clears the temporary brain context.
        """

        try:

            self.brain.clear_runtime_context()

            self.write_system_message(
                "Conversation context cleared."
            )

            if self.thinker_enabled:

                self.thinker_write(
                    "Context cleared."
                )

        except Exception as error:

            self.write_system_message(
                f"Error clearing context: {error}"
            )


    # ========================================================
    # TEXT WINDOW
    # ========================================================

    def show_text_window(
        self,
        title,
        content
    ):
        """
        Opens a secondary text window.
        """

        window = tk.Toplevel(
            self.root
        )

        window.title(
            title
        )

        window.geometry(
            "650x500"
        )

        text = scrolledtext.ScrolledText(
            window,
            wrap=tk.WORD,
            font=(
                FONT_NAME,
                10
            )
        )

        text.pack(
            fill=tk.BOTH,
            expand=True,
            padx=10,
            pady=10
        )

        text.insert(
            tk.END,
            safe_text(content)
        )

        text.config(
            state=tk.DISABLED
        )


    # ========================================================
    # THINKER
    # ========================================================

    def create_thinker(
        self
    ):
        """
        Creates the Thinker window.
        """

        if self.thinker_window is not None:

            try:

                if self.thinker_window.winfo_exists():

                    return

            except Exception:
                pass

        self.thinker_window = tk.Toplevel(
            self.root
        )

        self.thinker_window.title(
            "D-AI Thinker"
        )

        self.thinker_window.geometry(
            f"{THINKER_WIDTH}x{THINKER_HEIGHT}"
        )

        self.thinker_window.protocol(
            "WM_DELETE_WINDOW",
            self.close_thinker
        )

        # ----------------------------------------------------
        # THINKER HEADER
        # ----------------------------------------------------

        header = tk.Frame(
            self.thinker_window
        )

        header.pack(
            fill=tk.X,
            padx=10,
            pady=10
        )

        title = tk.Label(
            header,
            text="D-AI THINKER",
            font=(
                FONT_NAME,
                15,
                "bold"
            )
        )

        title.pack(
            side=tk.LEFT
        )

        status = tk.Label(
            header,
            text="ACTIVE",
            font=(
                FONT_NAME,
                9
            )
        )

        status.pack(
            side=tk.RIGHT
        )

        # ----------------------------------------------------
        # LOG
        # ----------------------------------------------------

        self.thinker_log = scrolledtext.ScrolledText(
            self.thinker_window,
            wrap=tk.WORD,
            font=(
                "Consolas",
                THINKER_FONT_SIZE
            ),
            state=tk.DISABLED
        )

        self.thinker_log.pack(
            fill=tk.BOTH,
            expand=True,
            padx=10,
            pady=(0, 10)
        )

        self.thinker_write(
            "THINKER ready."
        )


    # ========================================================
    # OPEN THINKER
    # ========================================================

    def open_thinker(
        self
    ):
        """
        Opens Thinker even if D-AI was started
        without --thinker.
        """

        self.thinker_enabled = True

        self.create_thinker()

        if self.thinker_window:

            try:

                self.thinker_window.deiconify()

                self.thinker_window.lift()

            except Exception:
                pass


    # ========================================================
    # CLOSE THINKER
    # ========================================================

    def close_thinker(
        self
    ):
        """
        Closes only the Thinker window.
        """

        if self.thinker_window is None:
            return

        try:

            self.thinker_window.destroy()

        except Exception:
            pass

        self.thinker_window = None

        self.thinker_log = None

        self.thinker_enabled = False


    # ========================================================
    # WRITE THINKER
    # ========================================================

    def thinker_write(
        self,
        text
    ):
        """
        Writes a line to Thinker.
        """

        if not self.thinker_enabled:
            return

        if self.thinker_log is None:
            return

        try:

            if not self.thinker_log.winfo_exists():

                return

        except Exception:

            return

        formatted = (
            f"[{current_time()}] "
            f"{safe_text(text)}\n"
        )

        def write():

            try:

                self.thinker_log.config(
                    state=tk.NORMAL
                )

                self.thinker_log.insert(
                    tk.END,
                    formatted
                )

                self.thinker_log.config(
                    state=tk.DISABLED
                )

                self.thinker_log.see(
                    tk.END
                )

                self.trim_thinker()

            except Exception:
                pass

        try:

            self.root.after(
                0,
                write
            )

        except Exception:
            pass


    # ========================================================
    # LIMIT THINKER
    # ========================================================

    def trim_thinker(
        self
    ):
        """
        Limits the size of the Thinker log.
        """

        if self.thinker_log is None:
            return

        try:

            line_count = int(
                self.thinker_log.index(
                    "end-1c"
                ).split(
                    "."
                )[0]
            )

        except Exception:

            return

        if line_count <= MAX_THINKER_LINES:

            return

        delete_lines = (
            line_count
            - MAX_THINKER_LINES
        )

        self.thinker_log.config(
            state=tk.NORMAL
        )

        self.thinker_log.delete(
            "1.0",
            f"{delete_lines + 1}.0"
        )

        self.thinker_log.config(
            state=tk.DISABLED
        )


    # ========================================================
    # CLEAR THINKER
    # ========================================================

    def clear_thinker(
        self
    ):
        """
        Clears the Thinker log.
        """

        if self.thinker_log is None:
            return

        try:

            self.thinker_log.config(
                state=tk.NORMAL
            )

            self.thinker_log.delete(
                "1.0",
                tk.END
            )

            self.thinker_log.config(
                state=tk.DISABLED
            )

            self.thinker_write(
                "Log cleared."
            )

        except Exception:
            pass


    # ========================================================
    # THINKER DIAGNOSTICS
    # ========================================================

    def update_thinker_diagnosis(
        self,
        diagnosis
    ):
        """
        Displays D-AI's internal analysis.
        """

        if not self.thinker_enabled:

            return

        if not isinstance(
            diagnosis,
            dict
        ):

            return

        self.thinker_write(
            "ANALYSIS"
        )

        self.thinker_write(
            f"Intent: "
            f"{diagnosis.get('intent', 'unknown')}"
        )

        self.thinker_write(
            f"Main concept: "
            f"{diagnosis.get('main_concept')}"
        )

        self.thinker_write(
            f"Confidence: "
            f"{diagnosis.get('confidence', 0.0)}"
        )

        tokens = diagnosis.get(
            "tokens",
            []
        )

        self.thinker_write(
            f"Tokens: {tokens}"
        )

        known = diagnosis.get(
            "known_words",
            []
        )

        self.thinker_write(
            f"Known words: "
            f"{len(known)}"
        )

        similar = diagnosis.get(
            "similar_messages",
            []
        )

        self.thinker_write(
            f"Similar messages: "
            f"{len(similar)}"
        )


    # ========================================================
    # EXPORT CHAT
    # ========================================================

    def export_chat(
        self
    ):
        """
        Saves the visible chat content.
        """

        if self.chat is None:

            return

        try:

            content = self.chat.get(
                "1.0",
                tk.END
            )

        except Exception as error:

            messagebox.showerror(
                "D-AI",
                f"Could not read the chat:\n{error}"
            )

            return

        filename = filedialog.asksaveasfilename(
            title="Export conversation",
            defaultextension=".txt",
            filetypes=[
                (
                    "Text file",
                    "*.txt"
                ),
                (
                    "All files",
                    "*.*"
                ),
            ]
        )

        if not filename:

            return

        try:

            with open(
                filename,
                "w",
                encoding="utf-8"
            ) as file:

                file.write(
                    content
                )

            self.write_system_message(
                f"Conversation exported: {filename}"
            )

        except OSError as error:

            messagebox.showerror(
                "D-AI",
                f"Could not save the file:\n{error}"
            )


    # ========================================================
    # CLOSE APPLICATION
    # ========================================================

    def close_application(
        self
    ):
        """
        Properly closes D-AI.
        """

        if not self.running:
            return

        self.running = False

        try:

            self.brain.save()

        except Exception:
            pass

        try:

            if self.thinker_window:

                self.thinker_window.destroy()

        except Exception:
            pass

        try:

            self.root.destroy()

        except Exception:
            pass


# ============================================================
# STARTUP FUNCTION
# ============================================================

def start_gui(
    thinker=False
):
    """
    Starts the D-AI interface.

    thinker=False:
        GUI only.

    thinker=True:
        GUI + Thinker.
    """

    app = DIAWindow(
        thinker=thinker
    )

    app.root.mainloop()


# ============================================================
# DIRECT EXECUTION
# ============================================================

if __name__ == "__main__":

    import sys

    thinker = (
        "--thinker"
        in sys.argv
    )

    start_gui(
        thinker=thinker
    )


# ============================================================
# D-AI
# gui.py
# BLOCK 2/2 - ADVANCED INTERFACE FUNCTIONS
# ============================================================

    # ========================================================
    # CREATE INFORMATION PANEL
    # ========================================================

    def create_info_window(
        self
    ):
        """
        Opens a window with general D-AI information.
        """

        window = tk.Toplevel(
            self.root
        )

        window.title(
            "D-AI Information"
        )

        window.geometry(
            "500x400"
        )

        try:

            info = self.brain.brain_info()

        except Exception as error:

            info = {
                "name": "D-AI",
                "type": "Error",
                "version": "?",
                "vocabulary": 0,
                "words": 0,
                "messages": 0,
                "learning_enabled": False,
                "memory_available": False,
                "error": str(error),
            }

        text = scrolledtext.ScrolledText(
            window,
            wrap=tk.WORD,
            font=(
                FONT_NAME,
                10
            ),
            state=tk.NORMAL
        )

        text.pack(
            fill=tk.BOTH,
            expand=True,
            padx=10,
            pady=10
        )

        content = (
            "D-AI\n"
            "==============================\n\n"
            f"Name: {info.get('name')}\n"
            f"Type: {info.get('type')}\n"
            f"Version: {info.get('version')}\n\n"
            f"Vocabulary: "
            f"{info.get('vocabulary')}\n"
            f"Learned words: "
            f"{info.get('words')}\n"
            f"Messages: "
            f"{info.get('messages')}\n\n"
            f"Learning active: "
            f"{info.get('learning_enabled')}\n"
            f"Memory available: "
            f"{info.get('memory_available')}\n"
        )

        if "error" in info:

            content += (
                f"\nError:\n"
                f"{info['error']}\n"
            )

        text.insert(
            tk.END,
            content
        )

        text.config(
            state=tk.DISABLED
        )


    # ========================================================
    # MEMORY WINDOW
    # ========================================================

    def show_memory(
        self
    ):
        """
        Displays memories known by D-AI.
        """

        memory = None

        try:

            memory = (
                self.brain._get_external_memory()
            )

        except Exception:
            memory = None

        if memory is None:

            messagebox.showwarning(
                "Memory",
                "Could not load memory.py."
            )

            return

        try:

            facts = memory.data.get(
                "facts",
                {}
            )

        except Exception:

            facts = {}

        if not facts:

            messagebox.showinfo(
                "Memory",
                "D-AI does not have any memories yet."
            )

            return

        text = (
            "D-AI MEMORY\n"
            "==============================\n\n"
        )

        for key, value in facts.items():

            text += (
                f"{key}: {value}\n"
            )

        self.show_text_window(
            "D-AI Memory",
            text
        )


    # ========================================================
    # MESSAGE EDITOR
    # ========================================================

    def set_input(
        self,
        text
    ):
        """
        Places text directly into the input field.
        """

        if self.entry is None:

            return

        self.entry.delete(
            0,
            tk.END
        )

        self.entry.insert(
            0,
            safe_text(text)
        )

        self.entry.focus_set()


    # ========================================================
    # RESEND LAST MESSAGE
    # ========================================================

    def resend_last(
        self
    ):
        """
        Places the last message back into the input field.
        """

        if not self.last_message:

            return

        self.set_input(
            self.last_message
        )


    # ========================================================
    # SHOW LAST RESPONSE
    # ========================================================

    def show_last_response(
        self
    ):
        """
        Displays the last generated response.
        """

        if not self.last_response:

            messagebox.showinfo(
                "D-AI",
                "There is no response yet."
            )

            return

        messagebox.showinfo(
            "Last response",
            self.last_response
        )


    # ========================================================
    # COPY LAST RESPONSE
    # ========================================================

    def copy_last_response(
        self
    ):
        """
        Copies the last response to the clipboard.
        """

        if not self.last_response:

            return

        try:

            self.root.clipboard_clear()

            self.root.clipboard_append(
                self.last_response
            )

            self.write_system_message(
                "Last response copied."
            )

        except Exception as error:

            self.write_system_message(
                f"Could not copy: {error}"
            )


    # ========================================================
    # COPY CHAT
    # ========================================================

    def copy_chat(
        self
    ):
        """
        Copies the entire visible conversation.
        """

        if self.chat is None:

            return

        try:

            content = self.chat.get(
                "1.0",
                tk.END
            )

            self.root.clipboard_clear()

            self.root.clipboard_append(
                content
            )

            self.write_system_message(
                "Chat copied to clipboard."
            )

        except Exception as error:

            self.write_system_message(
                f"Could not copy the chat: {error}"
            )


    # ========================================================
    # BRAIN TEST
    # ========================================================

    def run_brain_test(
        self
    ):
        """
        Runs a small automatic test.
        """

        tests = [
            "hello",
            "what is your name",
            "how are you",
            "thanks",
            "goodbye",
        ]

        results = []

        for message in tests:

            try:

                response = (
                    self.brain.think_message(
                        message
                    )
                )

                results.append(
                    f"> {message}\n"
                    f"  {response}\n"
                )

            except Exception as error:

                results.append(
                    f"> {message}\n"
                    f"  ERROR: {error}\n"
                )

        self.show_text_window(
            "Brain test",
            "\n".join(
                results
            )
        )


    # ========================================================
    # MANUAL DIAGNOSTIC
    # ========================================================

    def diagnose_current_input(
        self
    ):
        """
        Analyzes the text currently written.
        """

        if self.entry is None:

            return

        message = self.entry.get().strip()

        if not message:

            messagebox.showinfo(
                "Diagnostics",
                "Write something first."
            )

            return

        try:

            diagnosis = (
                self.brain.debug_response(
                    message
                )
            )

        except Exception as error:

            messagebox.showerror(
                "Diagnostics",
                f"Error:\n{error}"
            )

            return

        text = (
            "DIAGNOSTICS\n"
            "==============================\n\n"
            f"Input:\n"
            f"{diagnosis.get('input')}\n\n"
            f"Normalized:\n"
            f"{diagnosis.get('normalized')}\n\n"
            f"Tokens:\n"
            f"{diagnosis.get('tokens')}\n\n"
            f"Intent:\n"
            f"{diagnosis.get('intent')}\n\n"
            f"Concept:\n"
            f"{diagnosis.get('main_concept')}\n\n"
            f"Confidence:\n"
            f"{diagnosis.get('confidence')}\n"
        )

        self.show_text_window(
            "Diagnostics",
            text
        )


    # ========================================================
    # REPAIR BRAIN
    # ========================================================

    def repair_brain(
        self
    ):
        """
        Repairs the internal brain state.
        """

        try:

            result = (
                self.brain.repair_state()
            )

        except Exception as error:

            messagebox.showerror(
                "D-AI",
                f"Repair error:\n{error}"
            )

            return

        if result.get(
            "valid",
            False
        ):

            self.write_system_message(
                "Brain repaired successfully."
            )

            messagebox.showinfo(
                "D-AI",
                "The brain is correctly structured."
            )

        else:

            problems = result.get(
                "problems",
                []
            )

            messagebox.showwarning(
                "D-AI",
                "Problems found:\n"
                + "\n".join(
                    problems
                )
            )


    # ========================================================
    # VALIDATE BRAIN
    # ========================================================

    def validate_brain(
        self
    ):
        """
       Checks the state of the brain.
        """

        try:

            result = (
                self.brain.validate_state()
            )

        except Exception as error:

            messagebox.showerror(
                "D-AI",
                f"Error:\n{error}"
            )

            return

        if result.get(
            "valid",
            False
        ):

            messagebox.showinfo(
                "Validation",
                "✓ The brain is valid."
            )

        else:

            problems = result.get(
                "problems",
                []
            )

            messagebox.showwarning(
                "Validation",
                "Problems:\n"
                + "\n".join(
                    problems
                )
            )


    # ========================================================
    # CLEAR STATISTICAL MEMORY
    # ========================================================

    def reset_brain(
        self
    ):
        """
        Resets the statistical brain.
        """

        answer = messagebox.askyesno(
            "Reset brain",
            "Are you sure you want to reset "
            "the statistical brain?\n\n"
            "This should not delete memory.json."
        )

        if not answer:

            return

        try:

            self.brain.reset_brain()

            self.write_system_message(
                "Statistical brain reset."
            )

        except Exception as error:

            messagebox.showerror(
                "D-AI",
                f"Could not reset:\n{error}"
            )


    # ========================================================
    # CHANGE TITLE
    # ========================================================

    def update_title(
        self,
        extra=""
    ):
        """
        Updates the application title.
        """

        extra = safe_text(
            extra
        )

        if extra:

            self.root.title(
                f"{APP_NAME} - {extra}"
            )

        else:

            self.root.title(
                APP_NAME
            )


    # ========================================================
    # UPDATE STATUS
    # ========================================================

    def update_status(
        self,
        text
    ):
        """
        Changes the status text.
        """

        if self.status_label is None:

            return

        try:

            self.status_label.config(
                text=safe_text(text)
            )

        except Exception:
            pass


    # ========================================================
    # THINKER MODE
    # ========================================================

    def thinker_enabled_status(
        self
    ):
        """
        Returns whether Thinker is active.
        """

        return (
            self.thinker_enabled
            and
            self.thinker_window is not None
        )


    # ========================================================
    # SHOW CONTEXT
    # ========================================================

    def show_context(
        self
    ):
        """
        Displays the current context.
        """

        try:

            context = (
                self.brain.get_context()
            )

        except Exception as error:

            messagebox.showerror(
                "Context",
                f"Error:\n{error}"
            )

            return

        text = (
            "CURRENT CONTEXT\n"
            "==============================\n\n"
            f"Last user message:\n"
            f"{context.get('last_user_message', '')}\n\n"
            f"Last D-AI response:\n"
            f"{context.get('last_ai_message', '')}\n\n"
            f"Turn:\n"
            f"{context.get('conversation_turn', 0)}"
        )

        self.show_text_window(
            "Context",
            text
        )


    # ========================================================
    # SHOW SUMMARY
    # ========================================================

    def show_brain_summary(
        self
    ):
        """
        Displays a complete summary.
        """

        try:

            summary = (
                self.brain.export_summary()
            )

        except Exception as error:

            messagebox.showerror(
                "Summary",
                f"Error:\n{error}"
            )

            return

        text = json.dumps(
            summary,
            ensure_ascii=False,
            indent=4,
            default=str
        )

        self.show_text_window(
            "Brain summary",
            text
        )


    # ========================================================
    # KEYBOARD SHORTCUTS
    # ========================================================

    def bind_shortcuts(
        self
    ):
        """
        Registers useful shortcuts.
        """

        self.root.bind(
            "<Control-s>",
            lambda event: self.save_brain()
        )

        self.root.bind(
            "<Control-l>",
            lambda event: self.clear_chat()
        )

        self.root.bind(
            "<Control-t>",
            lambda event: self.open_thinker()
        )

        self.root.bind(
            "<Control-d>",
            lambda event:
                self.diagnose_current_input()
        )

        self.root.bind(
            "<Control-m>",
            lambda event:
                self.show_memory()
        )


    # ========================================================
    # FINAL CONFIGURATION
    # ========================================================

    def finalize_interface(
        self
    ):
        """
        Applies final configurations.
        """

        self.bind_shortcuts()

        try:

            self.entry.focus_set()

        except Exception:
            pass


# ============================================================
# IMPROVED STARTUP FUNCTION
# ============================================================

def start_gui(
    thinker=False
):
    """
    Starts the application.
    """

    app = DIAWindow(
        thinker=thinker
    )

    try:

        app.finalize_interface()

    except Exception:

        pass

    app.root.mainloop()


# ============================================================
# EXECUTION
# ============================================================

if __name__ == "__main__":

    import sys

    thinker = (
        "--thinker"
        in sys.argv
    )

    start_gui(
        thinker=thinker
    )


# ============================================================
# END OF GUI.PY
# ============================================================

#====================
# END OF BLOCKS
#====================