import streamlit as st
from games import DigitspanGame, NumerosityGame, ShapedanceGame

def main():
    st.set_page_config(page_title="Cognitive Game Practice", layout="centered")
    st.title("🧠 Cognitive Game Practice App")

    st.sidebar.title("Select a Game")
    game_choice = st.sidebar.selectbox(
        "Choose the game you want to play:",
        ["Digitspan", "Numerosity", "Shapedance"]
    )

    game_mapping = {
        "Digitspan": DigitspanGame,
        "Numerosity": NumerosityGame,
        "Shapedance": ShapedanceGame
    }

    selected_game_class = game_mapping.get(game_choice)
    if selected_game_class:
        game = selected_game_class()
        game.play()
    else:
        st.error("Invalid game selection.")

if __name__ == "__main__":
    main()
