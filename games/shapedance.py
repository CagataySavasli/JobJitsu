import random
import time
import math
import streamlit as st


# ---------- Utility Functions for HTML & CSS ---------- #

def generate_shape_html(shape: str, color: str) -> str:
    """
    Returns an HTML snippet representing a shape (circle, square, triangle)
    in a given color.
    """
    if shape == "circle":
        style = (
            "width: 40px; "
            "height: 40px; "
            f"background-color: {color}; "
            "border-radius: 50%; "
            "display: inline-block;"
        )
    elif shape == "square":
        style = (
            "width: 40px; "
            "height: 40px; "
            f"background-color: {color}; "
            "display: inline-block;"
        )
    elif shape == "triangle":
        # Create an upward-pointing triangle using borders.
        style = (
            "width: 0; "
            "height: 0; "
            "border-left: 20px solid transparent; "
            "border-right: 20px solid transparent; "
            f"border-bottom: 40px solid {color}; "
            "display: inline-block;"
        )
    return f'<div style="{style}"></div>'


def create_cube_html(pattern: list, selected: bool = False, transform: tuple = None) -> str:
    """
    Creates an HTML "card" to display the pattern of shapes.
    The pattern is arranged in a square grid based on the number of symbols.
    Applies a stored transformation (rotation and mirror) if provided.
    Adds a green border if the cube is selected.
    """
    # Use the provided transformation or default to no rotation/mirror.
    if transform is not None:
        rotation, mirror = transform
        transform_str = f"rotate({rotation}deg)"
        if mirror:
            transform_str += " scaleX(-1)"
    else:
        transform_str = "rotate(0deg)"

    extra_style = "border: 4px solid green;" if selected else ""

    # Compute grid dimensions: number of columns is the ceiling of the square root of number of symbols.
    grid_size = math.ceil(math.sqrt(len(pattern)))
    # Build the grid container for symbols.
    grid_container_style = (
        f"display: grid; grid-template-columns: repeat({grid_size}, 1fr); "
        "grid-gap: 4px; justify-items: center; align-items: center;"
    )
    grid_html = f'<div style="{grid_container_style}">'
    for (s, c) in pattern:
        grid_html += generate_shape_html(s, c)
    grid_html += "</div>"

    # Build the overall cube container style.
    container_style = (
        "display: inline-block; "
        "background-color: #4F2E82; "
        "border-radius: 8px; "
        "padding: 16px; "
        "margin: 8px; "
        "overflow: visible; "  # Ensure shapes aren't clipped.
        f"{extra_style} "
        f"transform: {transform_str}; "
        "transition: transform 1s;"
    )

    html = f'<div style="{container_style}">{grid_html}</div>'
    return html


# ---------- Main ShapedanceGame Class ---------- #

class ShapedanceGame:
    def __init__(self):
        if "shapedance" not in st.session_state:
            st.session_state.shapedance = {
                "start_time": time.time(),
                "total_time": 180,  # 3 minutes total game time (in seconds)
                "level": 1,
                "score": 0,
                "stage": "init",  # "init" before a level starts, then "active" during play
                "current_patterns": [],
                "matching_pair": [],
                "transformations": [],  # List of (rotation, mirror) for each cube.
                "result_message": "",
                "num_cubes": 0,
                "pattern_length": 0,
                "selected": []  # List to track currently selected cube indices
            }

    def compute_difficulty(self):
        """
        Adjust difficulty based on current level:
          - Increases pattern length every 3 levels.
          - Increases number of cubes (4, 6, 8, …).
        """
        level = st.session_state.shapedance["level"]
        pattern_length = 2 + ((level - 1) // 3)
        num_cubes = 4 + 2 * ((level - 1) // 3)
        return pattern_length, num_cubes

    def generate_pattern(self, length: int) -> list:
        """
        Generate a pattern as a list of (shape, color) tuples.
        """
        shapes = ["circle", "square", "triangle"]
        colors = ["red", "orange", "yellow", "green", "blue", "purple"]
        pattern = []
        for _ in range(length):
            shape = random.choice(shapes)
            color = random.choice(colors)
            pattern.append((shape, color))
        return pattern

    def start_level(self):
        """
        Sets up a new level by generating cube patterns.
        Exactly two cubes will have the same pattern.
        Also creates a list of transformation parameters (rotation, mirror)
        for each cube.
        """
        pattern_length, num_cubes = self.compute_difficulty()
        matching_pattern = self.generate_pattern(pattern_length)

        # Randomly choose two distinct indices for the matching pair.
        indices = list(range(num_cubes))
        matching_pair = sorted(random.sample(indices, 2))

        patterns = []
        for i in range(num_cubes):
            if i in matching_pair:
                patterns.append(matching_pattern)
            else:
                pat = self.generate_pattern(pattern_length)
                while pat == matching_pattern:
                    pat = self.generate_pattern(pattern_length)
                patterns.append(pat)

        # Generate random transformation parameters for each cube.
        transformations = []
        for _ in range(num_cubes):
            rotation = random.randint(-180, 180)  # Rotation angle in degrees.
            mirror = random.choice([True, False])  # Randomly mirror horizontally.
            transformations.append((rotation, mirror))

        st.session_state.shapedance.update({
            "current_patterns": patterns,
            "matching_pair": matching_pair,
            "transformations": transformations,
            "stage": "active",
            "result_message": "",
            "num_cubes": num_cubes,
            "pattern_length": pattern_length,
            "selected": []
        })

    def toggle_selection(self, index):
        """
        Toggle the selection state of the cube with the given index.
        If a cube is already selected, clicking it again will deselect it.
        Once exactly two cubes are selected, check the answer.
        """
        state = st.session_state.shapedance
        selected = state.get("selected", [])
        if index in selected:
            selected.remove(index)
        else:
            selected.append(index)
        state["selected"] = selected

        # When two cubes are selected, check if they match.
        if len(selected) == 2:
            self.check_answer()

    def check_answer(self):
        """
        Checks whether the two selected cubes match.
        If correct, the score and level are updated and a new level begins.
        Otherwise, an error message is displayed and the selection is reset.
        """
        state = st.session_state.shapedance
        selected = sorted(state.get("selected", []))
        if selected == state["matching_pair"]:
            state["result_message"] = "Correct! Moving to the next level."
            state["score"] += 1
            state["level"] += 1
            self.start_level()
        else:
            state["result_message"] = (
                f"Incorrect! Your answer: {[x + 1 for x in selected]}. "
                f"Correct answer: {[x + 1 for x in state['matching_pair']]}. Try again."
            )
            state["selected"] = []

    def play(self):
        """
        Main game loop:
          - Displays the time left, level, and score.
          - Renders the current level's cubes (always visible) so the player can click to select/deselect.
        """
        state = st.session_state.shapedance
        elapsed_time = time.time() - state["start_time"]
        time_left = state["total_time"] - elapsed_time

        st.title("Shape Dance Game")
        st.write(f"**Time Left:** {int(time_left)} seconds")
        st.write(f"**Level:** {state['level']}  |  **Score:** {state['score']}")

        if time_left <= 0:
            st.write("Time's up!")
            st.write(f"**Final Score:** {state['score']}  |  Level reached: {state['level']}")
            return

        # Stage: Before level has started.
        if state["stage"] == "init":
            if st.button("Start Level", key="start_level", on_click=self.start_level):
                return
            if state.get("result_message"):
                st.write(state["result_message"])

        # Stage: Active play (cubes always visible).
        elif state["stage"] == "active":
            if state.get("result_message"):
                st.write(state["result_message"])
            num_cubes = state["num_cubes"]
            patterns = state["current_patterns"]
            transformations = state["transformations"]
            selected = state.get("selected", [])
            cols = st.columns(3)
            for i, pattern in enumerate(patterns):
                col = cols[i % 3]
                is_selected = i in selected
                # Use the stored transformation for this cube.
                cube_html = create_cube_html(pattern, selected=is_selected, transform=transformations[i])
                col.markdown(cube_html, unsafe_allow_html=True)
                col.button(
                    "Select/Deselect",
                    key=f"cube_button_{i}",
                    on_click=self.toggle_selection,
                    args=(i,)
                )
                if (i + 1) % 3 == 0 and (i + 1) < num_cubes:
                    cols = st.columns(3)

