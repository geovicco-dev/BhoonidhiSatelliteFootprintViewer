import streamlit as st
import pandas as pd
import geopandas as gpd
import os
import uuid
import tempfile
import zipfile
from datetime import date, timedelta
import datetime
from shapely.geometry import Polygon
import folium

def get_bounds(shp_path):
    gdf = gpd.read_file(shp_path)
    lat = gdf.centroid.y.values[0]
    lon = gdf.centroid.x.values[0]
    return lat, lon

# First, let's create a DataFrame with the satellite information
satellite_data = pd.DataFrame([
    {"Satellite": "Aqua", "Availability": "31-Dec-2003 - 31-Dec-2019", "Resolution": "500 m"},
    {"Satellite": "CartoSat-1", "Availability": "8-May-2005 - 19-Feb-2019", "Resolution": "2.5 m"},
    {"Satellite": "CartoSat-2", "Availability": "14-Apr-2007 - 23-May-2019", "Resolution": "0.8 m"},
    {"Satellite": "CartoSat-2C", "Availability": "1-Mar-2016 - till date", "Resolution": "0.65 m - 1.6 m"},
    {"Satellite": "CartoSat-2D", "Availability": "17-Feb-2017 - till date", "Resolution": "0.65 m - 1.6 m"},
    {"Satellite": "CartoSat-2E", "Availability": "25-Jun-2017 - till date", "Resolution": "0.65 m - 1.6 m"},
    {"Satellite": "CartoSat-2F", "Availability": "15-Jun-2018 - till date", "Resolution": "0.65 m - 1.6 m"},
    {"Satellite": "CartoSat-3", "Availability": "10-Jun-2020 - till date", "Resolution": "0.28 m - 1.1 m"},
    {"Satellite": "EOS-04", "Availability": "23-Mar-2022 - till date", "Resolution": "3 m - 33 m"},
    {"Satellite": "EOS-06", "Availability": "1-Apr-2023 - till date", "Resolution": "360 m"},
    {"Satellite": "IRS-1A", "Availability": "4-Apr-1988 - 28-May-1991", "Resolution": "36 m - 73 m"},
    {"Satellite": "IRS-1B", "Availability": "2-Oct-1991 - 9-Sep-2001", "Resolution": "36 m - 73 m"},
    {"Satellite": "IRS-1C", "Availability": "14-Nov-1996 - 20-Sep-2007", "Resolution": "5.8 m - 56 m"},
    {"Satellite": "IRS-1D", "Availability": "1-Jan-1998 - 20-Sep-2007", "Resolution": "5.8 m - 56 m"},
    {"Satellite": "JPSS1", "Availability": "15-Jan-2021 - till date", "Resolution": "375 m - 750 m"},
    {"Satellite": "KompSat-3", "Availability": "1-Jan-2018 - 29-May-2020", "Resolution": "0.55 m"},
    {"Satellite": "KompSat-3A", "Availability": "1-Jan-2018 - 31-May-2020", "Resolution": "0.55 m"},
    {"Satellite": "LandSat-8", "Availability": "1-Jan-2017 - till date", "Resolution": "30 m"},
    {"Satellite": "LandSat-9", "Availability": "1-Apr-2022 - till date", "Resolution": "30 m"},
    {"Satellite": "NOAA-11", "Availability": "25-Aug-1994 - 13-Sep-1994", "Resolution": "1000 m"},
    {"Satellite": "NOAA-12", "Availability": "14-Sep-1994 - 4-Nov-1995", "Resolution": "1000 m"},
    {"Satellite": "NOAA-14", "Availability": "3-Apr-1995 - 22-Sep-2010", "Resolution": "1000 m"},
    {"Satellite": "NOAA-16", "Availability": "20-Jun-2001 - 11-Aug-2005", "Resolution": "1000 m"},
    {"Satellite": "NOAA-17", "Availability": "20-Sep-2005 - 13-Apr-2010", "Resolution": "1000 m"},
    {"Satellite": "NOAA-18", "Availability": "1-Oct-2005 - 9-Oct-2009", "Resolution": "1000 m"},
    {"Satellite": "NOAA-19", "Availability": "29-Apr-2010 - 29-Oct-2014", "Resolution": "1000 m"},
    {"Satellite": "Novasar-1", "Availability": "1-Oct-2019 - till date", "Resolution": "6 m - 30 m"},
    {"Satellite": "OceanSat-1", "Availability": "1-Jul-1999 - 29-Jul-2009", "Resolution": "360 m"},
    {"Satellite": "OceanSat-2", "Availability": "31-Dec-2009 - 3-May-2023", "Resolution": "360 m"},
    {"Satellite": "RISAT-1", "Availability": "1-Jul-2012 - 30-Sep-2016", "Resolution": "3 m - 30 m"},
    {"Satellite": "ResourceSat-1", "Availability": "7-Dec-2003 - 18-Nov-2023", "Resolution": "5.8 m - 56 m"},
    {"Satellite": "ResourceSat-2", "Availability": "8-May-2011 - till date", "Resolution": "5.8 m - 24 m"},
    {"Satellite": "ResourceSat-2A", "Availability": "18-Dec-2016 - till date", "Resolution": "5.8 m - 56 m"},
    {"Satellite": "Sentinel-1A", "Availability": "9-Oct-2019 - till date", "Resolution": "20 m"},
    {"Satellite": "Sentinel-1B", "Availability": "4-Oct-2019 - 23-Dec-2021", "Resolution": "20 m"},
    {"Satellite": "Sentinel-2A", "Availability": "1-Oct-2019 - till date", "Resolution": "10 m"}
])

def satellite_info_component(selected_satellite):
    # Filter the DataFrame for the selected satellite
    satellite_info = satellite_data[satellite_data['Satellite'] == selected_satellite]
    
    if not satellite_info.empty:
        st.subheader(f"Information for {selected_satellite}")
        st.write(f"**Availability:** {satellite_info['Availability'].values[0]}")
        st.write(f"**Resolution:** {satellite_info['Resolution'].values[0]}")
    else:
        st.warning(f"No information available for {selected_satellite}")

def initialize_sessionState():
    if st.session_state.get("zoom_level") is None:
        st.session_state["zoom_level"] = 4
    if st.session_state.get("aoi") is None:
        st.session_state["aoi"] = ''

def uploaded_file_to_gdf(data, crs):
    try:
        file_extension = os.path.splitext(data.name)[1]
    except AttributeError:
        st.error("Invalid file object. Make sure you're passing a valid file.")
        return None

    file_id = str(uuid.uuid4())
    file_path = os.path.join(tempfile.gettempdir(), f"{file_id}{file_extension}")

    try:
        with open(file_path, "wb") as file:
            file.write(data.getbuffer())
    except Exception as e:
        st.error(f"Failed to write uploaded file to temporary location: {str(e)}")
        return None

    try:
        if file_extension.lower() == ".kml":
            gpd.io.file.fiona.drvsupport.supported_drivers["KML"] = "rw"
            gdf = gpd.read_file(file_path, driver="KML")
        elif file_extension.lower() == ".zip":
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                extract_dir = os.path.join(tempfile.gettempdir(), file_id)
                zip_ref.extractall(extract_dir)
            shp_files = [f for f in os.listdir(extract_dir) if f.endswith('.shp')]
            if not shp_files:
                st.error("No shapefile found in the uploaded zip file.")
                return None
            gdf = gpd.read_file(os.path.join(extract_dir, shp_files[0]))
        else:
            gdf = gpd.read_file(file_path)

        if gdf.crs is None:
            gdf.set_crs(crs, inplace=True)
        elif gdf.crs != crs:
            gdf = gdf.to_crs(crs)

        return gdf

    except Exception as e:
        st.error(f"Failed to process the uploaded file: {str(e)}")
        return None

    finally:
        # Clean up temporary files
        if os.path.exists(file_path):
            os.remove(file_path)
        if file_extension.lower() == ".zip":
            for root, dirs, files in os.walk(os.path.join(tempfile.gettempdir(), file_id), topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
            os.rmdir(os.path.join(tempfile.gettempdir(), file_id))
            
def add_aoi_selector(mapObject):
    with st.expander("Select Area of Interest (AOI)", True):
        optionsList = ["Enter URL", "Upload Shapefile/GeoJSON"]
        option = st.radio("Select Option", optionsList)
        if option == optionsList[0]:
            url_data = st.text_input("Enter GeoJSON URL","")
            if url_data == '':
                st.info("Enter URL")
            else:
                gdf = gpd.read_file(url_data)
                mapObject.add_gdf(gdf, zoom_to_layer=True, layer_name=f"{url_data.split('/')[-1].split('.')[0]}")
                st.session_state['aoi'] = gdf
        elif option == optionsList[1]:
            uploaded_file = st.file_uploader(
                    "Upload a GeoJSON or a Zipped Shapefile to use as an AOI.",
                    type=["geojson", "zip"]
                    )
            crs = {"init": "epsg:4326"}
            if uploaded_file is not None:
                try:
                    gdf = uploaded_file_to_gdf(uploaded_file, crs)
                    mapObject.add_gdf(gdf, zoom_to_layer=True, layer_name=f"{uploaded_file.name.split('.')[0]}")
                    mapObject.zoom_to_gdf(gdf)
                    st.session_state['aoi'] = gdf
                except Exception as e:
                    st.error(e)
                    st.stop()
            else:
                st.info("Upload a GeoJSON or a Zipped Shapefile.")
   
def set_params():
    with st.expander("Define Processing Parameters"):
        satellite = st.selectbox("Select Satellite", [
                "ResourceSat-1",
                "ResourceSat-2",
                "ResourceSat-2A",
                "Sentinel-2A",
                "Sentinel-2B",
                "IRS-1C",
                "IRS-1D"
            ], index=2)
        
        satellite_info_component(satellite)
        
        # Define sensor options based on the selected satellite
        if satellite in ["ResourceSat-1", "ResourceSat-2", "ResourceSat-2A"]:
            sensor_options = ["LISS3", "LISS4"]
        elif satellite in ["Sentinel-2A", "Sentinel-2B"]:
            sensor_options = ["MSI"]
        elif satellite in ["IRS-1C", "IRS-1D"]:
            sensor_options = ["PAN", "LISS3"]
        else:
            sensor_options = []  # In case none of the above conditions are met
        sensor = st.selectbox("Select Sensor", sensor_options, index=0)
        
        form = st.form(key='form')       
        fromDate = form.date_input('Start Date', date.today() - timedelta(days=30))
        toDate = form.date_input('End Date', date.today()-timedelta(days=1))
        
        # Date Validation Check
        if toDate - fromDate < timedelta(days=10):
            st.warning('Difference between selected dates is too small. There might not be any scenes available!')

        # Submit Button
        submit = form.form_submit_button('Submit')
        if submit:
            st.session_state['fromDate'] = fromDate
            st.session_state["toDate"] = toDate
            st.session_state['satellite'] = satellite
            st.session_state['sensor'] = sensor
   
def get_satellite_sensor():
    satellite = st.session_state['satellite']
    sensor = st.session_state['sensor']
    if satellite == 'ResourceSat-1' and sensor == 'LISS3':
        return "ResourceSat-1_LISS3"
    elif satellite == 'ResourceSat-1' and sensor == 'LISS4':
        return "ResourceSat-1_LISS4(MONO)"
    elif satellite == 'ResourceSat-2' and sensor == 'LISS3':
        return ["ResourceSat-2_LISS3", "ResourceSat-2_LISS3_BOA", "ResourceSat-2_LISS3_L2"]
    elif satellite == 'ResourceSat-2' and sensor == 'LISS4':
        return ["ResourceSat-2_LISS4(MX23)", "ResourceSat-2_LISS4(MX70)", "ResourceSat-2_LISS4(MX70)_L2"]
    elif satellite == 'ResourceSat-2A' and sensor == 'LISS3':
        return ["ResourceSat-2A_LISS3", "ResourceSat-2A_LISS3_BOA", "ResourceSat-2A_LISS3_L2"]
    elif satellite == 'ResourceSat-2A' and sensor == 'LISS4':
        return ["ResourceSat-2A_LISS4(MX23)", "ResourceSat-2A_LISS4(MX70)", "ResourceSat-2A_LISS4(MX70)_L2"]
    elif satellite == 'Sentinel-2A' and sensor == 'MSI':
        return ["Sentinel-2A_MSI_Level-1C", "Sentinel-2A_MSI_Level-2A"]
    elif satellite == 'Sentinel-2B' and sensor == 'MSI':
        return ["Sentinel-2B_MSI_Level-1C", "Sentinel-2B_MSI_Level-2A"]
    elif satellite == 'IRS-1C' and sensor == 'PAN':
        return ["IRS-1C_PAN"]
    elif satellite == 'IRS-1D' and sensor == 'PAN':
        return ["IRS-1D_PAN"]
    elif satellite == 'IRS-1D' and sensor == 'LISS3':
        return ["IRS-1D_LISS3"]
    else:
        st.error('Invalid selection. Please try again.')
        st.stop()

def create_payload(gdf, start_date=None, end_date=None, product="Standard"):
    # Ensure the GeoDataFrame is in EPSG:4326 (lat/lon)
    gdf = gdf.to_crs(epsg=4326)
    
    # Get the bounding box
    bounds = gdf.total_bounds
    tllon, brlat, brlon, tllat = bounds
    
    # Set default dates if not provided
    if not start_date:
        start_date = datetime.now() - timedelta(days=30)
    if not end_date:
        end_date = datetime.now()
    
    # Format dates
    sdate = start_date.strftime("%b%%2F%d%%2F%Y").upper()
    edate = end_date.strftime("%b%%2F%d%%2F%Y").upper()
    
    sat_sen = get_satellite_sensor()
    if isinstance(sat_sen, list):
        sat_sen = "%2C".join(sat_sen)
    else:
        sat_sen = sat_sen
    
    payload = {
        "prod": product,
        "selSats": sat_sen,
        "offset": "0",
        "sdate": sdate,
        "edate": edate,
        "query": "area",
        "queryType": "polygon",
        "isMX": "No",
        "tllat": tllat,
        "tllon": tllon,
        "brlat": brlat,
        "brlon": brlon,
        "filters": "%7B%7D"
    }
    return payload

import requests
def process_request():
    if isinstance(st.session_state['aoi'], gpd.GeoDataFrame):
        url = "https://bhoonidhi.nrsc.gov.in/bhoonidhi/ProductSearch"

        headers = {
            # "Accept": "application/json, text/javascript, */*; q=0.01",
            "Content-Type": "application/json",
            # "DNT": "1",
            # "Origin": "https://bhoonidhi.nrsc.gov.in",
            # "Referer": "https://bhoonidhi.nrsc.gov.in/bhoonidhi/index.html",
            # "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0",
            # "X-Requested-With": "XMLHttpRequest",
        }
        response = requests.post(url, headers=headers, json=create_payload(st.session_state["aoi"], start_date=st.session_state['fromDate'], end_date=st.session_state['toDate'], product="Standard"))

        if response.status_code == 200:
            data = response.json()
            st.session_state['response'] = data['Results']
            st.session_state['total_scenes'] = len(data['Results'])
            st.write(f"Scenes found: {len(data['Results'])}")
        else:
            st.write("Request failed. Status code:", response.status_code)

def get_scene_footprint(scene):
    coord_keys = ['ImgCrnNWLat', 'ImgCrnNWLon', 'ImgCrnNELat', 'ImgCrnNELon', 'ImgCrnSELat', 'ImgCrnSELon', 'ImgCrnSWLat', 'ImgCrnSWLon']
    
    for k in coord_keys:
        if k not in scene.keys():
            print(f"Missing key: {k}")
            return None
    # Extract coordinates and pair them
    nw = (scene['ImgCrnNWLon'], scene['ImgCrnNWLat'])
    ne = (scene['ImgCrnNELon'], scene['ImgCrnNELat'])
    se = (scene['ImgCrnSELon'], scene['ImgCrnSELat'])
    sw = (scene['ImgCrnSWLon'], scene['ImgCrnSWLat'])

    # Create a polygon from the corner coordinates
    footprint = Polygon([nw, ne, se, sw])
    return footprint

def get_scene_meta_url(scene):
    base_url = "https://bhoonidhi.nrsc.gov.in"
    dirpath = scene["dirpath"]
    filename = scene["filename"]
    meta_url = f"{base_url}/{dirpath}/{filename}.meta"
    return meta_url

def get_quicklook_url(scene):
    base_url = "https://bhoonidhi.nrsc.gov.in"
    dirpath = scene["dirpath"]
    filename = scene["filename"]
    scene_id = scene["id"]
    if scene_id == filename:
        quicklook_url = f"{base_url}/{dirpath}/{filename}.jpg"
    else:
        quicklook_url = f"{base_url}/{dirpath}/{filename}.jpeg"
    return quicklook_url

def get_overlapping_scenes():
    ids, filenames, dirpath, satellite, sensor, processing_date, prod_type, footprints = [], [], [], [], [], [], [], []
    for item in st.session_state['response']:
        ids.append(item['ID'])
        filenames.append(item['FILENAME'])
        dirpath.append(item['DIRPATH'])
        satellite.append(item['SATELLITE'])
        sensor.append(item['SENSOR'])
        processing_date.append(item['DOP'])
        prod_type.append(item['PRODTYPE'])
        footprints.append(get_scene_footprint(item))
        
    # Create a GeoDataFrame
    gdf = gpd.GeoDataFrame(
        {
            'id': ids,
            'filename': filenames,
            'dirpath': dirpath,
            'satellite': satellite,
            'sensor': sensor,
            'processing_date': processing_date,
            'prod_type': prod_type,
            'geometry': footprints
        }
    )
    # Find Scenes Overlapping with Study Area
    scenes = gdf[gdf['geometry'].intersects(st.session_state['aoi'].geometry[0])]
    
    # Get Scene Metadata
    scenes["metadata"] = scenes.apply(get_scene_meta_url, axis=1)

    # Add Quicklook URL
    scenes["quicklook"] = scenes.apply(get_quicklook_url, axis=1)

    scenes.set_crs('epsg:4326', inplace=True)   
    
    return scenes 
    
# Function to create HTML content for popup
def create_popup_html(properties):
    filename = properties['filename']
    satellite = properties['satellite']
    sensor = properties['sensor']
    processing_date = properties['processing_date']
    metadata_url = properties['metadata']
    quicklook_url = properties['quicklook']
    
    html = f"""
    <b>Filename:</b> {filename}<br>
    <b>Satellite:</b> {satellite}<br>
    <b>Sensor:</b> {sensor}<br>
    <b>Processing Date:</b> {processing_date}<br>
    <b></b> <a href="{metadata_url}" target="{metadata_url}">View Metadata</a><br>
    <b></b> <a href="{quicklook_url}" target="_blank">View Quicklook</a>
    """
    return html    
    
    
def add_scenes_to_map(m):
    scenes = get_overlapping_scenes()
    
    # Add Scenes to Map based on Product Type
    for prod_type in scenes['prod_type'].unique():
        scenes_of_type = scenes[scenes['prod_type'] == prod_type]
        
        style = {
            "fillColor": "#ff0000", 
            "color": "black", 
            "weight": 0.2, 
            "dashArray": "3, 3", 
            "fillOpacity": 0.1
        }

        # Create a FeatureGroup for the product type
        feature_group = folium.FeatureGroup(name=f"Footprints - {prod_type}")

        for _, row in scenes_of_type.iterrows():
            properties = row.to_dict()
            popup_html = create_popup_html(properties)
            
            geojson = folium.GeoJson(
                row.geometry,
                style_function=lambda x: style,
                highlight_function=lambda x: {'weight': 3, 'color': 'red'},
                zoom_on_click=True,
                popup=folium.Popup(folium.Html(popup_html, script=True), max_width=800)
            )

            geojson.add_to(feature_group)

        feature_group.add_to(m)