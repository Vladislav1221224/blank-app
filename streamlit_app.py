import pandas as pd
import streamlit as st
import os
import re

years = [2018, 2019, 2020, 2021]

general_work_data_yearly = {}
general_education_data_yearly = {}

@st.cache_data
def load_and_process_all_data(folder_path):
    # Перебираємо всі файли в папці з даними
    for file_name in os.listdir(folder_path):
        # Перевірка на відповідність імені файлу
        match = re.match(r"data-(\d{4})\.xls", file_name)
        if match:
            # Визначаємо рік з імені файлу
            year = int(match.group(1))
            file_path = os.path.join(folder_path, file_name)

            # Завантаження та обробка даних
            data = pd.read_excel(file_path, header=None)
            data = data.drop([0, 1], axis=0).reset_index(drop=True)

            # Перевірка кількості стовпців
            if len(data.columns) > 9:
                data = data.iloc[:, :-1]  # Видаляємо останній стовпець

            # Встановлення нового заголовка
            new_header = data.iloc[0]
            data = data[1:]
            data.columns = new_header

            # Створення нових колонок для назви місяців
            months_eng = ["January-March", "January-June", "January-September", "January-December"]
            new_columns = [f"{month} (тыс. осіб)" if i % 2 == 0 else f"{month} (% до робочої сили)"
                           for month in months_eng for i in range(2)]

            # Присвоєння нових колонок
            data.columns = ["Age Group", *new_columns]

            # Спочатку заміняємо NaN значення на порожній рядок
            data.iloc[:, 0] = data.iloc[:, 0].fillna("")

            # Шукаємо потрібні строки
            cache = data[data['Age Group'].str.contains("Усе\s+населення\s+віком\s+15\s+років\s+і\s+старше", na=False)]
            if cache["Age Group"].empty:
                cache = data[data['Age Group'].str.contains("Усе населення у віці 15-70 років", na=False)]

            # Видалення колонки "Age Group"
            cache = cache.drop(columns=["Age Group"], errors="ignore")
            #Перетворення таблиці в потрібний формат (Months, Population, % Workforce)
            cache_melted = pd.DataFrame()
            for i, month in enumerate(months_eng):
                # Вибираємо стовпці з даними для цього місяця
                pop_col = f"{month} (тыс. осіб)"
                workforce_col = f"{month} (% до робочої сили)"

                # Додаємо рядки в новий формат
                temp_df = pd.DataFrame({
                    "Months": [month],
                    "Population": cache[pop_col].values,
                    "% of Workforce": cache[workforce_col].values
                })

                # Додаємо дані в загальний DataFrame
                cache_melted = pd.concat([cache_melted, temp_df], ignore_index=True)

            # Додаємо отримані дані до загальних даних
            general_work_data_yearly[year] = cache_melted

    return general_work_data_yearly

# Шлях до папки з файлами
folder_path = "dataset"
general_work_data_yearly = load_and_process_all_data(folder_path)

# Define the data for education in a dictionary format
general_education_data_yearly = {
    "Year": [2018, 2019, 2020, 2021],
    "Graduates": [55499, 50246, 47342, 261788]
}

# Convert the dictionary to a DataFrame
df_education = pd.DataFrame(general_education_data_yearly)

# Ensure the 'Year' column is treated as integers (to avoid formatting issues)
df_education['Year'] = df_education['Year'].astype(int)

# Prepare Population data for plotting
population_data = []
workforce_data = []
for year in years:
    if year in general_work_data_yearly:
        population_data.append(general_work_data_yearly[year]['Population'].sum())
        workforce_data.append(general_work_data_yearly[year]['% of Workforce'].sum())

# Prepare a new DataFrame for both Graduates and Population for line chart
df_plot = pd.DataFrame({
    'Year': years,
    'Graduates': df_education['Graduates'],
    'Population(in thousands)': population_data,
    '% Workforce': workforce_data
})

# Normalize the data
df_plot['Graduates Normalized'] = (df_plot['Graduates'] - df_plot['Graduates'].min()) / (df_plot['Graduates'].max() - df_plot['Graduates'].min())
df_plot['Population Normalized'] = (df_plot['Population(in thousands)'] - df_plot['Population(in thousands)'].min()) / (df_plot['Population(in thousands)'].max() - df_plot['Population(in thousands)'].min())
df_plot['% Workforce Normalized'] = (df_plot['% Workforce'] - df_plot['% Workforce'].min()) / (df_plot['% Workforce'].max() - df_plot['% Workforce'].min())

# Display the data as a table in Streamlit
st.write("Загальні дані випускників та населення за роками (2018-2021) та нормалізовані дані:")
st.dataframe(df_plot)

# Plotting the graphs using st.line_chart
st.write("Графіки випускників, населення та нормалізованих даних за роками:")
st.line_chart(df_plot.set_index('Year'))
