from interface import GUInterface
from processor import DataAnalyzer


def main():
    processor = DataAnalyzer()
    app = GUInterface(processor)
    app.run()


if __name__ == "__main__":
    main()