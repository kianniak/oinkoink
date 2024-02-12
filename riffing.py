#riff
import pandas as pd
import numpy as np
import streamlit as st
import math
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from streamlit_echarts import st_echarts
import Levenshtein
from streamlit_option_menu import option_menu
from streamlit_server_state import server_state, server_state_lock
import streamlit_shadcn_ui as ui
from utils import display_columns, get_filtered_data, load_data, calculate_stats, calculate_metrics, SDG_Impact_Alignment, calculate_country_metrics, selected_score, create_radar_chart, create_strip_plot, generate_chart, create_company_selectbox, create_gauge_options, create_sdg_chart, sdg_expander, find_closest_match, plot_choropleth, plot_bar_chart, filter_dataframe

st.set_page_config(page_title="Oracle Partnerships with Purpose Tool", page_icon="🔍", layout="wide", initial_sidebar_state="expanded")
df = load_data('oraclecomb.csv')

##function for IntroPage Text Wall
def intro_page():
    col1 , col2 = st.columns(2)
    with col1:
        st.subheader("Oracle Tool: Introduction")
        st.markdown(f'###### Welcome! :wave:')
        st.markdown('This Tool has been designed to assist Oracle in Filtering through potential corporate partners.\n\n'
                'It contains over 6,000 companies and assesses them based on our 4 C Framework represented by the **Oracle Score** and its subcomponents the, **Culture Score**, **Capactiy Score**, **Conduct Score**, and **Collaboration Score**.')
        st.divider()
        st.subheader('Things to Note')
        st.markdown('Please note that navigating between pages will reset the view while navigating between tabs will keep the filters intact. If an error occurs it is likely interaction between different sections filters. Please reset filters and try again.\n\n'
                '**To better Understand terminology, data sources and calcultations, please refer to the additional tabs above this page**. This will give you a better understanding of key concepts such as the Sustainable Development Goals (SDGS), B Corp Methodology, Culture Indicators & Financial Metrics used and how we calculate our Oracle Score and its subcomponents. \n\n')
        st.markdown('Further information on calculations, datasources and our freely shared code can be found on our Github. We are working to completely automate the collection and cleaning of data consistently and will update Oracle when we hit this milestone')
    with col2:
        st.subheader('Navigation')
        st.markdown(f'###### Where do you want to go? :wave:')

        st.markdown('The page has two main sections: **Oracle Score Dashboard** :bar_chart: :mag:, **Deep Dive on a Company** :factory::eyes:\n\n'
                '**Aggregate Data** :bar_chart: :mag: Consists of three embedded tabs. In this section you can filter the database based on a number of different criteria. Data will automatically update as you adjust the filter values. This section also contains a number of charts and statistics to help you understand the data distribution breaking down the Oracle Score in to its subcomponents. Further tabs allow us to look at sub-components. This page is useful for giving users a well rounded view of the universe!\n\n'
                
                '**Company Deep Dive** :factory::eyes: The page allows us to select a company from the dropdown and see a detailed overview of the company including performance on our 4Cs framework. Users can assess a Company performance across scores relative to a selected peer or the median of the universe. Lastly, users are shown a visual of company contribution to SDGs. This page is useful for understanding why a Company is rated as they are, what they might have in common with Oracle and is a launchpad to further research. \n\n'
            
                '**To Get Started** :page_facing_up: Use the **sidebar** on the left of the page to start exploring.')
    st.divider()


def aggframe(): 
    st.subheader("Oracle Score Dashboard")
    col1, col2, = st.columns([0.1, 0.9])
    with col1:
        st.markdown('Filters')
    with col2:
        st.caption('Use the Filters Below to Dynamically Narrow the Data Universe of Companies')
    filtered_data = get_filtered_data(df)
    st.session_state['filtered_data'] = filtered_data
    stats = calculate_stats(df, filtered_data, selected_score)
    st.markdown('Stats for Current Filtered Universe')  
    col1 , col2, col3, col4 = st.columns(4)
    stats = calculate_stats(df, filtered_data, selected_score)
    col1.metric(label="Total Companies", value=f"{stats['total_filtered_companies']:,}")
    col2.metric(label="UK Companies", value=f"{stats['total_filtered_uk_companies']:,}")
    col3.metric(label="Highest Oracle Score", value="{:.2f}".format(stats['highest_oracle_score']))
    col4.metric(label="Median Oracle Score", value="{:.2f}".format(stats['median_oracle_score']))
    col1, col2 = st.columns([0.1, 0.9])
    with col1:
        st.markdown('Filtered Table')
    with col2:
        st.caption('This table will dynamically update based where you set the sidebar filters. At startup it will show all companies in our analysis')
    filtered_df = filtered_data.sort_values(by='Oracle Score', ascending=False)
    st.data_editor(filtered_df, use_container_width=True, hide_index=True)
    csv = filtered_df.to_csv(index=False)
    st.download_button(
        label="Download Filtered data as CSV",
        data=csv,  # 'csv' is the CSV file data
        file_name='oraclecombfiltered.csv',
        mime='text/csv',
    )
def analysis1():
    filtered_data = st.session_state['filtered_data']
    st.subheader('Select a Score Category to See its Distribution and the Top 5 Best Performing Companies')
    score_columns = ['Oracle Score', 'Culture Score', 'Capacity Score', 'Conduct Score', 'Collaboration Score']
    selected_score = st.selectbox('Click To Select Score Category', score_columns)
    stats = calculate_stats(df, filtered_data, selected_score)
    st.markdown(f'Top 5 Companies for {selected_score}')
    st.caption(f'These are the Top 5 Companies on the {selected_score}. The arrow shows the distance from the median score value.')
    st.caption('Note: Sub-Components are Normalized between 0 and 100. The Oracle Score is a weighted average of these Normalized Scores. This is to enable comparision among disparate but methodologically similar calculations between datasets')
    filtered_data = st.session_state['filtered_data']
    top_5_companies = filtered_data.nlargest(5, selected_score)
    cols = st.columns(5) 
    for i, row in enumerate(top_5_companies.iterrows()):
        label = f"{row[1]['Company']}"  
        value = row[1][selected_score] 
        cols[i].metric(label=label, value="{:.2f}".format(value), delta = "{:.2f}".format(value - df[selected_score].median()))
    num_of_columns = 5
    for j in range(len(top_5_companies), num_of_columns):
        cols[j].empty()
    st.divider()
    st.markdown(f'Mean, Median and Highest Score on {selected_score}')
    metrics = df[selected_score].describe()
    col1, col2, col3= st.columns(3)
    with col1:
        st.metric(label="Median", value=f"{metrics['50%']:.2f}", delta ="None", delta_color="off")
    with col2:
        st.metric(label="Mean", value=f"{metrics['mean']:.2f}", delta =f"{metrics['mean'] - metrics['50%']:.2f}")
    with col3:
        st.metric(label="Highest Score", value=f"{metrics['max']:.2f}", delta =f"{metrics['max'] - metrics['50%']:.2f}")
    st.subheader('Swarm Chart of Filtered Metrics')
    st.markdown(f'This chart shows the distribution of scores for the {selected_score}.  Each industry type is colour coded. Hover over a value for more information including company name')          
    with st.expander('Click To Expand For More Information About Swarm Charts'):
            st.markdown('Swarm Charts are often used to display distribution on metrics.\n\n'
            'For example, in a business context, a swarm chart could display customer ratings for different products. Each dot represents a customer rating, and a dense cluster of dots at a high rating level indicates a well-received product.\n\n'
            'In our Case they show how companies by industry perform across our 4 Cs and the Oracle Score.\n\n'
            'Swarm charts can quickly highlight patterns in the distribution of scores. This makes them useful for understanding how the scores are distributed which assists in helping us get a feel for the general feel of the distribtution while clearly marking out potential outliers')
    swarm_plot = create_strip_plot(filtered_data, selected_score)
    st.plotly_chart(swarm_plot)
    st.divider()
    st.subheader(f"{selected_score} and Components by Industry")
    calculate_metrics(df, selected_score)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.text('Highest Industry (by median):')
        st.markdown(f'##### {highest_industry}')    
    with col2:        
        st.text('Lowest Industry (by median):')
        st.markdown(f'##### {lowest_industry}')    
    with col3:
        st.text('Highest Company:')
        st.markdown(f'##### {highest_company}')    
    with col4:
        st.text('Lowest Company:')
        st.markdown(f'##### {lowest_company}')
    st.markdown(f'This chart shows the Average Scores across Industries for {selected_score}.  Each industry type is colour coded. Filters on the Side Allow us to Isolate Specific Additional Characteristics')          
    stats = calculate_stats(df, filtered_data, selected_score)
    generate_chart(df, stats, selected_score, "industry")
def analysis2():
    filtered_data = st.session_state['filtered_data']
    st.subheader('Geographical and Company Size Distribution')
    score_columns = ['Oracle Score', 'Culture Score', 'Capacity Score', 'Conduct Score', 'Collaboration Score']
    selected_score = st.selectbox('Click To Select Score for Statistics on Metrics', score_columns)
    stats = calculate_stats(df, filtered_data, selected_score)
    col1, col2 = st.columns([1.7,1])
    with col1:
        country_metrics = calculate_country_metrics(filtered_data)
        generate_chart(filtered_data, stats, selected_score, "region")
    st.divider()
    with col2:
        generate_chart(df, filtered_data, selected_score, "size")
    df_gapminder = px.data.gapminder()
    recognized_countries = df_gapminder['country'].unique()
    df['Mapped Country'] = df['Country'].apply(lambda country: find_closest_match(country, recognized_countries))
    df['Country'] = df['Mapped Country']            
    country_counts = filtered_data2['Country'].value_counts().reset_index()
    country_counts.columns = ['Country', 'count']
    df = filtered_data2.groupby('Country').filter(lambda x: len(x) > 20)
    st.subheader('Oracle Score Coverage: Regional Concentrations')
    col1, col2, col3, col4 = st.columns(4)
    country_metrics_data = calculate_stats(df, filtered_data2, selected_score)
    with col1:
        st.metric(label="Home Market Companies Rated", value=f"UK - {country_metrics_data['total_uk_companies']:,}")
    with col2:
        st.metric(label="Region With Most Companies Rated", value=f"{country_metrics_data['most_companies_country']} - {country_metrics_data['most_companies_count']:,}")
    with col3:
        st.metric(label="Home Market Average Oracle Score", value=f"UK - {country_metrics_data['uk_avg_score']:.2f}")
    with col4:
        st.metric(label="Highest Average Oracle Score (n > 20)", value=f"{country_metrics_data['highest_avg_score_country']} - {country_metrics_data['highest_avg_score_value']:.2f}")
    col5, col6 = st.columns(2)
    with col5:
        st.plotly_chart(plot_choropleth(country_counts))
    with col6:
        st.plotly_chart(plot_bar_chart(country_metrics_data['region_country_counts']), theme='streamlit')

def deepdive():
    st.subheader("Company Deep Dive")
    score_columns = ['Oracle Score', 'Culture Score', 'Capacity Score', 'Conduct Score', 'Collaboration Score']
    option = create_company_selectbox(df, "Company")  
    if option:
        company_data = df[df['Company'] == option]
    if option:
        filtered_df2 = df[df['Company'] == option]
        selected_geography = filtered_df2['Region'].values[0]
        selected_industry = filtered_df2['Industry'].values[0]
        selected_culture = filtered_df2['Culture Score'].values[0]
        selected_cap = filtered_df2['Capacity Score'].values[0]
        selected_cond = filtered_df2['Conduct Score'].values[0]
        selected_collab = filtered_df2['Collaboration Score'].values[0]
        selected_rank_range =  filtered_df2['Oracle Score'].values[0]
        median_oracle_score = df['Oracle Score'].median()
        percentile_rank = (df[df['Oracle Score'] < selected_rank_range]['Oracle Score'].count() + 1) / df.shape[0] * 100
    st.divider()
    st.subheader(f'Company Overview - {option}')
    website = company_data['Website'].iloc[0]
    st.markdown(f"{website}")
    col1, col2 = st.columns([50,50])
    with col1:
        st.markdown(f"##### Oracle Score")
    with col2:
        st.markdown(f"##### Oracle Score Components")
    col1, col2, col3 = st.columns([50,25,25])
    with col1:
        oracle_score = company_data['Oracle Score'].values[0]
        st_echarts(options=create_gauge_options(oracle_score, median_oracle_score, 'Oracle Score'), key="oracle_score")
    with col2:
        culture_delta = float(company_data['Culture Score'].iloc[0]) - df['Culture Score'].median()
        capacity_delta = float(company_data['Capacity Score'].iloc[0]) - df['Capacity Score'].median()
        conduct_delta = float(company_data['Conduct Score'].iloc[0]) - df['Conduct Score'].median()
        collaboration_delta = float(company_data['Collaboration Score'].iloc[0]) - df['Collaboration Score'].median()
        oracle_delta =  float(company_data['Oracle Score'].iloc[0]) - df['Oracle Score'].median()
        oracle_delta = float(company_data['Oracle Score'].iloc[0]) - median_oracle_score
        st.metric("Culture Score", "{:.2f}".format(company_data['Culture Score'].iloc[0]), "{:.2f}".format(culture_delta))
        st.markdown("")
        st.markdown("")
        st.markdown("")
        st.markdown("")
        st.metric("Capacity Score", "{:.2f}".format(company_data['Capacity Score'].iloc[0]), "{:.2f}".format(capacity_delta))    
    with col3:
        st.metric("Conduct Score", "{:.2f}".format(company_data['Conduct Score'].iloc[0]), "{:.2f}".format(conduct_delta))
        st.markdown('')
        st.markdown("")
        st.markdown("")
        st.markdown("")
        st.metric("Collaboration Score", "{:.2f}".format(company_data['Collaboration Score'].iloc[0]), "{:.2f}".format(collaboration_delta))
    cola, colb, colc, cold, colz = st.columns(5)
    with cola: 
        st.markdown("Industry")
        industry_text = company_data['Industry'].iloc[0]
        st.markdown(f"###### {industry_text}")
    with colb:
        st.markdown('Region')
        geo_text = company_data['Region'].iloc[0]
        st.markdown(f"###### {geo_text}")
    with colc: 
        st.markdown(f'Company Size')
        size = company_data['Company Size'].iloc[0]
        st.markdown(f"###### {size}")
    with cold:
        st.markdown(f'Employees')
        employees = company_data['Employees (Estimate)'].iloc[0]
        st.markdown(f"###### {employees}")
    with colz:
        if company_data is not None and 'B Corp' in company_data.columns:
            b_corp_status = "Certified B Corp" if company_data['B Corp'].iloc[0] == 1 else "Not a Certified B Corp"
        else:
            b_corp_status = "Not a Certified B Corp"
            st.markdown("B Corp Status")
        st.markdown(f'B Corp Status')
        st.markdown(f"###### {b_corp_status}")
    st.markdown(f"###### Description")
    description = company_data['Description'].iloc[0]
    st.caption(f"{description}. Source: Company or Wikipedia")
    col1, col2 = st.columns([1.25, 1])
    with col1:
        st.subheader(f'Radar Plot - {option}')
        st.markdown('This chart shows the company\'s scores across each Component of the Oracle Score.\n\n'
        'Users can add any company from the database as an overlay to compare scores.\n\n'
        'Additionally, users can toggle the median scores to see how the company compares to the median of the universe.')
        median_scores = df[score_columns].median().tolist()
        scores = company_data[score_columns].iloc[0].tolist()
        selected_company = create_company_selectbox(df, 'Comparator')
        with st.expander('Click To Expand For More Information About Radar Charts'):
            st.markdown('Radar Charts are often used in business and sports to display performance metrics.\n\n'
            'For example, in business, they could compare different products or companies across a range of attributes like price, quality, and customer satisfaction.\n\n'
            'In sports, they might compare athletes across various skills like speed, strength, and agility.\n\n'
            'In our Case they show how a company performs across our 4 C\s.\n\n'
            'Radar charts can quickly highlight areas of strength and weakness. This makes them useful in situations where you want to assess the overall balance of a subject\s attributes, like is a company performing well on one metric but abysmally on another?\n\n'
            'One of the most significant functions of radar charts is their ability to overlay multiple subjects for direct comparison.\n\n'
            'This overlay can provide a clear visual representation of how different subjects compare across the same set of variables. For example, you could overlay the performance metrics of different departments within a company to see which areas each department excels or needs improvement in.')
    with col2: 
            st.markdown('')
            st.markdown('')
            st.markdown('')
            st.markdown('')
            col1, col2 = st.columns([1, 1])
            with col1:
                show_median = st.toggle('Show Median Scores', value=False)
            with col2:
                show_comparison = st.toggle('Show Selected Comparator', value=False)
            radar_chart = create_radar_chart(df, scores, score_columns, selected_company, option, show_median, show_comparison)
            st.plotly_chart(radar_chart)
            st.divider()

    st.subheader(f'SDG Revenue Alignment - {option}')
    sdg_expander()
    SDG_Impact_Alignment(df, selected_company)

styles = {
    "container": {"margin": "0px !important", "padding": "0!important", "align-items": "stretch", "background-color": "#fafafa"},
    "icon": {"color": "black", "font-size": "14px"}, 
    "nav-link": {"font-size": "14px", "text-align": "left", "margin":"0px", "--hover-color": "#eee"},
    "nav-link-selected": {"background-color": "lightblue", "font-size": "14px", "font-weight": "normal", "color": "black", },
}

st.subheader('Oracle Partnerships with Purpose Tool')
menu = {
    'title': 'Navigation',
    'items': { 
        'Introduction & Instructions' : {
            'action': None, 'item_icon': 'house', 'submenu': {
                'title': None,
                'items': { 
                    'Introduction' : {'action': intro_page, 'item_icon': 'list-task', 'submenu': None},
                    '3rd Party Data Used' : {'action': sdg_expander, 'item_icon': 'database-dash', 'submenu': None},
                    'Proprietary Data Logic' : {'action': "", 'item_icon': 'list-task', 'submenu': None},
                },
                'menu_icon': 'filter-circle',
                'default_index': 0,
                'with_view_panel': 'main',
                'orientation': 'horizontal',
                'styles': styles
            }
        },
        'Aggregate Data' : {
            'action': None, 'item_icon': 'funnel', 'submenu': {
                'title': None,
                'items': { 
                    'Aggregate Filter' : {'action': aggframe, 'table-landscape': 'key', 'submenu': None},
                    'Analysis Tab 1' : {'action': analysis1, 'item_icon': 'file-earmark-check', 'submenu': None},
                    'Analysis Tab 2' : {'action': analysis2, 'item_icon': 'file-earmark-plus', 'submenu': None},
                },
                'menu_icon': 'postcard',
                'default_index': 0,
                'with_view_panel': 'main',
                'orientation': 'horizontal',
                'styles': styles
            }
        },
        'Company Deep Dive' : {
            'action': None, 'item_icon': 'crosshair', 'submenu': {
                'title': None,
                'items': { 
                    'Company Deep Dive' : {'action': deepdive, 'item_icon': 'radar', 'submenu': None},
                    'SDG & Impact Alignment' : {'action': "", 'item_icon': 'rainbow', 'submenu': None},
                },
                'menu_icon': 'crosshair',
                'default_index': 0,
                'with_view_panel': 'main',
                'orientation': 'horizontal',
                'styles': styles
            }
        }
    },
    'menu_icon': 'option',
    'default_index': 0,
    'with_view_panel': 'sidebar',
    'orientation': 'vertical',
    'styles': styles
}

def show_menu(menu):
    def _get_options(menu):
        options = list(menu['items'].keys())
        return options

    def _get_icons(menu):
        icons = [v.get('item_icon', 'default_icon') for _k, v in menu['items'].items()]
        return icons

    kwargs = {
        'menu_title': menu['title'] ,
        'options': _get_options(menu),
        'icons': _get_icons(menu),
        'menu_icon': menu['menu_icon'],
        'default_index': menu['default_index'],
        'orientation': menu['orientation'],
        'styles': menu['styles']
    }

    with_view_panel = menu['with_view_panel']
    if with_view_panel == 'sidebar':
        with st.sidebar:
            menu_selection = option_menu(**kwargs)
    elif with_view_panel == 'main':
        menu_selection = option_menu(**kwargs)
    else:
        raise ValueError(f"Unknown view panel value: {with_view_panel}. Must be 'sidebar' or 'main'.")

    if menu['items'][menu_selection]['submenu']:
        show_menu(menu['items'][menu_selection]['submenu'])

    if menu['items'][menu_selection]['action']:
        menu['items'][menu_selection]['action']()

show_menu(menu)
st.write('Kian 2023. :gear: :mag: for Oracle.')

