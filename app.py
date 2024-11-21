import streamlit as st
import subprocess
import datetime


def run_script(script_path, user_id):
    p = subprocess.Popen(["python", script_path, user_id], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    return out.decode('utf-8')

st.title("Woodside Int Reports Scripts")

# Dictionary to map employee names to user IDs
employee_ids = {
    "Liz": "W67224",
    "Ryan": "W67272",
    "Edward": "W66759",
    "Paul": "W93908"
}

# Map script names to descriptions
script_legend = {
    "int041": "DWGM Settled Price (Delayed)",
    "int131": "DWGM Bid Stack Data",
    "int235": "DWGM Scheduled System Total",
    "int151": "Woodside DWGM's Scheduled Quantity",
    "int037b": "DWGM IntraDay Price Sensitivity",
    "actualflowstorage": "Actual Flow and Storage from Gas Bulletin Board"
}

# Display legend table in the sidebar explaining each script purpose
st.sidebar.title("Legend")
for script_name, description in script_legend.items():
    st.sidebar.write(f"{script_name} - {description}")

# Dropdown for selecting employee name
selected_employee = st.selectbox("Select Employee Name:", list(employee_ids.keys()))

# Get the corresponding user ID based on the selected employee
user_id = employee_ids[selected_employee]


# Define paths to your Python scripts
script1 = f"C:/Users/{user_id}/Woodside Energy Ltd/East Coast Domestic Gas Team - Documents/Analysis/Automations/int041_python_script.py"
script2 = f"C:/Users/{user_id}/Woodside Energy Ltd/East Coast Domestic Gas Team - Documents/Analysis/Automations/int131_python_script.py"
script3 = f"C:/Users/{user_id}/Woodside Energy Ltd/East Coast Domestic Gas Team - Documents/Analysis/Automations/int235_extract_clean.py"
script4 = f"C:/Users/{user_id}/Woodside Energy Ltd/East Coast Domestic Gas Team - Documents/Analysis/Automations/int037b_python_script.py"
script5 = f"C:/Users/{user_id}/Woodside Energy Ltd/East Coast Domestic Gas Team - Documents/Analysis/Automations/private/int151_python_script.py"
script6 = f"C:/Users/{user_id}/Woodside Energy Ltd/East Coast Domestic Gas Team - Documents/Analysis/Automations/actual_flow_storage_python.py"

script_paths = [script1, script2, script3, script4, script5, script6]

if st.button("**Run All Reports Scripts**"):
    for i, script_path in enumerate(script_paths):
        script_name = script_path.split('/')[-1].split('_')[0]

        st.write(f"Running {script_name} script...")

        # Run the script with user input
        script_output = run_script(script_path, user_id)

        st.success(f"Script {script_name} finished running successfully.")
        st.text_area(f"Output {i+1}:", script_output, height=400)  # Add a unique key argument

st.markdown("**Daily Reports**")
for script_path in script_paths:
    script_name = script_path.split('/')[-1].split('_')[0]
    if script_name in ["int131", "int235", "int041", "actual_flow_storage"]:
        button_key = f"Run_{script_name}_reports_script"
        if st.button(f"Run {script_name} reports script", key=button_key):
            st.write(f"Running {script_name} script...")

            # Run the script with user input
            script_output = run_script(script_path, user_id)

            st.success(f"Script {script_name} finished running successfully.")
            st.text_area("Output:", script_output, height=400)

# Define the script information for script6
script6_name = "actual_flow_storage"
script6_description = script_legend.get("actualflowstorage")

# Display information for script6 in the Daily Reports section
st.write(f"**{script6_name}** - {script6_description}:")
button_key = f"Run_{script6_name}_reports_script"
if st.button(f"Run {script6_name} reports script", key=button_key):
    st.write(f"Running {script6_name} script...")

    # Run the script with user input
    script_output = run_script(script6, user_id)

    st.success(f"Script {script6_name} finished running successfully.")
    st.text_area("Output:", script_output, height=400)

st.markdown("**Intra-Day Reports**")
for script_path in script_paths:
    script_name = script_path.split('/')[-1].split('_')[0]
    if script_name in ["int151", "int037b"]:
        button_key = f"Run_{script_name}_reports_script"
        if st.button(f"Run {script_name} reports script", key=button_key):
            st.write(f"Running {script_name} script...")

            # Run the script with user input
            script_output = run_script(script_path, user_id)

            st.success(f"Script {script_name} finished running successfully.")
            st.text_area("Output:", script_output, height=400)  # Adjust the height as needed
