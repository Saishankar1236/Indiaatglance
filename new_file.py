import streamlit as st 
import plotly.express as px 
import geopandas as gpd 
import pandas as pd 
import folium
import json
from folium import Choropleth , GeoJsonTooltip
import plotly.graph_objects as go
from streamlit_folium import folium_static

st.title("India at a glance")
st.header("Please select the state which you want to know more")


df_states_locations = pd.read_excel(r"Indian_States_UTs_Lat_Long.xlsx")
df_descriptions = pd.read_excel(r"India_States_Descriptions_Complete.xlsx")

selected_state= st.selectbox("Select state" , options=["Select a State"]+ df_states_locations['State/UT'].tolist())

st.subheader(selected_state , divider="orange")

if selected_state!="Select a State":
    description = df_descriptions[df_descriptions['State/UT']==selected_state]['Description'].iloc[0]
    st.write(description)
else:
    st.info("Please select any one state of your choice.")

data_df = pd.read_csv(r"tourist_across_different_states.csv")



metric_field = st.selectbox("Select field to see:", ["2021 Domestic","2021 Foreign","2022 Domestic","2022 Foreign"])


def get_state_center(state_name):
    return [float(df_states_locations[df_states_locations['State/UT'].str.strip().str.lower()==state_name.strip().lower()]['Latitude (°N)'].iloc[0]),float(df_states_locations[df_states_locations['State/UT'].str.strip().str.lower()==state_name.strip().lower()]['Longitude (°E)'].iloc[0])]

if selected_state!="Select a State":
    m = folium.Map(location=get_state_center(selected_state) , zoom_start=6)
else: 
    m = folium.Map(location=[22.9734, 78.6569], zoom_start=4.5)

with open("in.json","r", encoding="utf-8") as f:
    geojson_data = json.load(f)

data_dict = data_df.set_index("States/UTs").to_dict(orient="index")
for feature in geojson_data["features"]:
    state_name = feature["properties"]["name"]
    state_data = data_dict.get(state_name, {})
    for col in ["2021 Domestic","2021 Foreign","2022 Domestic","2022 Foreign"]:
        feature["properties"][col] = state_data.get(col, "No data")

folium.Choropleth(
    geo_data=geojson_data,
    data=data_df,
    columns=["States/UTs", metric_field],
    key_on="feature.properties.name",
    fill_color="YlGn",
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name=f"{metric_field}"
).add_to(m)

field_alias = {"2021 Domestic" : "2021 Domestic(in lakhs):","2021 Foreign" : "2021 Foreign(in lakhs):","2022 Domestic":"2022 Domestic(in lakhs):","2022 Foreign":"2022 Foreign(in lakhs):"}

tooltip = GeoJsonTooltip(
    fields=["name"] + [metric_field],
    aliases=["State:"]+[field_alias[metric_field]],
    sticky=True,
    labels=True
)

folium.GeoJson(
    geojson_data,
    style_function=lambda x: {'fillColor': 'transparent', 'color': 'transparent', 'weight': 0},
    tooltip=tooltip
).add_to(m)

folium_static(m)

if selected_state!="Select a State":
    st.markdown(f"The map shows the {selected_state} {metric_field}  tourist visits(in lakhs)")
else:
    st.markdown(f"The map shows the India {metric_field}  tourist visits(in lakhs)")

all_states = data_df['States/UTs'].tolist()

st.header("Different stats State-wise")

select_all= st.checkbox("Select all States" , value=True)

y_metrics = st.multiselect("Select Y-axis metrics", options=["2021 Domestic","2021 Foreign","2022 Domestic","2022 Foreign","Growth Rate DTV 22/21" ,"Growth Rate FTV 22/21" ,"% Share 2022 DTV" ,"% Share 2022 FTV"], default=["2021 Domestic"])
if select_all:
    mutiple_states = st.multiselect("Select Multiple States" , options =all_states , default=all_states , disabled=True )
else: 
    mutiple_states= st.multiselect("Select Multiple States" , options =all_states)


filtered_df = data_df[data_df['States/UTs'].isin(mutiple_states)]


for y in y_metrics:
    st.subheader(f"{y} by States/UTs(tourism)")
    fig = px.bar(
        filtered_df,
        x='States/UTs',
        y=y,
        color='States/UTs',
        barmode='group',
        title=f"{y} by {'States/UTs'} ({', '.join(mutiple_states)})"
    )
    st.plotly_chart(fig, use_container_width=True)







