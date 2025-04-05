import time
import streamlit as st
import random

class PathfinderGame:
    def __init__(self):
        # Initialize session state for Pathfinder if not already set.
        if "pathfinder" not in st.session_state:
            st.session_state.pathfinder = {
                "start_time": time.time(),   # Game start time
                "total_time": 300,           # Total game time in seconds (5 minutes)
                "score": 0,                  # Starting score
                "level": 1,                  # Starting level (or puzzle number)
                "stage": "init",             # Game stages: init, puzzle, gameover
                "current_puzzle": None,      # Placeholder for the current puzzle's road pieces
                "result_message": ""         # Placeholder for feedback messages
            }

    def generate_puzzle(self):
        """
        Generates a puzzle by selecting a template from multiple templates and then scrambling the order.
        """
        puzzle_templates = [
            [
                {"id": 1, "type": "endpoint", "open_edges": ["right"]},
                {"id": 2, "type": "straight", "open_edges": ["left", "right"]},
                {"id": 3, "type": "straight", "open_edges": ["left", "right"]},
                {"id": 4, "type": "endpoint", "open_edges": ["left"]}
            ],
            [
                {"id": 5, "type": "endpoint", "open_edges": ["down"]},
                {"id": 6, "type": "corner", "open_edges": ["up", "right"]},
                {"id": 7, "type": "straight", "open_edges": ["left", "right"]},
                {"id": 8, "type": "endpoint", "open_edges": ["left"]}
            ],
            [
                {"id": 9, "type": "corner", "open_edges": ["up", "left"]},
                {"id": 10, "type": "straight", "open_edges": ["up", "down"]},
                {"id": 11, "type": "corner", "open_edges": ["down", "right"]}
            ]
        ]
        
        correct_order = random.choice(puzzle_templates)
        scrambled_order = correct_order.copy()
        random.shuffle(scrambled_order)
        
        st.session_state.pathfinder["current_puzzle"] = {
            "correct_order": correct_order,
            "scrambled_order": scrambled_order
        }
    
    def display_reorder_ui(self):
        """
        Displays the scrambled puzzle pieces with options to move them.
        Each piece is displayed in a horizontal row with left/right buttons.
        """
        puzzle = st.session_state.pathfinder.get("current_puzzle")
        if not puzzle:
            st.write("No puzzle available.")
            return
        
        scrambled = puzzle["scrambled_order"]
        
        st.write("### Reorder the Puzzle Pieces")
        for idx, piece in enumerate(scrambled):
            left_col, text_col, right_col = st.columns([1, 4, 1])
            
            with left_col:
                if st.button("←", key=f"pathfinder_left_{idx}", help="Move this piece left"):
                    self.move_piece(idx, "left")
                    st.rerun()
            
            with text_col:
                st.markdown(f"**ID:** {piece['id']} &nbsp;&nbsp; **Type:** {piece['type']} &nbsp;&nbsp; **Edges:** {piece['open_edges']}")
            
            with right_col:
                if st.button("→", key=f"pathfinder_right_{idx}", help="Move this piece right"):
                    self.move_piece(idx, "right")
                    st.rerun()
    
    def move_piece(self, index, direction):
        """
        Moves a puzzle piece left or right in the scrambled order.
        """
        puzzle = st.session_state.pathfinder["current_puzzle"]
        order = puzzle["scrambled_order"]
        if direction == "left" and index > 0:
            # Swap with the piece on the left
            order[index], order[index - 1] = order[index - 1], order[index]
        elif direction == "right" and index < len(order) - 1:
            # Swap with the piece on the right
            order[index], order[index + 1] = order[index + 1], order[index]
        puzzle["scrambled_order"] = order
        st.session_state.pathfinder["current_puzzle"] = puzzle
    
    def check_solution(self):
        """
        Checks if the current scrambled order matches the correct order.
        Comparison is based on the sequence of piece IDs.
        """
        puzzle = st.session_state.pathfinder.get("current_puzzle")
        if not puzzle:
            st.session_state.pathfinder["result_message"] = "No puzzle to check."
            return
        
        correct = [piece["id"] for piece in puzzle["correct_order"]]
        current = [piece["id"] for piece in puzzle["scrambled_order"]]
        
        if current == correct:
            st.session_state.pathfinder["result_message"] = "Correct!"
            st.session_state.pathfinder["score"] += 1
            st.session_state.pathfinder["level"] += 1
        else:
            st.session_state.pathfinder["result_message"] = "Incorrect."
        # Prepare for the next puzzle
        st.session_state.pathfinder["stage"] = "init"
    
    def play(self):
        state = st.session_state.pathfinder

        # CSS Styling for a better look
        st.markdown(
            """
            <style>
            h3, h4 {
                color: #FF9900;
            }
            .stButton button {
                background-color: #4F2E82;
                color: white;
                font-weight: bold;
                border-radius: 6px;
                padding: 0.5em 1em;
            }
            </style>
            """,
            unsafe_allow_html=True
        )

        # Calculate remaining time
        elapsed = time.time() - state["start_time"]
        time_left = state["total_time"] - elapsed

        st.write(f"**Time Left:** {int(time_left)} seconds")
        st.write(f"**Level:** {state['level']}  |  **Score:** {state['score']}")

        if time_left <= 0:
            st.write("Time is up!")
            st.write(f"**Final Score:** {state['score']}")
            return

        # Stage: init - waiting to generate a new puzzle
        if state["stage"] == "init":
            if st.button("Generate New Puzzle", key="pathfinder_generate"):
                self.generate_puzzle()
                state["stage"] = "puzzle"
                state["result_message"] = ""
                st.rerun()

        # Stage: puzzle - display the puzzle reordering UI
        elif state["stage"] == "puzzle":
            self.display_reorder_ui()
            st.write("Arrange the pieces to form a connected pathway.")
            if st.button("Submit Order", key="pathfinder_submit"):
                self.check_solution()
                st.rerun()

        if state["result_message"]:
            st.write(state["result_message"])
