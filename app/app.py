import os
import shutil
import yaml
import json

import streamlit as st
from streamlit_option_menu import option_menu

from analyzer import CompetitorAnalyzer
from llm import LLMModel


DEFAULT_ROOT_FOLDER = "results"
LOGO_PATH = "logo.png"


def main():
    st.set_page_config(page_title="Comperator - Outsmart Your Competitors", layout="wide")
    
    # Set color scheme
    primary_color = "#2a7fff"  # Blue
    secondary_color = "#1fd160"  # Green
    
    # Add logo to the sidebar
    if os.path.exists(LOGO_PATH):
        with st.sidebar:
            st.image(LOGO_PATH, use_column_width=True)
    else:
        st.warning("Logo image not found.")
    
    # Sidebar
    with st.sidebar:
        selected_page = option_menu(
            menu_title=None,
            options=["Home", "Settings", "Competitors", "Analysis"],
            icons=["house", "gear", "people", "graph-up"],
            default_index=0,
            styles={
                "container": {"padding": "5!important", "background-color": "#f5f5f5"},
                "icon": {"color": primary_color, "font-size": "25px"},
                "nav-link": {"font-size": "16px", "text-align": "left", "margin": "0px", "--hover-color": "#eee"},
                "nav-link-selected": {"background-color": primary_color},
            }
        )
    
    if selected_page == "Home":
        home_page(primary_color, secondary_color)
    elif selected_page == "Competitors":
        competitors_page(primary_color, secondary_color)
    elif selected_page == "Analysis":
        analysis_page(primary_color, secondary_color)
    elif selected_page == "Settings":
        settings_page(primary_color, secondary_color)


def home_page(primary_color, secondary_color):
    st.title("Welcome to Comperator")
    st.write("Analyze your competitors and gain valuable insights to stay ahead in your market.")

    st.divider()

    st.header("My Product", anchor="my-product")
    
    # Load existing product information
    product_info = load_product_info()
    
    # Display current product information
    if product_info:
        st.subheader("Current Product Information")
        st.info(f"**Name:** {product_info['name']}\n\n**Description:** {product_info['description']}")
    
    # Input fields for product name and description
    st.subheader("Update Product Information")
    with st.form(key="product_info_form"):
        product_name = st.text_input("Product Name", value=product_info['name'] if product_info else "")
        product_description = st.text_area("Product Description", value=product_info['description'] if product_info else "")
        submit_button = st.form_submit_button(label="Save Product Information")
    
    if submit_button:
        product_info = {
            "name": product_name,
            "description": product_description
        }
        save_product_info(product_info)
        st.success("Product information saved successfully!")
        
        # Trigger a rerun of the app to refresh the page content
        st.experimental_rerun()


def competitors_page(primary_color, secondary_color):
    st.title("Competitors")
    
    # Load competitors
    competitors = load_competitors()
    
    # Display competitors in a visually appealing structure
    if competitors:
        st.subheader("Competitor List")
        
        # Create a container for the competitors
        with st.container():
            selected_competitors = []
            
            # Display each competitor in an expander
            for index, competitor in enumerate(competitors):
                with st.expander(competitor["name"], expanded=False):
                    col1, col2 = st.columns(2)
                    
                    # Display competitor details in the first column
                    with col1:
                        st.markdown(f"**Allowed Domains:**\n{', '.join(competitor['allowed_domains'])}")
                        st.markdown(f"**Start URLs:**\n{', '.join(competitor['start_urls'])}")
                    
                    # Display the checkbox in the second column
                    with col2:
                        selected = st.checkbox("Select for removal", key=f"checkbox_{index}")
                        if selected:
                            selected_competitors.append(competitor)
            
            # Remove selected competitors
            if selected_competitors:
                remove_button = st.button("Remove Selected", key="remove_selected")
                if remove_button:
                    for competitor in selected_competitors:
                        competitors.remove(competitor)
                    save_competitors(competitors)
                    st.success(f"{len(selected_competitors)} competitor(s) removed successfully!")
                    st.experimental_rerun()
    else:
        st.info("No competitors found. Add a competitor using the form below.")
    
    # Add a new competitor
    st.subheader("Add Competitor")
    with st.form(key="add_competitor_form"):
        name = st.text_input("Name")
        domains = st.text_input("Allowed Domains (comma-separated)")
        urls = st.text_input("Start URLs (comma-separated)")
        submit_button = st.form_submit_button("Add Competitor")
    
    if submit_button:
        competitor = {
            "name": name,
            "allowed_domains": domains.split(","),
            "start_urls": urls.split(",")
        }
        competitors.append(competitor)
        save_competitors(competitors)
        st.success(f"Competitor '{name}' added successfully!")
        st.experimental_rerun()


def analysis_page(primary_color, secondary_color):
    st.title("Analysis")
    
    # Select a competitor for analysis
    competitors = load_competitors()
    selected_competitor = st.selectbox("Select Competitor", [c["name"] for c in competitors])

    product_info = load_product_info()
    product_name = product_info['name']
    product_desc = product_info['description']

    config = load_config()
    languages = config["settings"]["languages"]
    max_pages = config["settings"]["max_pages"]
    llm_model = LLMModel(config["openai"]["api_url"], config["openai"]["api_key"], config["llm"]["model_name"])
    
    start_button = st.button("Start Analysis", key="start_analysis")
    
    if start_button:
        competitor = next(c for c in competitors if c["name"] == selected_competitor)

        compat_name = competitor["name"]
        allowed_domains = competitor["allowed_domains"]
        start_urls = competitor["start_urls"]

        analyzer = CompetitorAnalyzer(llm_model=llm_model, 
                                      product_name=product_name, 
                                      product_desc=product_desc)
        
        base_folder = f"{DEFAULT_ROOT_FOLDER}/{compat_name}"
        shutil.rmtree(base_folder, ignore_errors=True)
        os.makedirs(base_folder)

        with st.spinner("Analyzing competitor..."):
            analysis_res_file, wordcloud_file, _, _ = analyzer.analyze(base_folder=base_folder, name=compat_name, 
                                                                       allowed_domains=allowed_domains, start_urls=start_urls, 
                                                                       languages=languages, max_pages=max_pages)
        
        # Display analysis results and word cloud side by side
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Analysis Results")
            
            # Read the competitor analysis text from the saved file
            if os.path.exists(analysis_res_file):
                with open(analysis_res_file, "r") as f:
                    analysis_text = f.read()
                
                # Split the analysis text into sections
                sections = analysis_text.split("\n\n")
                st.markdown(sections[0])

                # Display each section in an expander
                for section in sections[1:]:
                    lines = section.strip().split("\n")
                    if lines:
                        title = lines[0].strip("1234567890. ")
                        content = "\n".join(lines[1:])
                        with st.expander(title, expanded=True):
                            st.markdown(content)
            else:
                st.warning("Analysis result not found.")
        
        with col2:
            st.subheader("Word Cloud")
            
            # Display the word cloud image from the saved file
            if os.path.exists(wordcloud_file):
                st.image(wordcloud_file, use_column_width=True)
            else:
                st.warning("Word cloud image not found.")


def settings_page(primary_color, secondary_color):
    st.title("Settings")
    
    # Load existing settings
    config = load_config()
    
    # OpenAI API settings
    st.subheader("OpenAI API Settings")
    api_url = st.text_input("API URL", value=config["openai"]["api_url"])
    api_key = st.text_input("API Key", type="password", value=config["openai"]["api_key"])
    
    # LLM settings
    st.subheader("LLM Settings")
    llm_model = st.text_input("LLM Model Name", value=config["llm"]["model_name"])
    
    # Other settings
    st.subheader("Other Settings")
    max_pages = st.number_input("Max Pages to Analyze", value=config["settings"]["max_pages"], min_value=1)
    languages = st.text_input("Languages (comma-separated)", value=",".join(config["settings"]["languages"]))
    
    save_button = st.button("Save Settings", key="save_settings")
    
    if save_button:
        settings = {
            "openai": {
                "api_url": api_url,
                "api_key": api_key
            },
            "llm": {
                "model_name": llm_model
            },
            "settings": {
                "max_pages": max_pages,
                "languages": languages.replace(" ", "").split(","),
            }
        }
        save_config(settings)
        st.success("Settings saved successfully!")


def load_config():
    try:
        with open(f"{DEFAULT_ROOT_FOLDER}/config.yaml", "r") as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        config = {
            "openai": {
                "api_url": "",
                "api_key": ""
            },
            "llm": {
                "model_name": "gpt-3.5-turbo"
            },
            "settings": {
                "max_pages": 10,
                "languages": ["en"],
            }
        }
        save_config(config)
    return config

def save_config(config):
    with open(f"{DEFAULT_ROOT_FOLDER}/config.yaml", "w") as f:
        yaml.dump(config, f)

def load_competitors():
    try:
        with open(f"{DEFAULT_ROOT_FOLDER}/competitors.json", "r") as f:
            competitors = json.load(f)
    except FileNotFoundError:
        competitors = []
    return competitors

def save_competitors(competitors):
    with open(f"{DEFAULT_ROOT_FOLDER}/competitors.json", "w") as f:
        json.dump(competitors, f)

def load_product_info():
    try:
        with open(f"{DEFAULT_ROOT_FOLDER}/product_info.json", "r") as f:
            product_info = json.load(f)
    except FileNotFoundError:
        product_info = {"name": "BestApp", "description": "Best AI BI tool."}
        save_product_info(product_info)
    return product_info

def save_product_info(product_info):
    with open(f"{DEFAULT_ROOT_FOLDER}/product_info.json", "w") as f:
        json.dump(product_info, f)

if __name__ == "__main__":

    # Create the "DEFAULT_ROOT_FOLDER" folder if it doesn't exist
    if not os.path.exists(DEFAULT_ROOT_FOLDER):
        os.makedirs(DEFAULT_ROOT_FOLDER, exist_ok=True)
    main()