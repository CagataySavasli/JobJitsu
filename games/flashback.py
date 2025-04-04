import time
import streamlit as st
import random


class FlashbackGame:
    def __init__(self):
        #initialize session for flashback
        if "flashback" not in st.session_state:
            st.session_state.flashback = {
                "start_time" : time.time(), #game start time
                "total_time" : 180, #total game time in second
                "level" : 1, #initial level
                "score":0, #initial score
                "stage": "init", #init, display, input stages
                "current_shape" : None,
                "shape_history" : [],
                "result_message" : ""
            }
            
            #### placeholder for user input (if needed later)
            st.session_state["input_response"] = ""

    def generate_shape(self):
        """
        Generates a random shape with a random color.
        For now, we choose from circle, square, or triangle, with a single color.
        Later, we can add two-color logic based on the level.
        """
        shapes = ["circle","square","triangle"]
        colors = ["red","blue","green","orange","purple","yellow"]
        shape = random.choice(shapes)
        color = random.choice(colors)
        
        shape_info = {"shape: " : shape, "color" : color}
        st.session_state.flashback["current_shape"] = shape_info
        st.sesson_state.flashback["shape_history"].append(shape_info)
    
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
        shape_info = st.sesion_state.flashback["current_shape"]
        if shape_info:
            html = self.get_shape_html(shape_info)
            st.markdown(html,unsafe_allow_html = True)
    
    def play(self):
        """
        For testing purposes, this play method allows you to generate and display a shape.
        """
        state = st.session_state.flashback
        st.write(f"**Level:** {state['level']}  |  **Score:** {state['score']}")
        if st.button("Generate Shape"):
            self.generate_shape()
            state["stage"] = "display"
        if state["stage"] == "display":
            self.display_shape()
            st.write("This is the current shape. (Further logic will handle matching and user input.)")
        