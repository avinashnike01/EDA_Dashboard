import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
from streamlit_option_menu import option_menu
from mitosheet.streamlit.v1 import spreadsheet
# ###import pandas_profiling
# ###from streamlit_pandas_profiling import st_profile_report
from streamlit_ydata_profiling import st_profile_report
from ydata_profiling import ProfileReport
import pygwalker as pyg
from pygwalker.api.streamlit import StreamlitRenderer
import dtale
import dtale.app as dtale_app
from dtale.views import startup
from dtale.app import get_instance
from pathlib import Path
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import json

from dash_charts import plotlycharts_dash as dashchart
# import chatcsv_fn6 as chatfn

st.set_page_config(page_title="EDA Dashboard", layout="wide", page_icon=":bar_chart:")

file_path = Path(__file__).parent/ "st_auth/config.yaml"
# with file_path.open("rb") as file:
#     config = yaml.load(file, Loader=SafeLoader)

with open('./st_auth/config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)
# st.write(config)

# Pre-hashing all plain text passwords once
# Hasher.hash_passwords(config['credentials'])

if config is None:
    with file_path.open("rb") as file:
        config = yaml.load(file, Loader=SafeLoader)
# st.write(config)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['pre-authorized']
)
# st.write(config)

# # New users info added to config.ymal 
# with open('./st_auth/config.yaml', 'w') as file:
#     yaml.dump(config, file, default_flow_style=False)
# # st.write(config)

if st.session_state["authentication_status"]:
    with st.sidebar:
        with st.expander("Update user"):
            try:
                if authenticator.update_user_details(st.session_state["username"]):
                    st.success("Entries updated successfully")
            except Exception as e:
                st.error(e)
        with st.expander("Reset password"):
            try:
                if authenticator.reset_password(st.session_state['username']):
                    st.success('Password modified successfully')
            except Exception as e:
                st.error(e)      
            st.info("Password must contain at least one lowercase letter, one uppercase letter, one number, and one special character. It must be between 8 and 20 characters long.")      
    with open("./st_auth/config.yaml", "w") as file:
        yaml.dump(config, file, default_flow_style=False)
else:
    # st.write(config)
    with st.sidebar:
        with st.expander("New user registration"):
            st.warning("You must be pre-authorized to register for this app. Contact the developer for the authorization.")
            try:
                email_of_registered_user, username_of_registered_user, name_of_registered_user = authenticator.register_user(pre_authorization=True, clear_on_submit=False, captcha=False)
                if email_of_registered_user:
                    st.success("User registered successfully")
            except Exception as e:
                st.error(e)
            st.info("Name should contain only alphabetic charachers (upper or lowercase), periods, or spaces. It must be between 2 and 100 characters.")
            st.info("Username can be either a simple name (1 to 20 characters with letters, numbers, underscores, or hyphens), OR, a valid email address.")            
            st.info("Password must contain at least one lowercase letter, one uppercase letter, one number, and one special character. It must be between 8 and 20 characters long.")
        with st.expander("Forgot password"):
            try:
                (
                    username_of_forgotten_password,
                    email_of_forgotten_password,
                    new_random_password,
                ) = authenticator.forgot_password()
                if username_of_forgotten_password:
                    st.success("New password to be sent securely")
                    # # Random password should be transferred to user securely
                    # st.write(config["credentials"]["usernames"])
                    st.write(username_of_forgotten_password)
                    st.write(new_random_password)
                elif username_of_forgotten_password == False:
                    st.error("Username not found")
            except Exception as e:
                st.error(e)
            st.info("Password must contain at least one lowercase letter, one uppercase letter, one number, and one special character. It must be between 8 and 20 characters long.")        
        with st.expander("Forgot username"):
            try:
                (
                    username_of_forgotten_username,
                    email_of_forgotten_username,
                ) = authenticator.forgot_username()
                if username_of_forgotten_username:
                    st.success("Username to be sent securely")
                    # # Username should be transferred to user securely
                    # st.write(config["credentials"]["usernames"])
                    st.write(username_of_forgotten_username)
                elif username_of_forgotten_username == False:
                    st.error("Email not found")
            except Exception as e:
                st.error(e)
            st.info("Username can be either a simple name (1 to 20 characters with letters, numbers, underscores, or hyphens), OR, a valid email address.")

        # st.write(config)    
        # file_path = Path(__file__).parent / "config.yaml"
        # with file_path.open("w") as file:
        with open("./st_auth/config.yaml", "w") as file:
            yaml.dump(config, file, default_flow_style=False)
        # st.write(config)
        
    # authenticator.logout('Logout','sidebar', key="unique_key")
    # st.sidebar.write(f'Welcome *{st.session_state["name"]}*')    

# st.write(st.session_state["username"])
# st.write(st.session_state["authentication_status"])
# st.write(st.session_state)

authenticator.login('main')
# st.write(config)

if st.session_state["authentication_status"]:
    html_title = """
    <div style="background-color: #586e75; padding:5px;border-radius:10px">
    <h1 style="color:white;text-align:center;font-size:30px;">  EDA Dashboard </h1>
    </div>
    """
    components.html(html_title)
    st.markdown(
        "<style>div.block-container{padding-top:3rem;}</style>", unsafe_allow_html=True
    )

    st.sidebar.write(
        f'Welcome *{st.session_state["name"]} ({st.session_state["username"]})*'
    )
    
    with st.sidebar:
        authenticator.logout('Logout','sidebar', key="unique_key")

    with st.sidebar:
        sidebar_options = option_menu(
            menu_title="Main Menu",
            options=["Home", "Dashboard", "EDA", "Viz", "ChatCSV"],
            icons=["house", "clipboard2-data", "lightbulb", "graph-up arrow"],
            menu_icon="cast",
            default_index=0,
        )

    @st.cache_data()
    def load_data(df_in):
        return (
            pd.read_excel(df_in, sheet_name=None)
            if df_in.type != "text/csv"
            else pd.read_csv(df_in)
        )
    
    # @st.cache_data()
    # def load_data(filepath):
    #     if filepath.type != "text/csv":
    #         st.info("Select the Sheet Name or None ")
    #         sheet_name = st.text_input("Sheet Name")

    def load_check(data_file):
        # Determine the file type
        if data_file.type in [
            "application/vnd.ms-excel",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "text/csv",
        ]:
            df = load_data(data_file)
            return df

        else:
            st.error("Unsupported file format. Please upload an Excel or CSV file.")

    with st.sidebar:
        data_file = st.file_uploader(
            "Upload a data file", type=["csv", "txt", "xls", "xlsx"]
        )

    if data_file is not None:
        df = load_check(data_file)

        if "Data" not in st.session_state:
            st.session_state["Df"] = df
            st.session_state["Data"] = df

    else:
        st.cache_data.clear()
        st.cache_resource.clear()
        # st.session_state.clear()
        if "Data" in st.session_state:
            del st.session_state.Data, st.session_state.Df
        st.warning(
            "No data has been uploaded, please upload a data file of type (csv, txt, xls, xlsx) at the sidebar."
        )        
        st.stop()

    @st.cache_resource()
    def pandas_report(df_in):
        return ProfileReport(df_in, title="PandasProfile Report")
        # pr = df_in.profile_report()
        # # st_profile_report(pr)
        # return pr

    # You should cache your pygwalker renderer, if you don't want your memory to explode
    @st.cache_resource
    def get_pyg_renderer(df_in, spec_mode, vspec) -> "StreamlitRenderer":
        # # If you want to use feature of saving chart config, set `spec_io_mode="rw"`
        # return StreamlitRenderer(df, spec="./gw_config.json", spec_io_mode="rw")
        if vspec is None:
            return StreamlitRenderer(df_in, spec_io_mode=spec_mode, kernel_computation=True,)
        else:
            return StreamlitRenderer(df_in, spec=vspec, spec_io_mode=spec_mode, kernel_computation=True,)


    # @st.cache_data()
    def dashboard_fn(df_in):
        return dashchart.mydash_fun(df_in)

    # def chat_fn(df_in):
    #     return chatfn.chatcsvfn(df_in)
    #     # return

    if sidebar_options == "Home":
        Home_statement = "The REDCap link for this project can be accessed [here](https://www.google.com) and a data file to be analyzed can be uploaded at the sidebar."
        st.markdown(Home_statement)

        if data_file is not None:
            dfnames_list = list(df.keys())
            df_list = list(df.values())
            df_mod, code = spreadsheet(*df_list, df_names=dfnames_list, height="1000px")
            st.write(code)
            st.session_state["Data"] = df_mod

    elif sidebar_options == "Dashboard":
        Dashboard_statement = "A desired dashboard, containing important KPIs (Key Performance Indices), meaningful charts, tables and graphs can be displayed here, on request."
        st.markdown(Dashboard_statement)
        if data_file is not None:  
            df_Data = st.session_state["Data"]

            sheet_names = list(df_Data.keys())
            with st.sidebar:
                sheet_choice = st.selectbox("Pick a sheet for EDA", sheet_names)

            df_sheet = df_Data[sheet_choice]

            dashboard_fn(df_sheet)

        else:
            st.info(
                "No data has been uploaded, please upload a data file of type (csv, txt, xls, xlsx) at the sidebar."
            )
            st.stop()

    elif sidebar_options == "EDA":
        EDA_statement = "Here you can either auto generate Explanatory Data Analysis report of the modified/filtered data, or perform your own customized EDA by selecting Dtale in the dropdown selectbox at the sidebar."
        st.markdown(EDA_statement)
        if data_file is not None: 
            df_Data = st.session_state["Data"]

            sheet_names = list(df_Data.keys())
            with st.sidebar:
                sheet_choice = st.selectbox("Pick a sheet for EDA", sheet_names)

            df_sheet = df_Data[sheet_choice]

            EDA_options = ["Pandas-Profiling", "Dtale"]
            with st.sidebar:
                EDA_choice = st.selectbox("Pick a EDA tool", EDA_options)

            if EDA_choice == "Pandas-Profiling":
                st.subheader("Automated EDA with Pandas-Profiling")
                # pandas_report(df_sheet)
                pandas_profile = pandas_report(df_sheet)
                st_profile_report(pandas_profile)
                # components.iframe(pandas_profile, height=1000)
                # st.write(pandas_profile)

                with st.sidebar:
                    if st.button("Download Report", type="primary"):
                        pandas_profile.to_file("pandas_profile.html")                

            elif EDA_choice == "Dtale":
                st.subheader("Perform customized EDA with Dtale")
                # report_dtale = dtale.show(df_sheet, ignore_duplicate=True)
                # # st.write(report_dtale._main_url)
                # components.iframe(report_dtale._main_url, height=1000)
                
                # Saving data to D-Tale:
                startup(data_id="1", data=df_sheet)
                # Retrieving data from D-Tale
                # remember we set the data_id of our previous dataframe was "1"
                dtale_instance = get_instance("1") # get_instance("1").data
                ## Retireving data on the front end for display in <iframe>
                # html_dtale = """<iframe src="/dtale/main/1" style="height: 100%;width: 100%"/>"""
                # components.html(html_dtale, height=1000, scrolling=True)   
                components.iframe("/dtale/main/1", width=None, height=1000, scrolling=True)
                ## Creating links to open D-Tale in new tab
                # html_dtale = """<a href="/dtale/main/1" target="_blank">Dataframe 1</a>"""                
                # st.markdown(html_dtale, unsafe_allow_html=True)
                
        else:
            st.info(
                "No data has been uploaded, please upload a data file of type (csv, txt, xls, xlsx) at the sidebar."
            )
            st.stop()

    elif sidebar_options == "Viz":
        Viz_statement = "Here you can create your own desired graphs and plots, and have filters on them. Note that, if you move/change to a different menu, then your created charts/graphs will be deleted. To save your created charts, click on "
        st.markdown(Viz_statement)
        if data_file is not None:  
            df_Data = st.session_state["Data"]

            sheet_names = list(df_Data.keys())
            with st.sidebar:
                sheet_choice = st.selectbox("Pick a sheet for EDA", sheet_names)

            df_sheet = df_Data[sheet_choice]

            with st.sidebar:
                with st.expander("Choose the mode"):
                    # viz_file = st.file_uploader(
                    #     "Upload the saved viz json file", type="json"
                    # )
                    if "viz_data" not in st.session_state:
                        st.session_state["viz_data"] = None

                    viz_choices = st.radio(
                        "Choose one viz option:",
                        options=["Modify", "Original", "Clean"],
                        horizontal=True,
                    )
                    if viz_choices == "Original":
                        spec_mode = "r"
                        st.session_state["viz_data"] = r"./viz_config/config_org.json"
                    elif viz_choices == "Modify":
                        spec_mode = "rw"
                        st.session_state["viz_data"] = r"./viz_config/config_mod.json"
                        # if "viz_save" not in st.session_state:
                        #     st.session_state["viz_save"] = None
                        # if viz_file is not None:
                        #     # st.write(viz_file.type)
                        #     st.session_state["viz_data"] = viz_file.read()  
                        #     st.session_state["viz_save"] = st.session_state["viz_data"]
                        # else:
                        #     st.session_state["viz_data"] = st.session_state["viz_save"]
                        #     if st.session_state["viz_save"] is not None:
                        #         st.write("This viz corresponds to the previously uploaded json file. To change it, upload another saved viz json file")
                        #     else:
                        #         st.write("Upload the saved viz json file")
                    else:
                        spec_mode = "rw"
                        st.session_state["viz_data"] = None
            # st.write(st.session_state["viz_data"])
            renderer = get_pyg_renderer(df_sheet, spec_mode, vspec=st.session_state["viz_data"])
            renderer.explorer()
            
        else:
            st.info(
                "No data has been uploaded, please upload a data file of type (csv, txt, xls, xlsx) at the sidebar."
            )
            st.stop()

    elif sidebar_options == "ChatCSV":
        chatcsv_statement = (
            "You can chat with your data file here (using an AI model)."
        )
        st.markdown(chatcsv_statement)
        if data_file is not None:  
            df_Data = st.session_state["Data"]

            sheet_names = list(df_Data.keys())
            with st.sidebar:
                sheet_choice = st.selectbox("Pick a sheet for EDA", sheet_names)

            df_sheet = df_Data[sheet_choice]
            # chat_fn(df_sheet)

        else:
            st.info(
                "No data has been uploaded, please upload a data file of type (csv, txt, xls, xlsx) at the sidebar."
            )
            st.stop()        

elif st.session_state["authentication_status"] is False:
    st.error("Username/password is incorrect")

elif st.session_state["authentication_status"] is None:
    st.warning("Please enter your username and password to Login, or, Register as a New User at the sidebar")