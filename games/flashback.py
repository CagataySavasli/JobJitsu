import time
import streamlit as st
import random

class FlashbackGame:
    def __init__(self):
        # Initialize session state for flashback
        if "flashback" not in st.session_state:
            st.session_state.flashback = {
                "start_time": time.time(),  # game start time
                "total_time": 180,           # total game time in seconds
                "level": 1,                # initial level
                "score": 0,                # initial score
                "stage": "init",           # stages: init, display, input, gameover
                "current_shape": None,
                "shape_history": [],
                "result_message": ""
            }
            # Placeholder for user input (if needed later)
            st.session_state["input_response"] = ""

    def generate_shape(self):
        """
        Generates a random shape with a random color.
        For now, we choose from circle, square, or triangle, with a single color.
        """
        shapes = ["circle", "square", "triangle"]
        colors = ["red", "blue", "green", "orange", "purple", "yellow"]
        shape = random.choice(shapes)
        color = random.choice(colors)
        
        shape_info = {"shape": shape, "color": color}
        st.session_state.flashback["current_shape"] = shape_info
        st.session_state.flashback["shape_history"].append(shape_info)
    
    def get_shape_html(self, shape_info):
        """
        Returns an HTML snippet representing the given shape.
        Uses inline CSS for simple styling.
        """
        shape = shape_info["shape"]
        color = shape_info["color"]
        if shape == "circle":
            style = (
                f"width: 60px; height: 60px; "
                f"background-color: {color}; border-radius: 50%; "
                "display: inline-block;"
            )
        elif shape == "square":
            style = (
                f"width: 60px; height: 60px; "
                f"background-color: {color}; "
                "display: inline-block;"
            )
        elif shape == "triangle":
            style = (
                "width: 0; height: 0; "
                "border-left: 30px solid transparent; "
                "border-right: 30px solid transparent; "
                f"border-bottom: 60px solid {color}; "
                "display: inline-block;"
            )
        return f'<div style="{style}"></div>'

    def display_shape(self):
        shape_info = st.session_state.flashback["current_shape"]
        if shape_info:
            html = self.get_shape_html(shape_info)
            st.markdown(html, unsafe_allow_html=True)
    
    def check_answer(self, user_choice: bool):
        state = st.session_state.flashback
        history = state["shape_history"]
        # There should be at least 2 shapes when we compare
        if len(history) < 2:
            state["result_message"] = "Not enough shapes to compare"
            state["stage"] = "init"
            return
        
        # Get the previous and current shapes
        prev_shape = history[-2]
        current_shape = history[-1]
        
        is_match = (prev_shape["shape"] == current_shape["shape"] and
                    prev_shape["color"] == current_shape["color"])
        
        if user_choice == is_match:
            state["result_message"] = "Correct!!!!"
            state["score"] += 1
            state["level"] += 1
            state["stage"] = "init"  # Continue to next round
        else:
            state["result_message"] = "Incorrect !!!!"
            state["stage"] = "gameover"  # Stop game on wrong answer
    
    def play(self):
        state = st.session_state.flashback
        
        # Calculate remaining time
        elapsed = time.time() - state["start_time"]
        time_left = state["total_time"] - elapsed
        
        st.write(f"**Time Left:** {int(time_left)} seconds")
        st.write(f"**Level:** {state['level']}  |  **Score:** {state['score']}")
        
        if time_left <= 0:
            st.write("Time is up!")
            st.write(f"**Final Score:** {state['score']}")
            return
        
        # Handle Game Over stage
        if state["stage"] == "gameover":
            st.write("Game Over!")
            st.write(f"**Final Score:** {state['score']}")
            return
        
        # Stage: init - Waits to start a new round.
        if state["stage"] == "init":
            # For the very first round, there is no previous shape
            # So we generate one and remain in init to prime the game.
            if len(state["shape_history"]) < 1:
                if st.button("Show Next Shape", key="first_shape"):
                    self.generate_shape()
                    # Remain in init so that no comparison is attempted yet.
                    state["result_message"] = ""
                    st.experimental_rerun()
            else:
                # For subsequent rounds, generate the next shape and then move to display.
                if st.button("Show Next Shape", key="next_shape"):
                    self.generate_shape()
                    state["stage"] = "display"
                    state["result_message"] = ""
                    st.experimental_rerun()
        
        # Stage: display - Show the current shape briefly.
        elif state["stage"] == "display":
            self.display_shape()
            st.write("Memorize this shape....")
            # Pause briefly (blocking call; in production, consider alternatives)
            time.sleep(2)
            # Move to input stage only if we have at least 2 shapes to compare.
            if len(state["shape_history"]) < 2:
                state["stage"] = "init"
            else:
                state["stage"] = "input"
            st.experimental_rerun()
        
        # Stage: input - Ask the user for their response.
        elif state["stage"] == "input":
            st.write("Do the last two shapes match?")
            if st.button("Match", key="match_button"):
                self.check_answer(True)
                st.experimental_rerun()
            if st.button("No Match", key="nomatch_button"):
                self.check_answer(False)
                st.experimental_rerun()
        
        # Display any feedback messages.
        if state["result_message"]:
            st.write(state["result_message"])
