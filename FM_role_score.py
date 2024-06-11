import PySimpleGUI as sg
import json
import pandas as pd

sg.theme('DarkAmber')

# Load roles from the JSON file
try:
    with open('player_roles.json', 'r') as file:
        roles_data = json.load(file)
except FileNotFoundError:
    print("Error: The file 'player_roles.json' was not found.")
except json.JSONDecodeError:
    print("Error: The file 'player_roles.json' is not a valid JSON.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
    roles_data = json.load(file)

# Create layout for the left side (checkboxes)
left_layout = []
for category, roles in roles_data.items():
    left_layout.append([sg.Text(category, font=("Arial", 12, "bold"))])
    for role in roles:
        left_layout.append([sg.Checkbox(role['role'], key=role['role_abbr'])])

# Create a scrollable column for the left side (roles)
left_column = sg.Column(left_layout, scrollable=True, vertical_scroll_only=True, size=(250, 400))

# Create layout for the right side (buttons)
right_layout = [
    [sg.Button("Import", size=(15, 2), font=("Arial", 12))],
    [sg.Button("Calculate", size=(15, 2), font=("Arial", 12))],
    [sg.Button("Save", size=(15, 2), font=("Arial", 12))]
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
                if column not in ["Inf", "Rec", "Name", "Nat", "Club", "Position", "Preferred Foot", "Height", "Weight"]:
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

            sg.popup('Table Imported and Transformed')
            print(df)  # You can add further processing here
        else:
            sg.popup('No tables found in the HTML file.')

# Event loop
while True:
    event, values = window.read()
    if event == sg.WINDOW_CLOSED:
        break
    elif event == "Import":
        import_html_table()
    elif event in ["Calculate", "Save"]:
        print(f"{event} pressed")

window.close()