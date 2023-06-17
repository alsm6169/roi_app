import streamlit as st
import pandas as pd
import altair as alt
import numpy as np

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


def show_main_app():
    st.title("Hillrom VIP RoI calculator")
    st.subheader("General Information Settings")
    input_dict = {}
    input_dict['projection_years'] = st.slider("Projection Years",
                                               min_value=3, max_value=15, value=10, step=1)
    input_dict['num_beds'] = st.number_input("Number of Beds",
                                             min_value=10, value=150, step=10)
    input_dict['average_stay'] = st.number_input("Average Stay",
                                                 min_value=1.0, value=6.2, step=0.1)
    input_dict['average_occupancy'] = st.number_input("Average Occupancy (%)",
                                                      min_value=0.0, max_value=1.0, value=0.9, step=0.1)
    st.divider()
    st.subheader("Cost Settings")
    st.divider()
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
    st.divider()
    st.subheader("Injury Reduction Benefit Settings")
    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Pressure Injuries")
        input_dict['pinj_risk'] = st.number_input("Pressure Injury Risk (%)",
                                                  min_value=0.0, max_value=1.0, value=0.07, step=0.05)
        input_dict['pinj_sore_reduction'] = st.number_input("Pressure Injury Sore Rate Reduction due to Hillrom (%)",
                                                       min_value=0.0, max_value=1.0, value=0.33,step=0.05)
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
                                                      min_value=0.0, max_value=1.0, value=0.2, step=0.05)
        input_dict['fall_additional_days'] = st.number_input("Fall Additional Additional Length of Stay",
                                                             min_value=1, max_value=10, value=4, step=1)
        input_dict['fall_cost_per_day'] = st.number_input("Fall Additional Cost per Hospital Day  ($)",
                                                          min_value=50.0, max_value=500.0, value=71.62, step=5.0)
    st.divider()
    st.subheader("Other Benefit Settings")
    input_dict['nurse_workload_saving'] = st.number_input("Nurse Workload Saving ($)",
                                                        min_value=1000, value=9080, step=100)
    st.divider()
    num_keys = len(list(input_dict.values()))
    input_val_list = np.array(list(input_dict.values()))
    # convert from list into matrix for inserting into dataframe
    input_val_matrix = np.repeat(input_val_list, input_dict['projection_years']).\
        reshape(num_keys,input_dict['projection_years'])

    df_in = pd.DataFrame(index=range(input_dict['projection_years']),
                      columns=input_dict.keys(),
                      data=input_val_matrix.T)

    # start amending dataframe
    df_in = df_in.drop(['projection_years'], axis=1)
    # set costs other than year 0 (at time of purchase to 0)
    df_in.loc[1:,['hp_cost_per_bed','hp_warranty', 'man_cost_per_bed', 'man_warranty']] = 0
    # number of admissions per year
    df_in['num_admissions'] = (df_in['num_beds'] * 365) * df_in['average_occupancy'] / df_in['average_stay']
    # st.dataframe(df_in)
    df_interim = pd.DataFrame()
    df_interim['hp_year_cost'] = (df_in['hp_cost_per_bed'] + df_in['hp_service_cost_per_year'] +
                                   df_in['hp_warranty']) * df_in['num_beds'] * -1
    df_interim['man_year_cost'] = (df_in['man_cost_per_bed'] + df_in['man_service_cost_per_year'] +
                                   df_in['man_warranty']) * df_in['num_beds'] * -1
    df_interim['hp_pinj_saving'] = df_in['num_admissions'] * df_in['pinj_risk'] * \
                                   (1 - df_in['pinj_sore_reduction']) * \
                                   df_in['pinj_additional_days'] * \
                                   df_in['pinj_cost_per_day']
    df_interim['hp_fall_saving'] = df_in['num_admissions'] * df_in['fall_risk'] * \
                                   df_in['fall_near_bed'] * \
                                   df_in['fall_reduction_probability'] * \
                                   df_in['fall_additional_days'] * \
                                   df_in['fall_cost_per_day']
    df_interim['year_pnl'] = df_interim['hp_year_cost'] - df_interim['man_year_cost'] + \
                             df_interim['hp_pinj_saving'] + df_interim['hp_fall_saving'] + \
                             df_in['nurse_workload_saving']
    df_interim['cumulative_pnl'] = df_interim['year_pnl'].cumsum()
    df_interim.insert(loc=0, column='Year', value=df_interim.index)
    df_interim['Year'] = 'Y-' + (df_interim['Year']+1).astype(str)
    st.dataframe(df_interim.round(0))

    # Create Altair Chart
    chart = alt.Chart(df_interim).mark_bar().encode(
        x=alt.X('Year:N',sort=None),
        y=alt.Y('cumulative_pnl:Q'),
        tooltip=['Year', alt.Tooltip('cumulative_pnl:Q', format=',.0f')]
    ).interactive()

    st.altair_chart(chart, use_container_width=True)

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
    if not st.session_state.login:
        show_login()
    else:
        show_main_app()


if __name__ == "__main__":
    main()
