import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu
import os

pwd = os.getcwd()

st.set_page_config(
    page_title='Import Data to S3 Bucket', 
    page_icon=':bar_chart:', 
    layout='wide')



### SET UP PAGES ###
# import the pages

# main_page = st.Page(
#     rf'{pwd}/app_pages/main.py',
#     title='Main Page'
# )

econ_page = st.Page(
    rf'{pwd}/app_pages/econ.py',
    title='Econ Upload Page'
)

tsic_egat_page = st.Page(
    rf'{pwd}/app_pages/tsic_egat.py',
    title='TSIC EGAT Upload Page'
)

tsic_mea_page = st.Page(
    rf'{pwd}/app_pages/tsic_mea.py',
    title='TSIC MEA Upload Page'
)

tsic_pea_page = st.Page(
    rf'{pwd}/app_pages/tsic_pea.py',
    title='TSIC PEA Upload Page'
)

### ------------------ ###
# create a navigation
# page_order = [
#     #main_page,
#     econ_page,
#     tsic_egat_page,
#     tsic_mea_page,
#     tsic_pea_page
# ]

# add subdirectories of the page
page_order = {
    #'Main Page': page_order,
    'Econ': [econ_page],
    'TSIC': [tsic_egat_page, tsic_mea_page,  tsic_pea_page]
}

##st.sidebar.selectbox('Menu', list(page_order.keys()))
# selected_page = st.navigation(page_order)
# selected_page.run()

##menu = st.sidebar.radio('Menu', list(page_order.keys()))
##menu = ['Economic', 'TSIC'] 
with st.sidebar:
    selected = option_menu('Electricity Demand', ['Econ', 'TSIC'],
                           icons=['🏠', '📈', '📊', '📉', '📈', '📊'], menu_icon="cast", default_index=0,
                           styles={
                                "container": {"padding": "5px", "background-color": "#fff"},
                                "icon": {"color": "orange", "font-size": "25px"},
                                "nav-link": {
                                    "font-size": "16px",
                                    "text-align": "left",
                                    "margin": "0px",
                                    "color": "black",
                                    "background-color": "#ffedcc",
                                    "--hover-color": "#ffd699"
                                },
                                "nav-link-selected": {"background-color": "orange", "color": "white"},
        })
# with st.sidebar:
#     selected = option_menu('Electricity Supply', ['Distribution Loss'],
#                            icons=['🏠', '📈', '📊', '📉', '📈', '📊'], menu_icon="cast", default_index=0)
if selected == 'Econ':
    #with st.sidebar:
    selected = option_menu('', ['Economic Index'],
                           icons=[ '📈', '📈', '📈'], default_index=0, orientation="vertical")
    if selected == 'Economic Index':
        st.navigation([econ_page]).run()

elif selected == 'TSIC':
    with st.sidebar:
        selected = option_menu('', ['EGAT', 'MEA', 'PEA'],
                           icons=[ '📈', '📈', '📈'], default_index=0, orientation="vertical")
    if selected == 'EGAT':
        st.navigation([tsic_egat_page]).run()
    elif selected == 'MEA':
        st.navigation([tsic_mea_page]).run()
    elif selected == 'PEA':
        st.navigation([tsic_pea_page]).run()
        
with st.sidebar:
    selected = option_menu('Electricity Supply', ['Distribution Loss'],
                           icons=['🏠', '📈', '📊', '📉', '📈', '📊'], menu_icon="cast", default_index=0)