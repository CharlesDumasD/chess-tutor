"""Hugging Face Spaces entry point."""

from chess_tutor.app import build_demo

demo = build_demo()


if __name__ == "__main__":
    demo.launch()
