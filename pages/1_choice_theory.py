import random
from itertools import combinations

import numpy as np
import pandas as pd
import src.scripts.plot_themes as thm
import src.scripts.utils as utl
import streamlit as st
from matplotlib import pyplot as plt
from st_pages import add_page_title

### PAGE CONFIGS ###
utl.micro_page_config()
utl.local_css("src/styles/styles_pages.css")

# create one column with consistent width
_, col_top, _ = utl.wide_col()

### PAGE INTRO ###

with col_top:
    st.title("Preferences and Choices")
    st.header("Rationality, WARP, and Utility Representation")
    st.write(
        "This week we're studying Choice Theory, which is at the core of microecnomic theory."
    )
    st.write(
        "As a visual exercise, I decided to build a simple game to check if you're consistent in your choices."
    )

### START OF CONTENT ###


### VISUALS ###
_, c1, _ = utl.wide_col()

with c1:
    st.markdown(
        "<h3 style='text-align: left'> 1. Let's check your fruit choices!</h3>",
        unsafe_allow_html=True,
    )

    st.markdown(
        r"""Suppose there are 4 fruits: Apple, Banana, Mango, and Orange.<br>
                You will be given different menus ("bundles) of 2-3 fruits to choose from.<br>
                Based on your preferences, pick one or more fruits from each bundle.<br>
                Once you finish, you can check if you're not violating axioms of the rational choice theory.""",
        unsafe_allow_html=True,
    )

_, warp_col, _ = st.columns((0.2, 1, 0.2))

with warp_col:
    st.markdown(
        "<h3 style='text-align: center'>WARP checker</h3>",
        unsafe_allow_html=True,
    )

    # Pseudo code for WARP violation checker:
    # 1. Generate bundles of size 2 and 3 from the given items.
    # 2. Display a bundle of items to the user.
    # 3. User selects the items they prefer.
    # 4. Record the user's choice.
    # 5. Remove shown bundle from the list
    # 6. Do not allow empty choices
    # 7. Repeat steps 2-6 until all bundles have been shown.
    # 8. Check if the user chose consistently according to WARP in all of the bundles.
    # 9. If WARP is violated, display the reason and the bundles where the violation occurred.
    # 10. If WARP is not violated, display a message saying so.

    # Items and Bundles
    items = ["Apple", "Banana", "Mango", "Orange"]

    def generate_bundles(items):
        """Generate bundles of size 2 and 3 from the given items."""
        bundles = []
        for i in range(3, 4):
            bundles.extend(combinations(items, i))
        return bundles

    BUNDLES = generate_bundles(items)

    # Session state to keep track of choices, the current bundle, and shown bundles
    def initialize_session_state():
        st.session_state.choices = []
        st.session_state.shown_bundles = []
        st.remaining_bundles = BUNDLES
        st.session_state.current_bundle = random.choice(BUNDLES)
        st.session_state.end_choices = False

    if "shown_bundles" not in st.session_state:
        initialize_session_state()

    bundle_number = len(st.session_state.shown_bundles) + 1

    if bundle_number <= len(BUNDLES):
        # Displaying the current bundle
        st.write(
            f"Bundle {bundle_number} of {len(BUNDLES)}. Please select one or more items."
        )

        # Displaying checkboxes for the items in the current bundle
        selected_items = []
        for item in st.session_state.current_bundle:
            # Use the bundle number as a unique key for each checkbox
            unique_key = f"{item}_{bundle_number}"
            checked = st.checkbox(item, key=unique_key)
            if checked:
                selected_items.append(item)

        confirm = st.button("Confirm Choices")
        if confirm and selected_items:
            # Record choices and shown bundles
            st.session_state.choices.append(set(selected_items))
            st.session_state.shown_bundles.append(st.session_state.current_bundle)

            # Remove current bundle from the remaining ones
            st.session_state.remaining_bundles = [
                bundle
                for bundle in BUNDLES
                if bundle not in st.session_state.shown_bundles
            ]

            # Check if there are any remaining bundles left and pick one if so
            if st.session_state.remaining_bundles:
                st.session_state.current_bundle = random.choice(
                    st.session_state.remaining_bundles
                )
            st.rerun()
    else:
        st.write("All bundles have been shown.")
        st.session_state.end_choices = True

    def generate_html_table(bundles, choices):
        """Generate an HTML table from lists of bundles and choices."""
        html_table = '<table border="1">'

        # Add the headers
        html_table += "<thead><tr><th>Bundles</th><th>Choices</th></tr></thead><tbody>"

        # Add the rows of data
        for bundle, choice in zip(bundles, choices):
            bundle_str = str(bundle).replace("'", "")
            choice_str = str(choice).replace("'", "")

            html_table += f"<tr><td>{bundle_str}</td><td>{choice_str}</td></tr>"

            # html_table += f"<tr><td>{bundle}</td><td>{choice}</td></tr>"

        # Close the table
        html_table += "</tbody></table>"

        return html_table

    # After you have collected all bundles and choices:
    if st.session_state.end_choices:
        html_table = generate_html_table(
            st.session_state.shown_bundles, st.session_state.choices
        )
        st.markdown(html_table, unsafe_allow_html=True)

    def check_warp_pairwise(
        x,
        y,
        bundles=st.session_state.shown_bundles,
        choices=st.session_state.choices,
    ):
        """Check if the user chose consistently according to WARP in all of the bundles."""
        bundles_xy = []
        rel_choices = []
        # bundle_index = []

        for i in range(len(bundles)):
            if (x in bundles[i]) and (y in bundles[i]):
                bundles_xy.append(bundles[i])
                rel_choices.append(choices[i])
                # bundle_index.append(i)

        # st.write(f"Bundles that contain both {x} and {y}: {bundles_xy}")
        # st.write(f"Respective choices: {rel_choices}")

        # check if x, y were chosen at least once across relevant bundles
        choose_x = [(b, c) for b, c in zip(bundles_xy, rel_choices) if x in c]
        choose_y = [(b, c) for b, c in zip(bundles_xy, rel_choices) if y in c]
        len_x = len(choose_x)
        len_y = len(choose_y)

        if len_x == 0 or len_y == 0:
            return {
                "condition": False,
                "reason": "Impossible to detect WARP violation.",
            }

        # conditions for violation of WARP
        # either x or y was chosen in all bundles or both were chosen in all bundles
        warp_A = []
        warp_B = []

        if 0 < len_x < len(rel_choices):
            # if condition fails, then it meanst that x was chosen in at least one but not all bundles
            for bundle, choice in zip(bundles_xy, rel_choices):
                if x in choice:
                    warp_A = [bundle, choice]
                elif y in choice:
                    warp_B = [bundle, choice]

            return {
                "condition": True,
                "reason": "WARP violation detected!",
                "item_1": x,
                "item_2": y,
                "chosen": warp_A,
                "not_chosen": warp_B,
            }

        elif 0 < len_y < len(rel_choices):
            # if condition fails, then it meanst that y was chosen in at least one but not all bundles
            for bundle, choice in zip(bundles_xy, rel_choices):
                if y in choice:
                    warp_A = [bundle, choice]
                elif x in choice:
                    warp_B = [bundle, choice]

            return {
                "condition": True,
                "reason": "WARP violation detected!",
                "item_1": y,
                "item_2": x,
                "chosen": warp_A,
                "not_chosen": warp_B,
            }

        else:
            return {"condition": False, "reason": "WARP was not violated."}

    if st.session_state.end_choices:
        # loop through all pairs of items until a WARP violation is found
        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("Check for WARP violations", type="primary"):
            for x, y in combinations(items, 2):
                warp = check_warp_pairwise(x, y)
                # st.write("looping", x, y)
                # st.write(f"""{warp["reason"]}""")

                if warp["condition"]:
                    st.write("Your choices were inconsistent according to WARP.😔")

                    st.markdown(
                        f"""**Explanation:**<br>
                    Let's call bundles $A=$ {warp["chosen"][0]} and $B=$ {warp["not_chosen"][0]}<br>
                    Your choices were:<br>
                    $C(A)=C${warp["chosen"][0]} $=${warp["chosen"][1]}<br>
                    $C(B)=C${warp["not_chosen"][0]} $=${warp["not_chosen"][1]}<br>                                                          
                    Both {warp["item_1"]} and {warp['item_2']} were available in bundles $A$ and $B$.<br>
                    {warp["item_1"]} was among choices from $A$ and {warp["item_2"]} was among choices from $B$.<br>
                    However {warp["item_1"]} was not chosen from $B$.<br>
                    Therefore, WARP is violated.""",
                        unsafe_allow_html=True,
                    )

                    break  # exit the loop once the first violation is found
            else:
                st.write("No WARP violations detected.🥳")
                st.write(
                    "Don't get too excited though, we'd need more choices to fully check whether your preferences are rational."
                )

        # Refresh only works if it's outside/independent of WARP button, otherwise it will only refresh WARP
        if st.button("Click to Restart", type="primary"):
            # If button pressed, trigger JS to refresh page
            st.write(
                '<meta http-equiv="refresh" content="1">',
                unsafe_allow_html=True,
            )

_, c2, _ = utl.wide_col()

with c2:
    st.markdown(
        "<h4 style='text-align: left'>Interesting takeaways</h4>",
        unsafe_allow_html=True,
    )

    # Streamlit is annoying because it doesn't render inline equations $$ within HTML tags
    # Need to find a solution around that, e.g., with st.latex(), and increase margins manually with CSS?
    st.markdown(
        r"""
            Building this algorithm definitely helped me internalize WARP for life. Below is my way of converting math into code.<br>
            WARP states that if $x, y \in B_1 \cap B_2$ and if $x \in C(B_1)$, $y \in C(B_2)$, then it must be the case that $x \in C(B_2)$. <br>
            1. Observe that WARP only applies to bundles that contain both $x$ and $y$.<br>
            2. Thus it also requires a pairwise comparison of each two items, $x$ and $y$, e.g., Apple and Banana, Apple and Mango, etc.
            (maybe there was a more efficient way?)<br>
            3. Then for each pair of bundles apply the following:<br>
            a. Filter shown bundles to only those that contain both $x$ and $y$.<br>
            b. Filter choices from these bundles into two lists, one where $x$ was chosen and one where $y$ was chosen separately.<br>
            c. For WARP to hold, either $x$ or $y$ or both must be chosen in all relevant bundles.
            Therefore, if either of the lists is empty or if both lists are same length, then WARP is not violated.<br>
            d. If (c.) doesn't hold, then filter through the relevant bundles to pick two bundles $A$ and $B$
            and their choices to proof WARP violation in text.<br>
            """,
        unsafe_allow_html=True,
    )

    rev_prefs_link = "https://cran.r-project.org/web/packages/revealedPrefs/index.html"
    st.markdown(
        rf"""I found this package in R, [revealedPrefs]({rev_prefs_link}), which seem to have more efficient/general solutions. Is there no need to for this in Python?""",
        unsafe_allow_html=True,
    )


### THEORY ###
_, c3, _ = utl.wide_col()

with c3:
    st.markdown(
        "<h3 style='text-align: left'> 2. Theory</h3>",
        unsafe_allow_html=True,
    )

    st.write(
        "Collection of statements about preference relations and utility representation."
    )

    st.write("Work in progress - check back soon.")

### EXERCISES ###
_, c4, _ = utl.wide_col()

with c4:
    st.markdown(
        "<h3 style='text-align: left'> 3. Exercises </h3>",
        unsafe_allow_html=True,
    )

    st.write(
        r"Check out Rubinstein's lecture notes for exercises of all levels of difficulty."
    )

    st.link_button(
        "Rubinstein's Lecture Notes, pp. 10-11, 21-23, 44-47",
        "https://arielrubinstein.tau.ac.il/books/PUP2020.pdf",
        type="secondary",
    )

### PROOFS ###
_, c5, _ = utl.wide_col()

with c5:
    st.markdown(
        "<h3 style='text-align: left'> 4. Proofs to remember</h3>",
        unsafe_allow_html=True,
    )

    st.write(
        r"This will contain some of the main proofs. I'll try to explain how I memorize math in plain English."
    )

    st.write("Work in progress - check back soon.")
