import random
import time
import streamlit as st

class DigitspanGame:
    def __init__(self):
        if "digitspan" not in st.session_state:
            st.session_state.digitspan = {
                "start_time": time.time(),
                "total_time": 180,  # total time in seconds (adjust as needed)
                "level": 1,
                "score": 0,
                "stage": "init",  # can be "init", "show", or "input"
                "current_sequence": "",
                "result_message": "",
            }
            st.session_state["input_answer"] = ""

    def shuffle_string(self, s: str) -> str:
        chars = list(s)
        random.shuffle(chars)
        return ''.join(chars)

    def compute_difficulty(self):
        """
        Increases digit count every 3 levels.
        Level 1–3: 2 digits, 4–6: 3 digits, etc.
        Display time: 3.0, 2.0, 1.5 seconds respectively.
        """
        level = st.session_state.digitspan["level"]
        digit_count = 2 + ((level - 1) // 3)
        group_index = (level - 1) % 3
        display_times = [3.0, 2.0, 1.5]
        display_time = display_times[group_index]
        return digit_count, display_time

    def start_level(self):
        """Generates a random sequence and sets the stage to display it."""
        digit_count, display_time = self.compute_difficulty()
        sequence = ''.join(random.choices(self.shuffle_string("0123456789ABCDEFGHIJKLMNOPRSTUVYZ"), k=digit_count))
        st.session_state.digitspan.update({
            "current_sequence": sequence,
            "stage": "show",
            "result_message": "",
            "digit_count": digit_count,
            "display_time": display_time
        })
        st.session_state["input_answer"] = ""

    def check_answer(self):
        """Compares the user input with the generated sequence."""
        state = st.session_state.digitspan
        user_input = str(st.session_state.get("input_answer", "").strip())
        correct_sequence = str(state["current_sequence"])
        if user_input == correct_sequence:
            state["result_message"] = "Correct! Moving to the next level."
            state["score"] += 1
            state["level"] += 1
        else:
            state["result_message"] = (
                f"Incorrect! Your answer: {user_input}. Correct answer: {correct_sequence}. Try again."
            )
        state["stage"] = "init"
        st.session_state["input_answer"] = ""

    def play(self):
        state = st.session_state.digitspan
        elapsed_time = time.time() - state["start_time"]
        time_left = state["total_time"] - elapsed_time

        # Display the timer, level, and score.
        st.write(f"**Time Left:** {int(time_left)} seconds")
        st.write(f"**Level:** {state['level']} / 18  |  **Score:** {state['score']}")

        # If time is up or maximum level reached, end the game.
        if time_left <= 0 or state["level"] > 18:
            st.write("Time's up or maximum level reached!")
            st.write(f"**Final Score:** {state['score']}  |  Level: {state['level'] - 1}")
            return

        # Stage: init – waiting to start a level.
        if state["stage"] == "init":
            if st.button("Start Level", key="start_level", on_click=self.start_level):
                return  # on_click will update the state.
            if state.get("result_message"):
                st.write(state["result_message"])

        # Stage: show – display the sequence for a fixed time.
        elif state["stage"] == "show":
            sequence_placeholder = st.empty()
            sequence_placeholder.write(
                f"**Sequence ({state['digit_count']} chars):** {state['current_sequence']}"
            )
            st.write(f"This sequence will be visible for {state['display_time']} seconds...")
            time.sleep(state["display_time"])
            sequence_placeholder.empty()
            state["stage"] = "input"

        # Stage: input – allow the user to type in the sequence.
        if state["stage"] == "input":
            st.text_input("Enter the sequence:", key="input_answer", on_change=self.check_answer)
            st.write("Press Enter or click outside the box to submit.")

        # Pause briefly and then re-run the script to update the timer.
        time.sleep(1)
        st.rerun()
