import PySimpleGUI as sg
import pandas as pd

sg.theme('DarkAmber')

# Possible roles in FM24
checkbox_items = {
    "Goalkeepers": ["gk_defend", "skd_defend", "sks_support", "ska_attack"],
    "Central Defenders": [
        "bpdd_defend", "bpds_stopper", "bpdc_cover", "cdd_defend",
        "cds_stopper", "cdc_cover", "wcbd_defend", "wcbs_support",
        "wcba_attack", "ls_support", "la_attack", "ncbd_defend",
        "ncbs_stopper", "ncbc_cover"
    ],
    "Full Backs": [
        "fbd_defend", "fbs_support", "fba_attack", "fbau_automatic",
        "nfbd_defend", "wbd_defend", "wbs_support", "wba_attack",
        "wbau_automatic", "cwbs_support", "cwba_attack", "iwbd_defend",
        "iwbs_support", "iwba_attack", "iwbau_automatic"
    ],
    "Midfielders": [
        "bwmd_defend", "bwms_support", "ad_defend", "hbd_defend",
        "rps_support", "regs_support"
    ]
}

# Create layout for the left side (checkboxes)
left_layout = []
for category, items in checkbox_items.items():
    left_layout.append([sg.Text(category, font=("Arial", 12, "bold"))])
    for item in items:
        left_layout.append([sg.Checkbox(item, key=item)])

# Create a scrollable column for the left side (roles)
left_column = sg.Column(left_layout, scrollable=True, vertical_scroll_only=True, size=(150, 400))

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
window = sg.Window("FM Position Score", layout)

def import_html_table():
    file_path = sg.popup_get_file('Choose an HTML file', file_types=(("HTML Files", "*.html"),))
    if file_path:
        tables = pd.read_html(file_path, encoding='utf-8')
        if tables:
            df = tables[0]
            
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