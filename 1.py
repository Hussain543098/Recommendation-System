import streamlit as st
import pandas as pd

# Load the data
purchase_data = pd.read_csv("synthetic_medical_purchase_data.csv")
tools_data = pd.read_csv("cleaned_surgical_tools.csv")

# Clean the price column by removing the $ sign and converting to float
tools_data["Price"] = (
    tools_data["Price"].replace({"\$": "", ",": ""}, regex=True).astype(float)
)

# Extract product ID from Title
tools_data["Tool_ID"] = tools_data["Title"].apply(lambda x: x.split(" | ")[-1])

# Keep relevant columns
tools_data = tools_data[["Tool_ID", "Title", "Image", "Price", "Category"]]


# Function to get top 3 recommendations based on user type and budget
def get_recommendations(user_type, user_budget_min, user_budget_max):
    filtered_tools = tools_data[
        (tools_data["Price"] >= user_budget_min)
        & (tools_data["Price"] <= user_budget_max)
    ]
    if user_type != "All":
        filtered_tools = filtered_tools[filtered_tools["Category"] == user_type]

    recommendations = []

    for _, tool in filtered_tools.head(3).iterrows():
        recommendations.append(
            {
                "Tool Name": tool["Title"],
                "Tool ID": tool["Tool_ID"],
                "Price": tool["Price"],
                "Image URL": tool["Image"],
            }
        )

    if not recommendations:
        return "No tools found within the selected criteria."

    return recommendations


# ------------------- Streamlit UI -------------------

st.set_page_config(page_title="Surgical Tool Recommender", layout="centered")
st.title("Budget-based Surgical Tool Recommendation System")

# Sidebar inputs
st.sidebar.header("Filter Criteria")
user_type = st.sidebar.selectbox(
    "Select User Type:",
    [
        "All",
        "Gynecology",
        "Surgical Instruments",
        "Dissecting Forceps",
        "General",
        "Diagnostic Instruments",
        "Dermatology",
    ],
)

min_budget = st.sidebar.number_input("Minimum Budget ($):", min_value=0, value=500)
max_budget = st.sidebar.number_input("Maximum Budget ($):", min_value=0, value=10000)

# Get and display recommendations
if min_budget <= max_budget:
    recommendations = get_recommendations(user_type, min_budget, max_budget)

    if isinstance(recommendations, str):
        st.warning(recommendations)
    else:
        st.subheader("Here are your top 3 recommendations:")

        for rec in recommendations:
            has_image = rec["Image URL"] and rec["Image URL"].lower() != "missing_url"
            html_block = f"""
            <div style="
            background-color: #ffffff;
            padding: 20px;
            margin-bottom: 20px;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
            transition: transform 0.2s ease;
            ">
            <h3 style="margin-bottom: 10px; color: #1f4e79;">🛠️ {rec['Tool Name']}</h3>
            <p style="margin: 6px 0;"><strong>🔢 Product ID:</strong> {rec['Tool ID']}</p>
            <p style="margin: 6px 0;"><strong>💲 Price:</strong> ${rec['Price']:.2f}</p>
            <div style="margin: 15px 0; text-align: center;">
            {"<img src='" + rec['Image URL'] + "' width='220' style='border-radius:8px; border:1px solid #ccc;'>" if has_image else "<div style='font-size:14px; color:#888;'>🚫 No image available</div>"}
            </div>
            </div>
            """

            st.markdown(html_block, unsafe_allow_html=True)
else:
    st.error(
        "Please ensure the minimum budget is less than or equal to the maximum budget."
    )
