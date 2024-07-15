# Competitor Analysis Application

## Overview
The Competitor Analysis Application is a useful tool that utilizes Large Language Models (LLMs) to perform comprehensive competitor analysis. It crawls competitor websites, extracts relevant content, classifies the content, generates summaries, and provides a comparative analysis of the competitor's product features against your own product. The application also includes a web-based interface built with Streamlit for easy interaction and visualization of the analysis results.

## Features
- Web crawling and content extraction from competitor websites
- Content classification into predefined categories
- Text summarization of extracted content
- Word cloud generation for visual representation of competitor's content
- Comparative analysis of competitor's product features against your product
- Integration with OpenAI's LLM for natural language processing tasks
- Web-based interface using Streamlit for easy interaction and result visualization

## Installation
1. Clone the repository:
   ```
   git clone https://github.com/your-username/competitor-analysis-app.git
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up the configuration file:
   - Create a `config.yaml` file in the project root directory.
   - Specify the following configuration parameters:
     - `competitors`: List of competitors with their name, allowed domains, and start URLs.
     - `application`: Application-specific settings such as LLM model name, languages, root folder, and maximum pages to crawl.
     - `product`: Your product's name and description.

4. Set up the environment variables:
   - Create a `.env` file in the project root directory.
   - Specify the following environment variables:
     - `URL`: The base URL of the OpenAI API.
     - `API_KEY`: Your OpenAI API key.

## Usage
1. Run the Streamlit application:
   ```
   streamlit run app/app.py
   ```

   This will start the web-based interface for the Competitor Analysis Application.

2. Use the Streamlit interface to:
   - Select competitors to analyze
   - Initiate the competitor analysis process
   - View the analysis results, including:
     - Crawled content for each competitor
     - Word cloud image for each competitor
     - Summaries of the extracted content
     - Comparative analysis of your product against each competitor

3. Interact with the visualizations and explore the analysis results through the user-friendly Streamlit interface.

## Modules

### `app.py`
The main Streamlit application file that creates the web-based interface for the Competitor Analysis Application. It allows users to select competitors, initiate the analysis process, and visualize the results.

### `main.py`
The main entry point of the application. It loads the configuration, initializes the LLM model, and orchestrates the competitor analysis process.

### `analyzer.py`
The core module responsible for performing the competitor analysis. It integrates various components such as the crawler, summarizer, classifier, and LLM to analyze competitor websites and generate insights.

### `crawler.py`
The web crawling module that extracts content from competitor websites. It utilizes the `BeautifulSoup` library to parse HTML and extract relevant text content.

### `summarizer.py`
The text summarization module that generates concise summaries of the extracted content using the LLM model.

### `classifier.py`
The content classification module that categorizes the extracted content into predefined content types using the LLM model.

### `llm.py`
The LLM module that provides an interface to interact with the OpenAI API for generating chat completions. It is implemented as a singleton class to ensure a single instance throughout the application.

### `wordcloud_generator.py`
The word cloud generation module that creates a visual representation of the most frequent words in the extracted content. It uses the `WordCloud` library to generate the word cloud image.

### `comparative_analysis.py`
The comparative analysis module that compares the features and characteristics of your product against the competitors' products. It utilizes the LLM model to generate insights and highlight the unique selling points of your product.

## Dependencies
- Python 3.7+
- OpenAI API
- BeautifulSoup
- langdetect
- WordCloud
- PyYAML
- python-dotenv
- Streamlit

## License
This project is licensed under the [MIT License](LICENSE).

## Contributing
Contributions are welcome! If you find any issues or have suggestions for improvement, please open an issue or submit a pull request.
