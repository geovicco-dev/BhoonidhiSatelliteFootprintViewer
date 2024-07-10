import streamlit as st
st.set_page_config(page_title='Bhoonidhi Satellite Footprint Viewer', layout='wide')
import geemap.foliumap as geemap
import warnings; warnings.filterwarnings('ignore')
import geopandas as gpd
import src.utils as ut

ut.initialize_sessionState()

st.title('  Bhoonidhi Satellite Footprint Viewer')

# INITIALIZE MAP
m = geemap.Map(plugin_Draw=True, add_google_map=False)  

# Convert C2 into Sidebar
st.sidebar.title('Parameters', )
with st.sidebar:
    ut.add_aoi_selector(mapObject=m)
    if st.session_state.aoi is not None:
        st.info("Select AOI to Proceed")
        ut.set_params()
        if 'satellite' in st.session_state:
            # Display satellite information
            ut.satellite_info_component(st.session_state.satellite)
        if st.session_state['FormSubmitter:processing-params-Submit']:
            ut.process_request()
            if hasattr(st.session_state, 'response') and hasattr(st.session_state, 'aoi') and (st.session_state.total_scenes > 0):
                ut.add_scenes_to_map(m)
            else:
                st.error('No data found. Please try again with different parameters.')
# print(st.session_state)
m.to_streamlit(height=800)