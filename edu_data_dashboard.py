import streamlit as st
import pandas as pd
import plotly.express as px

#Page Configuration

st.set_page_config(
    page_title="Educational Facilities in Nigeria Dashboard",
    page_icon="📚",
    layout="wide"
)

@st.cache_data #Decorator to speed up the app
def load_data():
    try:
        df = pd.read_csv('data/clean_edu_data.csv')
        return df
    except FileExistsError as e:
        st.warning(f'Error!: {e}')


def sidebar_filter(df):
    st.sidebar.header('Student Filters')

    facility = st.sidebar.multiselect(
        'Choose Facility Type',
        options=df['facility_type'].unique(),
        default=df['facility_type'].unique()
    )

    management = st.sidebar.multiselect(
        'Choose Management Type',
        options=df['management'].unique(),
        default=df['management'].unique()
    )

    location = st.sidebar.multiselect(
        "Select State(s)",
        options=df['states'].unique(),
        default=df['states'].unique()
    )
    return facility, management, location

    #To connect the filters
def filter_data(df, facility, management, location):
    filtered_df = df[df['facility_type'].isin(facility) & df['management'].isin(management) & df['states'].isin(location)]
    return filtered_df

    #KPI Metrics
def display_kpi(filtered_df):
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric('📚 Total Schools', f'{len(filtered_df):,}')

    with col2:
        tot_stud = filtered_df['total_student'].sum() if len(filtered_df) > 0 else 0
        st.metric('👩🏻‍🤝‍👩🏼 Total Students', f'{tot_stud:,}')
    
    with col3:
        average_studs = filtered_df['total_student'].mean() if len(filtered_df) > 0 else 0
        st.metric('🧑🏻‍🤝‍🧑🏼Average Students', f'{average_studs:.2f}')

    with col4:
        electricity_pct = (filtered_df['PHCN_electricity'] == True).sum() / len(filtered_df) * 100 if len(filtered_df) > 0 else 0
        st.metric('💡Schools with PHCN', f'{electricity_pct:.2f}%')

    with col5:
        water_pct = (filtered_df['improved_water_supply'] == True).sum() / len(filtered_df) * 100 if len(filtered_df) > 0 else 0
        st.metric('💡Schools with Water', f'{water_pct:.2f}%')

#Charts Creation
def display_charts(filtered_df):
    if len(filtered_df) == 0:
        st.warning('No Filter Selected. Please Adjust Selection')
        return

    col1, col2 = st.columns(2)

    with col1:
        st.subheader('Distribution of School Types')
        school_count = filtered_df['facility_type'].value_counts()
        fig1 = px.bar(
            x=school_count.index,
            y=school_count.values,
        )
        fig1.update_layout(
            xaxis_title='School Type',
            yaxis_title='Frequency'
        )
        st.plotly_chart(fig1, width='stretch')

    with col2:
        st.subheader('Students Population Distribution')
        fig2 = px.histogram(
            filtered_df, x='total_student', nbins=20
        )
        fig2.update_traces(
            marker_line_color='white',
            marker_line_width=1
        )

        fig2.update_layout(
            xaxis_title='School Population',
            yaxis_title='Count'
        )
        st.plotly_chart(fig2, width='stretch')
    
    col3, col4 = st.columns(2)

    with col3:
        st.subheader('School Management Comparision')
        mgt_count = filtered_df['management'].value_counts()
        fig3 = px.bar(
            x=mgt_count.index,
            y=mgt_count.values,
        )
        fig3.update_layout(
            xaxis_title='Management Type',
            yaxis_title='Count'
        )
        st.plotly_chart(fig3, width='stretch')

    with col4:
        st.subheader('Electricity Availability')
        ele_count = filtered_df['PHCN_electricity'].value_counts()
        fig4 =px.pie(
            values=ele_count.values,
            names=ele_count.index,
        hole=0.4
        )
        st.plotly_chart(fig4, width='stretch')

    col5, col6 = st.columns(2)

    with col5:
            Water_pct = (
            filtered_df['improved_water_supply'].mean() * 100
            )
            Sanitation_pct = (filtered_df['improved_sanitation'].mean() * 100)

            access = pd.DataFrame({
                'Category':['Water','Sanitation'],
                'Percentage':[Water_pct,Sanitation_pct]
        
            })
            fig4 = px.pie(
                access,
                values='Percentage',
                names='Category',
                title='Access to Improved Water and Sanitation'
            )
            st.plotly_chart(fig4, width='stretch')




    with col6:
        fig6 = px.scatter_mapbox(filtered_df,
            lat='latitude',
            lon='longitude',
            hover_name='facility_name',
            zoom=4,
            height=600
        )
        fig6.update_layout(
            mapbox_style='open-street-map'
        )
        st.plotly_chart(fig6, width='stretch')

#Display Table
def table_data(filtered_df):
    if len(filtered_df) > 0:
        st.dataframe(filtered_df, width='stretch', height=300)
    else:
        st.warning('No Student Data To Display')

    


#Control Function
def main():
    #load data
    df = load_data()

    #sidebar call
    facility, management, location = sidebar_filter(df)

    #filter connection
    filtered_df =filter_data(df, facility, management, location)

    st.title('Educational Facilities in Nigeria Dashboard')
    st.markdown('---')

    #call filter
    display_kpi(filtered_df)

    #Display Chart
    st.markdown("---")
    display_charts(filtered_df)

    #Display dataframe
    st.markdown("---")
    table_data(filtered_df)


main()
