import difflib
import os
import streamlit as st
import pandas as pd

# Set up webpage configuration
st.set_page_config(page_title="The League Tables Football Finder", layout="centered")

st.title("┌────────────────────────────────────┐")
st.title("│ The League Tables Football Finder  │")
st.title("└────────────────────────────────────┘")
st.write("*(Separate multiple players with commas, e.g., Messi, Ronaldo)*")

file_name = "ExampleFootball.xlsx"

if not os.path.exists(file_name):
    st.error(f"Notification: The file '{file_name}' was not found in your GitHub repository.")
    st.info("Please upload your Excel file to the same GitHub folder as this script.")
else:
    try:
        df = pd.read_excel(file_name)
        
        # Automatically find the player/name column dynamically
        player_col = None
        for col in df.columns:
            if "player" in str(col).lower() or "name" in str(col).lower():
                player_col = col
                break
        
        if player_col is None and len(df.columns) > 0:
            player_col = df.columns[0]

        if player_col is not None:
            # Force conversion to safe string values
            df[player_col] = df[player_col].astype(str)

            # Web input box instead of command line input()
            user_input = st.text_input("Enter player name(s):", key="player_search").strip()

            if user_input:
                # Split the input by commas and clean up extra spaces
                search_names = [name.strip() for name in user_input.split(",") if name.strip()]
                
                # Combine multiple search names into a single regular expression
                search_regex = "|".join(search_names)
                result = df[df[player_col].str.contains(search_regex, case=False, na=False)]

                if result.empty:
                    st.warning("Could not locate any footballers matching your search.")
                    
                    # Fetch unique values for typo suggestions
                    all_players = df[player_col].unique().tolist()
                    for target in search_names:
                        if not df[df[player_col].str.contains(target, case=False, na=False)].empty:
                            continue
                        suggestions = difflib.get_close_matches(target, all_players, n=2, cutoff=0.3)
                        if suggestions:
                            st.write(f"Did you mean for **{target}**:")
                            for name in suggestions:
                                st.write(f"- {name}")
                else:
                    # Filter out requested exclusion columns
                    columns_to_remove = ["Matches", "Rk", "Age", "90s", "MP", "G+A", "G+A-PK", "Gls.1", "Ast.1", "G+A.1", "G-PK.1"]
                    clean_result = result.drop(columns=columns_to_remove, errors="ignore")

                    # Display natively as an interactive, clean web table grid
                    st.dataframe(clean_result, use_container_width=True)
        else:
            st.error("Notification: The Excel sheet appears to be empty.")
            
    except Exception as e:
        st.error("An unexpected issue occurred while loading the data.")
