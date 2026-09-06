import sys
from gui import start_gui


def main():
    thinker = "--thinker" in sys.argv

    start_gui(thinker)


if __name__ == "__main__":
    main()