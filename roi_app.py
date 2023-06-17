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
                                                                 min_value=100, value=220, step=10)
        input_dict['hp_warranty'] = st.number_input("HP Warranty Cost ($)",
                                                    min_value=0, value=567, step=10)

    with col2:
        st.subheader("Manual Bed")
        input_dict['man_cost_per_bed'] = st.number_input("Manual Cost per Bed ($)",
                                                         min_value=100, value=861, step=10)
        input_dict['man_service_cost_per_year'] = st.number_input("Manual Bed Service per Year ($)",
                                                                  min_value=100, value=100, step=10)
        input_dict['man_warranty'] = st.number_input("Manual Warranty ($)",
                                                     min_value=0, value=0, step=10)
    st.divider()
    st.subheader("Potential Benefit Settings")
    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Pressure Injuries")
        input_dict['pinj_risk'] = st.number_input("Pressure Injury Risk (%)", min_value=0.0, max_value=1.0, value=0.07,
                                                  step=0.05)
        input_dict['pinj_additional_days'] = st.number_input("Pressure Additional Length of Stay",
                                                             min_value=1, value=4, step=1)
        input_dict['pinj_cost_per_day'] = st.number_input("Pressure Additional Cost per Hospital Day ($)",
                                                          min_value=50, max_value=500,
                                                          value=71, step=5)

    with col2:
        st.subheader("Patient Falls")
        input_dict['fall_risk'] = st.number_input("Inpatient Fall risk (%)",
                                                  min_value=0.0, max_value=1.0, value=0.03, step=0.05)
        input_dict['fall_near_bed'] = st.number_input("Fall Near Bed Probability (%)",
                                                      min_value=0.0, max_value=1.0, value=0.6, step=0.05)
        input_dict['fall_additional_days'] = st.number_input("Fall Additional Additional Length of Stay",
                                                             min_value=1, max_value=10, value=4, step=1)
        input_dict['fall_cost_per_day'] = st.number_input("Fall Additional Cost per Hospital Day  ($)",
                                                          min_value=50, max_value=500,
                                                          value=72, step=5)
    st.divider()
    num_keys = len(list(input_dict.values()))
    input_val_list = np.array(list(input_dict.values()))
    input_val_matrix = np.repeat(input_val_list, input_dict['projection_years']).\
        reshape(num_keys,input_dict['projection_years'])

    df = pd.DataFrame(index=range(input_dict['projection_years']),
                      columns=input_dict.keys(),
                      data=input_val_matrix.T)
    df = df.drop(['projection_years'], axis=1)
    # df['num_beds'] = input_dict['num_beds']
    # df['average_stay'] = input_dict['average_stay']
    # df['average_occupancy'] = input_dict['average_occupancy']
    # df[['num_beds', 'average_stay', 'average_occupancy']] = input_dict['num_beds'],\
    #    input_dict['average_stay'], input_dict['average_occupancy']

    st.dataframe(df)

    # Generate Dataframe
    # data = pd.DataFrame({
    #     'Numbers': ['Number 1', 'Number 2', 'Number 3'],
    #     'Values': [num_beds, number2, number3]
    # })
    #
    # # Create Altair Chart
    # chart = alt.Chart(data).mark_bar().encode(
    #     x='Numbers',
    #     y='Values',
    #     tooltip=['Numbers', 'Values']
    # ).interactive()
    #
    # st.altair_chart(chart, use_container_width=True)
    #
    # # Display Dataframe
    # st.write("Dataframe:")
    # st.dataframe(data)

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
