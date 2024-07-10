import streamlit as st
st.set_page_config(page_title='Bhoonidhi Satellite Footprint Viewer', layout='wide')
import geemap.foliumap as geemap
import warnings; warnings.filterwarnings('ignore')
import pandas as pd
import src.utils as ut

ut.initialize_sessionState()

st.title('  Bhoonidhi Satellite Footprint Viewer')

# Initialize Map
m = geemap.Map(plugin_Draw=False, add_google_map=False)  

# Create a Sidebar
st.sidebar.title('Parameters', )
with st.sidebar:
    ut.add_aoi_selector(mapObject=m)
    if st.session_state.aoi is "":
        st.info("Select AOI to Proceed")
    else:
        ut.set_params()
        if st.session_state['FormSubmitter:form-Submit']:
            ut.process_request()
            if hasattr(st.session_state, 'response') and hasattr(st.session_state, 'aoi') and (st.session_state.total_scenes > 0):
                ut.add_scenes_to_map(m)
            else:
                st.error('No data found. Please try again with different parameters.')

m.to_streamlit(height=850)

# Show scene metadataas a DataFrame below the map
if 'response' in st.session_state:
# Initialize an empty list to store DataFrames
    df_list = []
    for item in st.session_state['response']:
        if isinstance(item, dict):
            # Create a DataFrame for each dictionary and add it to the list
            df_list.append(pd.DataFrame([item]))
        else:
            st.write(f"Skipping an item that is not a dictionary. Type: {type(item)}")

    # Concatenate all DataFrames in the list
    if df_list:
        df = pd.concat(df_list, ignore_index=True)
        
    # Display the DataFrame
    with st.expander("Scenes Metadata"):
        st.dataframe(df)
else:
    pass