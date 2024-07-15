import os
import argparse
import yaml
import datetime
import logging 

from dotenv import load_dotenv

from analyzer import CompetitorAnalyzer
from llm import LLMModel

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def main(config_file):
    with open(config_file, "r") as f:
        config = yaml.safe_load(f)
    competitors = config['competitors']
    model_name= config['application']['llm_model_name']
    languages = config['application']['languages']
    root_folder = config["application"]["root-folder"]
    max_pages = config["application"]["max-pages"]
    product_name = config["product"]["name"]
    product_desc = config["product"]["description"]

    # Load variables from .env file
    load_dotenv()
    try:
        url = os.environ['URL']
        api_key = os.environ['API_KEY']
    except KeyError as e:
        raise ValueError(f"Missing environment variable: {e.args[0]}")

    # Create the LLM model
    llm_model = LLMModel(url, api_key, model_name)
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    root_folder = f"{root_folder}/competitor_analyze_{timestamp}"
    os.makedirs(root_folder)

    for comp in competitors:
        name = comp['name']
        allowed_domains = comp['allowed_domains']
        start_urls = comp['start_urls']

        base_folder = f"{root_folder}/{name}"
        os.makedirs(base_folder)

        # Crete and run the analyzer
        analyzer = CompetitorAnalyzer(
            llm_model=llm_model,
            product_name=product_name,
            product_desc=product_desc)
        
        analyzer.analyze(base_folder=base_folder, name=name, 
                         allowed_domains=allowed_domains, start_urls=start_urls, 
                         languages=languages, max_pages=max_pages)

    logger.info("Competio")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Competitor Analysis Application')
    parser.add_argument('-c', '--config', type=str, default='config.yaml',
                        help='Path to the configuration file (default: config.yaml)')
    args = parser.parse_args()
    config_file = args.config
    main(config_file)
