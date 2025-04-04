import random
import time
import streamlit as st

class NumerosityGame:
    def __init__(self):
        if "numerosity" not in st.session_state:
            st.session_state.numerosity = {
                "start_time": time.time(),
                "total_time": 180,  # 3 minutes
                "level": 1,
                "score": 0,
                "stage": "init",  # Can be "init" or "challenge"
                "operator": None,
                "target": None,
                "pool": [],
                "selected": [],
                "result_message": ""
            }

    def generate_puzzle(self):
        """Creates a new numerical puzzle and updates the session state."""
        level = st.session_state.numerosity["level"]
        operators = ["+", "-", "*", "/"]
        op = random.choice(operators)
        st.session_state.numerosity["operator"] = op

        pool_size = 7 + level - 1
        number_range = (1, 20) if level < 3 else (1, 50)

        if op == "+":
            a, b, c = [random.randint(*number_range) for _ in range(3)]
            target = a + b + c
        elif op == "-":
            b = random.randint(*number_range)
            c = random.randint(*number_range)
            a = random.randint(b + c, b + c + (number_range[1] - number_range[0]))
            target = a - b - c
        elif op == "*":
            a = random.randint(1, max(2, number_range[1] // 2))
            b = random.randint(1, max(2, number_range[1] // 2))
            c = random.randint(1, max(2, number_range[1] // 2))
            target = a * b * c
        elif op == "/":
            r = random.randint(1, 10)
            b = random.randint(1, max(2, number_range[1] // 2))
            c = random.randint(1, max(2, number_range[1] // 2))
            a = r * b * c
            target = int(a / b / c)

        valid_numbers = [a, b, c]
        pool = valid_numbers.copy()
        while len(pool) < pool_size:
            pool.append(random.randint(*number_range))
        random.shuffle(pool)

        st.session_state.numerosity.update({
            "target": target,
            "pool": pool,
            "selected": [],
            "result_message": "",
            "stage": "challenge"
        })

    def toggle_number(self, index):
        """Toggles selection status of a number in the pool."""
        selected = st.session_state.numerosity["selected"]
        if index in selected:
            selected.remove(index)
        else:
            if len(selected) < 3:
                selected.append(index)
            else:
                st.session_state.numerosity["result_message"] = "You can only select 3 numbers."

    def submit_answer(self):
        """Evaluates the selected numbers and checks if they produce the target result."""
        state = st.session_state.numerosity
        indices = state["selected"]
        if len(indices) != 3:
            state["result_message"] = "Please select exactly 3 numbers."
            return

        selected_numbers = [state["pool"][i] for i in indices]
        op = state["operator"]

        try:
            if op == "+":
                result = sum(selected_numbers)
            elif op == "-":
                result = selected_numbers[0] - selected_numbers[1] - selected_numbers[2]
            elif op == "*":
                result = selected_numbers[0] * selected_numbers[1] * selected_numbers[2]
            elif op == "/":
                if selected_numbers[1] == 0 or selected_numbers[2] == 0:
                    result = None
                else:
                    result = int(selected_numbers[0] / selected_numbers[1] / selected_numbers[2])
        except ZeroDivisionError:
            result = None

        if result == state["target"]:
            state["result_message"] = "✅ Correct!"
            state["score"] += 1
            state["level"] += 1
        else:
            state["result_message"] = (
                f"❌ Incorrect! Your answer: {selected_numbers} = {result}, "
                f"but the target was {state['target']}."
            )

        state["stage"] = "init"

    def play(self):
        """Controls game flow: timer, levels, and user interaction."""
        state = st.session_state.numerosity
        elapsed = time.time() - state["start_time"]
        remaining = int(state["total_time"] - elapsed)

        if remaining <= 0:
            st.warning("⏰ Time's up!")
            st.success(f"Final Score: {state['score']}")
            return

        st.markdown(
            f"""
            <div style='position:fixed; top:10px; right:20px;
                        background-color:#f0f0f0; padding:10px 20px;
                        border-radius:10px; border:1px solid #ddd;
                        font-weight:bold; font-size:18px; z-index:1000;'>
                ⏰ Time Left: {remaining} seconds
            </div>
            """, unsafe_allow_html=True
        )

        st.write(f"**Level:** {state['level']}  |  **Score:** {state['score']}")

        if state["stage"] == "init":
            st.button("Start New Puzzle", key="new_puzzle", on_click=self.generate_puzzle)
            if state.get("result_message"):
                st.write(state["result_message"])

        elif state["stage"] == "challenge":
            st.write(f"**Operation:** {state['operator']}")
            st.write(f"**Target Result:** {state['target']}")
            st.write("### Number Pool:")
            cols = st.columns(5)
            for idx, num in enumerate(state["pool"]):
                col = cols[idx % 5]
                label = f"[X] {num}" if idx in state["selected"] else str(num)
                col.button(label, key=f"num_{idx}", on_click=self.toggle_number, args=(idx,))

            st.write("**Selected Numbers:**", [state["pool"][i] for i in state["selected"]])
            st.button("Submit Answer", key="submit", on_click=self.submit_answer)

            if state.get("result_message"):
                st.write(state["result_message"])

        # Auto-refresh for live timer
        time.sleep(1)
        st.rerun()
