import pandas as pd
from sqlalchemy import create_engine, text

# Create database engine
engine = create_engine('sqlite:///Maji_Ndogo_farm_survey_small.db')
