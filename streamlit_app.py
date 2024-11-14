import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


#datas
#https://ourworldindata.org/alcohol-consumption
#https://ourworldindata.org/life-expectancy
# Load data
data = pd.read_csv("life-expectancy.csv")
alcohol_data = pd.read_csv("alcohol-consumption.csv")

# Ensure Year is an integer and Alcohol Consumption is a float
alcohol_data["Year"] = alcohol_data["Year"].astype(int)
alcohol_data["Alcohol Consumption"] = alcohol_data["Alcohol Consumption"].astype(float)

# Set up Streamlit app
st.title("Life Expectancy and Alcohol Consumption Analysis")
st.write("This app allows you to explore life expectancy trends and alcohol consumption by country.")

# Filter countries for selection in the sidebar
countries = data['Entity'].unique()
selected_countries = st.sidebar.multiselect(
    "Select countries to display in overall analysis", countries, default=["Afghanistan", "Albania"])

# Select year range
min_year, max_year = int(data["Year"].min()), int(data["Year"].max())
year_range = st.sidebar.slider(
    "Select year range for life expectancy", min_year, max_year, (min_year, max_year), step=5)

# Filter data based on selections
filtered_data = data[(data["Entity"].isin(selected_countries)) & 
                     (data["Year"] >= year_range[0]) & 
                     (data["Year"] <= year_range[1])]

# Rename column for clarity
filtered_data = filtered_data.rename(columns={
    "Period life expectancy at birth - Sex: all - Age: 0": "Life Expectancy"
})

# Plot the data using Plotly Express
st.header("Life Expectancy Over Time by Country")
fig_life_expectancy = px.line(
    filtered_data,
    x="Year",
    y="Life Expectancy",
    color="Entity",
    title="Life Expectancy Over Time",
    labels={"Life Expectancy": "Life Expectancy (Years)", "Entity": "Country"}
)
st.plotly_chart(fig_life_expectancy)

# Alcohol Consumption Analysis for Selected Year
available_years = sorted(alcohol_data["Year"].unique())
selected_year = st.sidebar.select_slider("Select year for alcohol consumption analysis", options=available_years)
top_n = st.sidebar.slider("Select number of top countries", 1, 50, 10)

# Filter alcohol data for the selected year
yearly_alcohol_data = alcohol_data[alcohol_data["Year"] == selected_year]
top_n_alcohol = yearly_alcohol_data.nlargest(top_n, 'Alcohol Consumption').copy()
top_n_alcohol = top_n_alcohol.sort_values(by="Alcohol Consumption", ascending=False)
top_n_alcohol["Ranked Country"] = [f"{i+1}. {country}" for i, country in enumerate(top_n_alcohol["Entity"])]

# Create Plotly bar chart for Top N Alcohol Consumption
fig_alcohol = px.bar(
    top_n_alcohol,
    x="Ranked Country",
    y="Alcohol Consumption",
    labels={"Alcohol Consumption": "Liters of Alcohol", "Ranked Country": "Country (Ranked)"},
    title=f"Top {top_n} Countries by Alcohol Consumption (Liters per Capita)"
)
st.plotly_chart(fig_alcohol)

# Detailed Analysis for a Single Country
selected_country = st.selectbox("Choose a country for detailed analysis", countries)
country_life_data = data[data["Entity"] == selected_country]
country_alcohol_data = alcohol_data[alcohol_data["Entity"] == selected_country]

# Merge data on the "Year" column to align the two datasets for the selected country
merged_data = pd.merge(country_life_data, country_alcohol_data, on=["Entity", "Year"], how="inner")
merged_data = merged_data.rename(columns={
    "Period life expectancy at birth - Sex: all - Age: 0": "Life Expectancy",
    "Alcohol Consumption": "Alcohol Consumption (Liters per Capita)"
})

# Plot combined graph with two y-axes
fig_combined = go.Figure()

# Add Life Expectancy trace
fig_combined.add_trace(
    go.Scatter(
        x=merged_data["Year"],
        y=merged_data["Life Expectancy"],
        mode="lines+markers",
        name="Life Expectancy",
        line=dict(color="blue"),
        yaxis="y1"
    )
)

# Add Alcohol Consumption trace
fig_combined.add_trace(
    go.Scatter(
        x=merged_data["Year"],
        y=merged_data["Alcohol Consumption (Liters per Capita)"],
        mode="lines+markers",
        name="Alcohol Consumption (Liters per Capita)",
        line=dict(color="red"),
        yaxis="y2"
    )
)

# Update layout to add two y-axes
fig_combined.update_layout(
    title=f"Life Expectancy and Alcohol Consumption Over Time in {selected_country}",
    xaxis=dict(title="Year"),
    yaxis=dict(
        title="Life Expectancy",
        titlefont=dict(color="blue"),
        tickfont=dict(color="blue")
    ),
    yaxis2=dict(
        title="Alcohol Consumption (Liters per Capita)",
        titlefont=dict(color="red"),
        tickfont=dict(color="red"),
        overlaying="y",
        side="right"
    ),
    legend=dict(x=0.1, y=1.1)
)

# Display the combined plot in Streamlit
st.plotly_chart(fig_combined)
