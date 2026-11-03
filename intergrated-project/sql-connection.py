import pandas as pd
from sqlalchemy import create_engine, text

# Create database engine
engine = create_engine('sqlite:///Maji_Ndogo_farm_survey_small.db')

# View available tables
with engine.connect() as connection:
    result = connection.execute(text("SELECT name FROM sqlite_master WHERE type='table';"))
    for row in result:
        print(row)

# Query to join all relevant features
sql_query = """
SELECT *
FROM geographic_features
JOIN weather_features USING (Field_ID)
JOIN soil_and_crop_features USING (Field_ID)
JOIN farm_management_features USING (Field_ID)
"""

# Load the combined data into a DataFrame
with engine.connect() as connection:
    MD_agric_df = pd.read_sql_query(text(sql_query), connection)

MD_agric_df

# Drop the redundant ID column
MD_agric_df.drop(columns='Field_ID', inplace=True)

# Fix swapped column names
MD_agric_df.rename(columns={'Annual_yield': 'Crop_type_Temp', 'Crop_type': 'Annual_yield'}, inplace=True)
MD_agric_df.rename(columns={'Crop_type_Temp': 'Crop_type'}, inplace=True)

# Correct negative elevation values
MD_agric_df['Elevation'] = MD_agric_df['Elevation'].abs()

# Clean crop type names
def correct_crop_type(crop):
    crop = crop.strip()
    corrections = {
        'cassaval': 'cassava',
        'wheatn': 'wheat',
        'teaa': 'tea'
    }
    return corrections.get(crop, crop)

MD_agric_df['Crop_type'] = MD_agric_df['Crop_type'].apply(correct_crop_type)

len(MD_agric_df['Crop_type'].unique())

MD_agric_df['Elevation'].min()

MD_agric_df['Annual_yield'].dtype

def explore_crop_distribution(df, crop_filter):
    filtered_df = df[df['Crop_type'] == crop_filter]
    return filtered_df['Rainfall'].mean(), filtered_df['Elevation'].mean()

explore_crop_distribution(MD_agric_df, "tea")

explore_crop_distribution(MD_agric_df, "wheat")

def analyse_soil_fertility(df):
    return df.groupby('Soil_type')['Soil_fertility'].mean()

analyse_soil_fertility(MD_agric_df)

### START FUNCTION
def climate_geography_influence(df,column):
    return df.groupby([column]).agg({'Elevation': 'mean', 'Min_temperature_C': 'mean', 'Max_temperature_C': 'mean', 'Rainfall': 'mean'})
### END FUNCTION

climate_geography_influence(MD_agric_df, 'Crop_type')

grouped_df = MD_agric_df.groupby("Soil_type").mean(numeric_only = True).sort_values(by="Elevation",ascending=False)
print(grouped_df.index[0])
grouped_df

### START FUNCTION
def find_ideal_fields(df):
    mean_yield = df['Standard_yield'].mean()
    filtered_df = df[(df['Standard_yield'] > mean_yield)]
    return filtered_df.groupby("Crop_type").count().sort_values(by="Standard_yield", ascending = False).index[0]
### END FUNCTION

type(find_ideal_fields(MD_agric_df))

def find_good_conditions(df, crop_type):
    filtered_df = df[
        (df['Crop_type'] == crop_type) &
        (df['Standard_yield'] > df['Standard_yield'].mean()) &
        (df['Ave_temps'].between(12, 15)) &
        (df['Pollution_level'] < 0.0001)
    ]
    return filtered_df

find_good_conditions(MD_agric_df, "tea").shape

MD_agric_df.query('Standard_yield > 0.5 and Soil_type == "Loamy"')

MD_agric_df[(MD_agric_df['Standard_yield'] > 0.5) & (MD_agric_df['Soil_type'] == 'Loamy')]

soil_types = ['Loamy', 'Sandy', 'Silt']

MD_agric_df.query('Soil_type in @soil_types')

MD_agric_df.groupby('Crop_type')['Standard_yield'].mean().plot(kind='bar')

MD_agric_df['Standard_yield'].plot(kind='hist', bins =20)

MD_agric_df.plot(kind='scatter', x = "Pollution_level", y = "Standard_yield" )
