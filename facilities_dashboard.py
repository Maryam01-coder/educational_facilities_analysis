import pandas as pd
import streamlit as st
import plotly.express as px

# set up config
st.set_page_config(
    page_title="Educational Facilities Dashboard",
    page_icon="🏫",
    layout="wide"
)

@st.cache_data #Decorator to speed up the app
def load_dataset():
    try:
        df = pd.read_csv("cleaned_facilities_records.csv")
        return df
    except FileExistsError as e:
        st.warning(f'Error! File does not exist: {e}')


def sidebar_filter(df):
    st.sidebar.header('🔍 Filters')

    facility = st.sidebar.multiselect(
        'Select Facility Type',
        options=df['facility_type_display'].unique(),
        default=df['facility_type_display'].unique()
    )

    management = st.sidebar.multiselect(
        'Select Management Type',
        options=df['management'].unique(),
        default=df['management'].unique()
    )

    location = st.sidebar.multiselect(
        "Select Local Government",
        options=df['unique_lga'].unique(),
        default=df['unique_lga'].unique()
    )
    st.sidebar.divider()

    st.sidebar.subheader("📅 Date Range")

    df["date_of_survey"] = pd.to_datetime(df["date_of_survey"])

    start_date = st.sidebar.date_input(
        "Start Date",
        value=df["date_of_survey"].min().date()
    )

    end_date = st.sidebar.date_input(
        "End Date",
        value=df["date_of_survey"].max().date()
    )

    return facility, management, location, start_date, end_date

#adding download button
def save_filtered_df(filtered_df):
    st.sidebar.divider()

    st.sidebar.subheader("📥 Export")

    csv = filtered_df.to_csv(index=False).encode("utf-8")

    st.sidebar.download_button(
        label="Download Filtered Data",
        data=csv,
        file_name="filtered_data.csv",
        mime="text/csv"
    )

def filter_data(df, facility, management, location, start_date, end_date):
    filtered_df = df[
        df['facility_type_display'].isin(facility) & 
        df['management'].isin(management) & 
        df['unique_lga'].isin(location) & 
        (df["date_of_survey"].dt.date >= start_date) & 
        (df["date_of_survey"].dt.date <= end_date)
    ]
    return filtered_df


def format_students(value):
    if value >= 1000000:
        return f"{value / 1000000:.0f}M"
    elif value >= 1000:
        return f"{value / 1000:.0f}K"
    else:
        return f"{value:,.0f}"

#displaying the KPIS
def kpi_display(filtered_df):
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric('🏫Total Schools', f'{len(filtered_df):,}')

    with col2:
        total_students = filtered_df['num_students_total'].sum() if len(filtered_df) > 0 else 0
        st.metric('👩🏻‍🤝‍👩🏼Total Students', format_students(total_students))    

    with col3:
        average_students = filtered_df['num_students_total'].mean() if len(filtered_df) > 0 else 0
        st.metric('🧑🏻‍🤝‍🧑🏼Average Students', f'{average_students:.2f}')

    with col4:
        electricity = (filtered_df['phcn_electricity'] == True).sum() / len(filtered_df) * 100 if len(filtered_df) > 0 else 0
        st.metric('💡Schools with PHCN', f'{electricity:.2f}%')

    with col5:
        water_access = (filtered_df['improved_water_supply'] == True).sum() / len(filtered_df) * 100 if len(filtered_df) > 0 else 0
        st.metric('🚰Schools with Water', f'{water_access:.2f}%')

#creating plotly charts 
def charts(filtered_df):
    if len(filtered_df) == 0:
        st.warning('No Filter Selected. Please Adjust Your Selection.')
        return

    col1, col2 = st.columns(2)

    with col1:
        st.subheader('Distribution of School Types')
        school_count = filtered_df['facility_type_display'].value_counts()
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
        st.subheader('Distribution of Students Population')
        fig2 = px.histogram(
            filtered_df, 
            x='num_students_total', 
            nbins=20,
        )
        fig2.update_traces(
            marker_line_color='white',
            marker_line_width=1
        )

        fig2.update_layout(
            xaxis_title='Students Population',
            yaxis_title='School Population'
        )
        st.plotly_chart(fig2, width='stretch')
    
    col3, col4 = st.columns(2)

    with col3:
        st.subheader('Distribution of Unique School Management')
        m_count = filtered_df['management'].value_counts()
        fig3 = px.bar(
            x=m_count.index,
            y=m_count.values,
        )
        fig3.update_layout(
            xaxis_title='Management Type',
            yaxis_title='Count'
        )
        st.plotly_chart(fig3, width='stretch')

    with col4:
        st.subheader('Electricity Availability')
        electricity_count = filtered_df['phcn_electricity'].value_counts()
        fig4 =px.pie(
            values=electricity_count.values,
            names=electricity_count.index,
            hole=0.5,
        )
        st.plotly_chart(fig4, width='stretch')

    col5, col6 = st.columns(2)

    with col5:
            Water_access = (
            filtered_df['improved_water_supply'].mean() * 100
            )
            Sanitation_access = (filtered_df['improved_sanitation'].mean() * 100)

            access = pd.DataFrame({
                'Category':['Water','Sanitation'],
                'Percentage':[Water_access,Sanitation_access]
        
            })
            fig4 = px.pie(
                access,
                values='Percentage',
                names='Category',
                title='Access to Improved Water and Sanitation',
            )
            st.plotly_chart(fig4, width='stretch')


    with col6:
        fig6 = px.scatter_map(filtered_df,
            lat='latitude',
            lon='longitude',
            hover_name='facility_name',
            zoom=4,
            height=600,
        )
        fig6.update_layout(
            map_style='open-street-map'
        )
        st.plotly_chart(fig6, width='stretch')

#Display Table
def table(filtered_df):
    if len(filtered_df) > 0:
        st.dataframe(filtered_df, width='stretch', height=300)
    else:
        st.warning('No record to display. Use the filter options.')

def main():
    # load dataset
    df = load_dataset()

    # sidebar items
    facility, management, location, start_date, end_date = sidebar_filter(df)

    # filtered_df 
    filtered_df =filter_data(df, facility, management, location, start_date, end_date)

    #download button
    save_filtered_df(filtered_df)

    #main_layout
    st.title("Educational Facilities Dashboard")
    st.markdown("---")

    #metrics/kpis
    kpi_display(filtered_df)

    #plotly_chart
    charts(filtered_df)

    #display table
    table(filtered_df)

if __name__ == "__main__":
    main()