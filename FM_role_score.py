import PySimpleGUI as sg
import json
import pandas as pd
from datetime import datetime

sg.theme('DarkAmber')

# Load roles from the JSON file
try:
    with open('player_roles.json', 'r') as file:
        roles_data = json.load(file)
except FileNotFoundError:
    sg.popup_error("Error: The file 'player_roles.json' was not found.")
    roles_data = {}
except json.JSONDecodeError:
    sg.popup_error("Error: The file 'player_roles.json' is not a valid JSON.")
    roles_data = {}
except Exception as e:
    sg.popup_error(f"An unexpected error occurred: {e}")
    roles_data = {}

# Create layout for the left side (checkboxes)
left_layout = []
for category, roles in roles_data.items():
    left_layout.append([sg.Text(category, font=("Arial", 12, "bold"))])
    for role in roles:
        left_layout.append([sg.Checkbox(role['role'], key=role['role_abbr'])])

# Create a scrollable column for the left side (roles)
left_column = sg.Column(left_layout, scrollable=True, vertical_scroll_only=True, size=(300, 400))

# Create layout for the right side (buttons and dropdown)
right_layout = [
    [sg.Button("Import", size=(15, 2), font=("Arial", 12))],
    [sg.Button("Calculate Selected", size=(15, 2), font=("Arial", 12))],
    [sg.Button("Calculate All", size=(15, 2), font=("Arial", 12))],
    [sg.Button("Save", size=(15, 2), font=("Arial", 12))],
    [sg.Combo(['-ALL-'], default_value='-ALL-', size=(18, 1), key='division_dropdown', readonly=True, enable_events=True)]
]

# Combine left and right layouts
layout = [
    [left_column, sg.VSeparator(), sg.Column(right_layout, vertical_alignment='top')]
]

# Create the window
window = sg.Window("FM Role Score Calculator", layout)

def import_html_table():
    file_path = sg.popup_get_file('Choose an HTML file', file_types=(("HTML Files", "*.html"),))
    if file_path:
        tables = pd.read_html(file_path, encoding='utf-8')
        if tables:
            df = tables[0]

            # Remove rows where the "Name" column is NaN
            df = df.dropna(subset=["Name"])
            
            # Function to clean and transform the data
            def transform_value(column, value):
                if column not in ["Inf", "Rec", "Name", "Nat", "Club", "Division", "Position", "Preferred Foot", "Height", "Weight"]:
                    if pd.isna(value) or value == '-':
                        return 1
                    if isinstance(value, str) and '-' in value:
                        parts = value.split('-')
                        return int(parts[0].strip() or 1)
                    try:
                        return int(float(value))
                    except ValueError:
                        return value  # Return the original value if conversion fails
                elif column == "Age":
                    try:
                        return int(float(value))
                    except ValueError:
                        return value  # Return the original value if conversion fails
                elif column == "Height":
                    # Remove " cm" from the height values
                    return int(value.split(' ')[0]) if isinstance(value, str) else value
                elif column == "Weight":
                    # Remove " kg" from the weight values
                    return int(value.split(' ')[0]) if isinstance(value, str) else value
                return value

            # Apply the transformation to each element in the DataFrame
            df = df.apply(lambda x: x.map(lambda v: transform_value(x.name, v)))

            # Extract unique divisions and update the dropdown menu
            unique_divisions = sorted(df['Division'].dropna().unique().tolist())
            window['division_dropdown'].update(values=['-ALL-'] + unique_divisions, value='-ALL-')

            sg.popup('Table Imported and Transformed')
            return df
        else:
            sg.popup('No tables found in the HTML file.')
            return None

def calculate_best_players(df, selected_roles, selected_division):
    eligible_positions_goalkeeper = ["GK"]
    eligible_positions_defender = ["D (C)", "D (LC)", "D (RC)", "D (RLC)", "D (L)", "D (R)", "D (RL)", "WB (RL)", "WB (L)", "WB (R)" , "DM"]
    eligible_positions_fullbacks = ["D (LC)", "D (RC)", "D (RLC)", "D (L)", "D (R)", "D (RL)", "WB (RL)", "WB (L)", "WB (R)", "M (L)", "M (R)", "M (RL)"]

    best_players = {}

    for category, roles_info in roles_data.items():
        for role_info in roles_info:
            role = role_info['role']
            role_abbr = role_info['role_abbr']
            if role_abbr in selected_roles:
                scores = []
                total_multiplier = sum(role_info[attr] for attr in role_info if attr not in ['role', 'role_abbr'])

                for _, player in df.iterrows():
                    if selected_division == '-ALL-' or player['Division'] == selected_division:
                        if any(pos in player['Position'] for pos in eligible_positions_goalkeeper) and role_abbr.startswith(("gkd", "skd", "sks", "ska")):
                            total_score = sum(player[attr] * role_info[attr] for attr in role_info if attr not in ['role', 'role_abbr'])
                            normalized_score = total_score / total_multiplier
                            scores.append((player['Name'], player['Age'], player['Position'], player['Club'], player['Division'], player['Height'], player['Weight'], player['Preferred Foot'], normalized_score))
                        elif any(pos in player['Position'] for pos in eligible_positions_defender) and role_abbr.startswith(("bpdd", "bpds", "bpdc", "cdd", "cds", "cdc", "wcbd", "wcbs", "wcba", "ls", "ld", "ncbd", "ncbs", "ncbc")):
                            total_score = sum(player[attr] * role_info[attr] for attr in role_info if attr not in ['role', 'role_abbr'])
                            normalized_score = total_score / total_multiplier
                            scores.append((player['Name'], player['Age'], player['Position'], player['Club'], player['Division'], player['Height'], player['Weight'], player['Preferred Foot'], normalized_score))
                        elif any(pos in player['Position'] for pos in eligible_positions_fullbacks) and role_abbr.startswith(("fbd", "fbs", "fba", "fbau", "nfbd", "wbd", "wbs", "wba", "wbau", "cwbs", "cwba", "iwbd", "iwbs", "iwba", "iwbau", "ifbd")):
                            total_score = sum(player[attr] * role_info[attr] for attr in role_info if attr not in ['role', 'role_abbr'])
                            normalized_score = total_score / total_multiplier
                            scores.append((player['Name'], player['Age'], player['Position'], player['Club'], player['Division'], player['Height'], player['Weight'], player['Preferred Foot'], normalized_score))

                # Sort players by normalized score
                sorted_scores = sorted(scores, key=lambda x: x[8], reverse=True)

                if sorted_scores:
                    top_score = sorted_scores[0][8]
                    
                    top_10_players = []
                    for player in sorted_scores[:10]:
                        score_diff = ((top_score - player[8]) / top_score) * 100 if top_score != 0 else 0
                        top_10_players.append(player + (score_diff,))

                    best_players[role] = top_10_players

    return best_players

def calculate_all_roles_for_players(df, selected_division):
    eligible_positions_goalkeeper = ["GK"]
    eligible_positions_defender = ["D (C)", "D (LC)", "D (RC)", "D (RLC)", "D (L)", "D (R)", "D (RL)", "WB (RL)", "WB (L)", "WB (R)" , "DM"]
    eligible_positions_fullbacks = ["D (LC)", "D (RC)", "D (RLC)", "D (L)", "D (R)", "D (RL)", "WB (RL)", "WB (L)", "WB (R)", "M (L)", "M (R)", "M (RL)"]
    all_players_scores = []

    for _, player in df.iterrows():
        if selected_division == '-ALL-' or player['Division'] == selected_division:
            player_scores = [player['Name'], player['Age'], player['Position'], player['Club'], player['Division'], player['Height'], player['Weight'], player['Preferred Foot']]
            
            for category, roles_info in roles_data.items():
                for role_info in roles_info:
                    role_abbr = role_info['role_abbr']
                    total_multiplier = sum(role_info[attr] for attr in role_info if attr not in ['role', 'role_abbr'])

                    if any(pos in player['Position'] for pos in eligible_positions_goalkeeper) and role_abbr.startswith(("gkd", "skd", "sks", "ska")):
                        total_score = sum(player[attr] * role_info[attr] for attr in role_info if attr not in ['role', 'role_abbr'])
                        normalized_score = total_score / total_multiplier
                        player_scores.append(normalized_score)
                    elif any(pos in player['Position'] for pos in eligible_positions_defender) and role_abbr.startswith(("bpdd", "bpds", "bpdc", "cdd", "cds", "cdc", "wcbd", "wcbs", "wcba", "ls", "ld", "ncbd", "ncbs", "ncbc")):
                        total_score = sum(player[attr] * role_info[attr] for attr in role_info if attr not in ['role', 'role_abbr'])
                        normalized_score = total_score / total_multiplier
                        player_scores.append(normalized_score)
                    elif any(pos in player['Position'] for pos in eligible_positions_fullbacks) and role_abbr.startswith(("fbd", "fbs", "fba", "fbau", "nfbd", "wbd", "wbs", "wba", "wbau", "cwbs", "cwba", "iwbd", "iwbs", "iwba", "iwbau", "ifbd")):
                        total_score = sum(player[attr] * role_info[attr] for attr in role_info if attr not in ['role', 'role_abbr'])
                        normalized_score = total_score / total_multiplier
                        player_scores.append(normalized_score)
                    else:
                        player_scores.append(None)  # Append None if not applicable

            all_players_scores.append(player_scores)

    return all_players_scores

def save_all_players_scores_to_csv(df, roles_info, selected_roles, selected_division):
    for role_info in roles_info:
        role_abbr = role_info['role_abbr']
        if role_abbr in selected_roles:  # Check if the checkbox is ticked
            scores = []
            total_multiplier = sum(role_info[attr] for attr in role_info if attr not in ['role', 'role_abbr'])
            if total_multiplier == 0:
                sg.popup_error(f"Error: Total multiplier for role '{role_info['role']}' is zero. Skipping saving scores for this role.")
                continue
            
            eligible_positions_goalkeeper = ["GK"]
            eligible_positions_defender = ["D (C)", "D (LC)", "D (RC)", "D (RLC)", "D (L)", "D (R)", "D (RL)", "WB (RL)", "WB (L)", "WB (R)", "DM"]
            eligible_positions_fullbacks = ["D (LC)", "D (RC)", "D (RLC)", "D (L)", "D (R)", "D (RL)", "WB (RL)", "WB (L)", "WB (R)", "M (L)", "M (R)", "M (RL)"]

            for _, player in df.iterrows():
                if selected_division == '-ALL-' or player['Division'] == selected_division:
                    if any(pos in player['Position'] for pos in eligible_positions_goalkeeper) and role_abbr.startswith(("gkd", "skd", "sks", "ska")):
                        total_score = sum(player[attr] * role_info[attr] for attr in role_info if attr not in ['role', 'role_abbr'])
                        normalized_score = total_score / total_multiplier
                        scores.append((player['Name'], player['Age'], player['Position'], player['Club'], player['Division'], player['Height'], player['Weight'], player['Preferred Foot'], normalized_score))
                    elif any(pos in player['Position'] for pos in eligible_positions_defender) and role_abbr.startswith(("bpdd", "bpds", "bpdc", "cdd", "cds", "cdc", "wcbd", "wcbs", "wcba", "ls", "ld", "ncbd", "ncbs", "ncbc")):
                        total_score = sum(player[attr] * role_info[attr] for attr in role_info if attr not in ['role', 'role_abbr'])
                        normalized_score = total_score / total_multiplier
                        scores.append((player['Name'], player['Age'], player['Position'], player['Club'], player['Division'], player['Height'], player['Weight'], player['Preferred Foot'], normalized_score))
                    elif any(pos in player['Position'] for pos in eligible_positions_fullbacks) and role_abbr.startswith(("fbd", "fbs", "fba", "fbau", "nfbd", "wbd", "wbs", "wba", "wbau", "cwbs", "cwba", "iwbd", "iwbs", "iwba", "iwbau", "ifbd")):
                        total_score = sum(player[attr] * role_info[attr] for attr in role_info if attr not in ['role', 'role_abbr'])
                        normalized_score = total_score / total_multiplier
                        scores.append((player['Name'], player['Age'], player['Position'], player['Club'], player['Division'], player['Height'], player['Weight'], player['Preferred Foot'], normalized_score))

            # Sort scores by normalized score (index 8) in descending order
            scores_sorted = sorted(scores, key=lambda x: x[8], reverse=True)

            # Generate timestamp for filename
            timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
            file_name = f"{role_abbr.lower()}_{timestamp}.csv"

            # Save to CSV
            with open(file_name, 'w', newline='', encoding='utf-8') as f:
                f.write("Name,Age,Position,Club,Division,Height,Weight,Preferred Foot,Score,Diff to 1st (%)\n")
                top_score = scores_sorted[0][8] if scores_sorted else 0
                for player in scores_sorted:
                    score_diff = ((top_score - player[8]) / top_score) * 100 if top_score != 0 else 0
                    f.write(f"{player[0]},{player[1]},{player[2]},{player[3]},{player[4]},{player[5]},{player[6]},{player[7]},{player[8]:.2f},{score_diff:.2f}\n")  # Format player[8] and score_diff as float with 2 decimal places
            sg.popup(f"Saved {role_info['role']} scores to {file_name}")

def save_all_roles_to_csv(df, all_players_scores, roles_data):
    header = ["Name", "Age", "Position", "Club", "Division", "Height", "Weight", "Preferred Foot"]
    for category, roles_info in roles_data.items():
        for role_info in roles_info:
            header.append(role_info['role_abbr'])
    df_all_players = pd.DataFrame(all_players_scores, columns=header)

    timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    file_name = f"all_roles_scores_{timestamp}.csv"
    df_all_players.to_csv(file_name, index=False)
    sg.popup(f"Saved all players' scores for all roles to {file_name}")

# Event loop
df = None
best_players = None
while True:
    event, values = window.read()
    if event == sg.WINDOW_CLOSED:
        break
    elif event == "Import":
        df = import_html_table()
    elif event == "Calculate Selected":
        if df is not None:
            selected_roles = [role for role, selected in values.items() if selected]
            selected_division = values['division_dropdown']
            best_players = calculate_best_players(df, selected_roles, selected_division)
            display_text = ""
            for role, players in best_players.items():
                display_text += f"{role}:\n"
                display_text += f"{'Name':<25} {'Age':<5} {'Position':<10} {'Club':<25} {'Division':<15} {'Height':<7} {'Weight':<7} {'Preferred Foot':<15} {'Score':<5} {'Diff to 1st (%)':<5}\n"
                display_text += "-" * 140 + "\n"  # Adjusted width to accommodate Position and Diff
                for player in players:
                    display_text += f"{player[0]:<25} {player[1]:<5} {player[2]:<10} {player[3]:<25} {player[4]:<15} {player[5]:<7} {player[6]:<7} {player[7]:<15} {player[8]:.2f} {player[9]:.2f}\n"
                display_text += "\n"
            sg.popup_scrolled("Top 10 Players for Each Role", display_text, size=(100, 30))
    elif event == "Calculate All":
        if df is not None:
            selected_division = values['division_dropdown']
            all_players_scores = calculate_all_roles_for_players(df, selected_division)
            save_all_roles_to_csv(df, all_players_scores, roles_data)
    elif event == "Save":
        if df is not None:
            save_all_players_scores_to_csv(df, [role_info for roles_info in roles_data.values() for role_info in roles_info], 
                                           [role_abbr for role_abbr, selected in values.items() if selected], 
                                           values['division_dropdown'])

window.close()
