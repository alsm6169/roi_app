import streamlit as st
import pandas as pd
import altair as alt
import numpy as np
from PIL import Image

if 'login' not in st.session_state:
    st.session_state.login = False


def show_login():
    # Login Section
    st.sidebar.header("Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    login_button = st.sidebar.button("Login")

    if login_button:
        if authenticate(username, password):
            st.sidebar.success("Logged in as {}".format(username))
            st.session_state.login = True
            show_main_app()
        else:
            st.session_state.login = False
            st.sidebar.error("Invalid username or password")


def input_panel(input_dict):
    with st.expander("General Information Settings"):
        input_dict['projection_years'] = st.slider("Projection Years",
                                                   min_value=3, max_value=15, value=10, step=1)
        input_dict['num_beds'] = st.number_input("Number of Beds",
                                                 min_value=10, value=150, step=10)
        input_dict['average_stay'] = st.number_input("Average Stay",
                                                     min_value=1.0, value=6.2, step=0.1)
        input_dict['average_occupancy'] = st.number_input("Average Occupancy (%)",
                                                          min_value=0.0, max_value=1.0, value=0.9, step=0.1)
    # st.divider()
    # st.subheader("Cost Settings")
    # st.divider()
    with st.expander("Cost Settings"):
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Hillrom EPB")
            input_dict['hp_cost_per_bed'] = st.number_input("HP Cost per Bed ($)",
                                                            min_value=100, value=1763, step=10)
            input_dict['hp_service_cost_per_year'] = st.number_input("HP Bed Service per Year ($)",
                                                                     min_value=100.0, value=219.8, step=10.0)
            input_dict['hp_warranty'] = st.number_input("HP Warranty Cost ($)",
                                                        min_value=0, value=567, step=10)

        with col2:
            st.subheader("Manual Bed")
            input_dict['man_cost_per_bed'] = st.number_input("Manual Cost per Bed ($)",
                                                             min_value=100, value=861, step=10)
            input_dict['man_service_cost_per_year'] = st.number_input("Manual Bed Service per Year ($)",
                                                                      min_value=100.0, value=100.0, step=10.0)
            input_dict['man_warranty'] = st.number_input("Manual Warranty ($)",
                                                         min_value=0, value=0, step=10)
    # st.divider()
    # st.subheader("Injury Reduction Benefit Settings")
    # st.divider()
    with st.expander("Injury Reduction Benefit Settings"):
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Pressure Injuries")
            input_dict['pinj_risk'] = st.number_input("Pressure Injury Risk (%)",
                                                      min_value=0.0, max_value=1.0, value=0.07, step=0.05)
            input_dict['pinj_sore_reduction'] = st.number_input(
                "Pressure Injury Sore Rate Reduction due to Hillrom (%)",
                min_value=0.0, max_value=1.0, value=0.33, step=0.05)
            input_dict['pinj_additional_days'] = st.number_input("Pressure Additional Length of Stay",
                                                                 min_value=1, value=4, step=1)
            input_dict['pinj_cost_per_day'] = st.number_input("Pressure Additional Cost per Hospital Day ($)",
                                                              min_value=50.0, max_value=500.0, value=70.62, step=5.0)

        with col2:
            st.subheader("Patient Falls")
            input_dict['fall_risk'] = st.number_input("Inpatient Fall Risk (%)",
                                                      min_value=0.0, max_value=1.0, value=0.03, step=0.05)
            input_dict['fall_near_bed'] = st.number_input("Fall Near Bed Probability (%)",
                                                          min_value=0.0, max_value=1.0, value=0.6, step=0.05)
            input_dict['fall_reduction_probability'] = st.number_input("Fall Reduction Probability (%)",
                                                                       min_value=0.0, max_value=1.0, value=0.2,
                                                                       step=0.05)
            input_dict['fall_additional_days'] = st.number_input("Fall Additional Additional Length of Stay",
                                                                 min_value=1, max_value=10, value=4, step=1)
            input_dict['fall_cost_per_day'] = st.number_input("Fall Additional Cost per Hospital Day  ($)",
                                                              min_value=50.0, max_value=500.0, value=71.62, step=5.0)
    # st.divider()
    # st.subheader("Other Benefit Settings")
    with st.expander("Other Benefit Settings"):
        input_dict['nurse_workload_saving'] = st.number_input("Nurse Workload Saving ($)",
                                                              min_value=1000, value=9080, step=100)
    # st.divider()

    return input_dict


def calculate_roi(input_dict):
    num_keys = len(list(input_dict.values()))
    input_val_list = np.array(list(input_dict.values()))
    # convert from list into matrix for inserting into dataframe
    input_val_matrix = np.repeat(input_val_list, input_dict['projection_years']). \
        reshape(num_keys, input_dict['projection_years'])

    df_in = pd.DataFrame(index=range(input_dict['projection_years']),
                         columns=input_dict.keys(),
                         data=input_val_matrix.T)

    # start amending dataframe
    df_in = df_in.drop(['projection_years'], axis=1)
    # set costs other than year 0 (at time of purchase to 0)
    df_in.loc[1:, ['hp_cost_per_bed', 'hp_warranty', 'man_cost_per_bed', 'man_warranty']] = 0
    # number of admissions per year
    df_in['num_admissions'] = (df_in['num_beds'] * 365) * df_in['average_occupancy'] / df_in['average_stay']
    # st.dataframe(df_in)
    df_out = pd.DataFrame()
    df_out['hp_year_cost'] = (df_in['hp_cost_per_bed'] + df_in['hp_service_cost_per_year'] +
                                  df_in['hp_warranty']) * df_in['num_beds'] * -1
    df_out['man_year_cost'] = (df_in['man_cost_per_bed'] + df_in['man_service_cost_per_year'] +
                                   df_in['man_warranty']) * df_in['num_beds'] * -1
    df_out['hp_pinj_saving'] = df_in['num_admissions'] * df_in['pinj_risk'] * \
                                   (1 - df_in['pinj_sore_reduction']) * \
                                   df_in['pinj_additional_days'] * \
                                   df_in['pinj_cost_per_day']
    df_out['hp_fall_saving'] = df_in['num_admissions'] * df_in['fall_risk'] * \
                                   df_in['fall_near_bed'] * \
                                   df_in['fall_reduction_probability'] * \
                                   df_in['fall_additional_days'] * \
                                   df_in['fall_cost_per_day']
    df_out['year_pnl'] = df_out['hp_year_cost'] - df_out['man_year_cost'] + \
                             df_out['hp_pinj_saving'] + df_out['hp_fall_saving'] + \
                             df_in['nurse_workload_saving']
    df_out['cumulative_pnl'] = df_out['year_pnl'].cumsum()
    df_out.insert(loc=0, column='Year', value=df_out.index)
    df_out['Year'] = 'Y-' + (df_out['Year'] + 1).astype(str)
    # st.dataframe(df_out.round(0))
    return df_out


def display_charts(df_out):
    # Create Altair Chart
    chart = alt.Chart(df_out).mark_bar().encode(
        x=alt.X('Year:N', sort=None),
        y=alt.Y('cumulative_pnl:Q'),
        tooltip=['Year', alt.Tooltip('cumulative_pnl:Q', format=',.0f')]
    ).interactive()

    st.altair_chart(chart, use_container_width=True)


def show_main_app():
    input_dict = {}
    # st.title("Hillrom VIP RoI calculator")
    ansea_img = Image.open('Logo.png')
    st.image(ansea_img)
    st.write()
    st.write()
    st.markdown("<h1 style='text-align: left; color: darkblue;'>Hillrom VIP RoI Calculator</h1>", unsafe_allow_html=True)
    # st.subheader("General Information Settings")
    main_col1, main_col2 = st.columns([0.35,0.65])
    with main_col1:
        st.subheader("Model Parameter Settings")
        st.divider()
        input_dict = input_panel(input_dict)
    with main_col2:
        st.subheader("RoI Model Cumulative P&L")
        st.divider()
        df_out = calculate_roi(input_dict)
        display_charts(df_out)

    # Logout Button
    logout_button = st.sidebar.button("Logout")
    if logout_button:
        st.sidebar.empty()  # Clear the sidebar
        st.empty()  # Clear the main content
        st.info("Logged out")
        st.session_state.login = False


def authenticate(username, password):
    # Replace with your authentication logic
    if username == "admin" and password == "password":
        return True
    else:
        return False


def main():
    st.set_page_config(page_title='Hillrom VIP RoI calculator',
                       layout="wide")
    if not st.session_state.login:
        show_login()
    else:
        show_main_app()


if __name__ == "__main__":
    main()
