import streamlit as st
import pandas as pd

# Load data
data = pd.read_csv("life-expectancy.csv")
alcohol_data = pd.read_csv("alcohol-consumption.csv")
alcohol_data["Year"] = alcohol_data["Year"].astype(int)
alcohol_data["Alcohol Consumption"] = alcohol_data["Alcohol Consumption"].astype(float)

# Set up Streamlit app
st.title("Life Expectancy and Alcohol Consumption Analysis")
st.write("This app allows you to explore life expectancy trends and alcohol consumption by country.")

# Life Expectancy Analysis
st.header("Life Expectancy Over Time by Country")

# Filter countries for selection in the sidebar
countries = data['Entity'].unique()
selected_countries = st.sidebar.multiselect("Select countries to display", countries, default=["Afghanistan", "Albania"])

# Select year range
min_year, max_year = int(data["Year"].min()), int(data["Year"].max())
year_range = st.sidebar.slider("Select year range for life expectancy", min_year, max_year, (min_year, max_year),step=5)

# Filter data based on selections
filtered_data = data[(data["Entity"].isin(selected_countries)) & 
                     (data["Year"] >= year_range[0]) & 
                     (data["Year"] <= year_range[1])]

filtered_countries_data = filtered_data[filtered_data["Entity"].isin(selected_countries)]

# Pivot the data to have countries as columns and years as the index
pivot_data = filtered_countries_data.pivot_table(
    index='Year', 
    columns='Entity', 
    values="Period life expectancy at birth - Sex: all - Age: 0"
)
# Plot the data using Streamlit's line_chart function
st.line_chart(pivot_data)

# Get unique years from the data and sort them
available_years = sorted(alcohol_data["Year"].unique())

# Use select_slider to limit choices to available years
selected_year = st.sidebar.select_slider("Select year for alcohol consumption", options=available_years)

# Filter data for the selected year
yearly_alcohol_data = alcohol_data[alcohol_data["Year"] == selected_year]

# Display the filtered data
st.dataframe(yearly_alcohol_data)
top_n = st.sidebar.slider("Select number of top countries", 1, 50, 10)

# Alcohol Consumption Analysis
st.header(f"Top {top_n} Countries by Alcohol Consumption for {selected_year} year")

st.dataframe(alcohol_data["Year"])
st.write(selected_year)
# Filter alcohol data for the selected year
yearly_alcohol_data = alcohol_data[(alcohol_data["Year"] == selected_year)]

# Display the filtered data
st.dataframe(yearly_alcohol_data)

filtered_countries_data = filtered_data[filtered_data["Entity"].isin(selected_countries)]

# Top N countries by alcohol consumption
top_n_alcohol = yearly_alcohol_data.nlargest(top_n, 'Alcohol Consumption').copy()
top_n_alcohol['Alcohol Consumption'] = top_n_alcohol['Alcohol Consumption'].astype(float)

top_n_alcohol = top_n_alcohol.sort_values(by="Alcohol Consumption",ascending=False)
# Rank countries and set as index
top_n_alcohol["Ranked Country"] = [f"{i+1}. {country}" for i, country in enumerate(top_n_alcohol["Entity"])]
top_n_alcohol.set_index("Ranked Country", inplace=True)
st.dataframe(top_n_alcohol['Alcohol Consumption'])
# Display the bar chart with ranked countries
st.header(f'Top {top_n} Countries by Alcohol Consumption (Liters per Capita)')
st.bar_chart(top_n_alcohol['Alcohol Consumption'], y_label='Liters of Alcohol')
