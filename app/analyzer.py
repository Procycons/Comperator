       
import logging
import json

from wordcloud import WordCloud

from crawler import BeautifulSoupCrawler
from summarizer import Summarizer
from classifier import ContentClassifier
from llm import LLMModel
from utils import normalize_text, nltk_lan_mapper


AVG_WORD_LEN = 7 # chars
MAX_NUM_WORDS = 4000 # words
MAX_TXT_LENGTH = AVG_WORD_LEN * MAX_NUM_WORDS # chars


logger = logging.getLogger(__name__)


SYS_PROMPT = """As a Competitive Analyst, your task is to compare the features of our product {product_name} 
      with the features of the competitor product following .

      {product_name} descirption and features:
      {product_description}

      Provide a comparative analysis of the features, 
      highlighting the similarities, differences, 
      and any unique aspects of each product. 
      Focus on the key areas where {product_name} differentiates itself from the competitor. 
      Identify potential gaps or areas of improvement for {product_name} based on the competitor's offerings.

      Structure your analysis in the following format:
      1. Similarities:
        - Point 1
        - Point 2
        ...
      2. Differences:
        - Point 1
        - Point 2
        ...
      3. Unique aspects of {product_name}:
        - Point 1
        - Point 2
        ...
      4. Potential gaps or areas of improvement for {product_name}:
        - Point 1
        - Point 2
        ...

      Provide your analysis in a concise and clear manner, focusing on the most important points. Start directly with the first point without any introductory phrases or additional remarks."""


class CompetitorAnalyzer:
    def __init__(self, llm_model: LLMModel, product_name: str, product_desc: str) -> None:
        self.llm_model = llm_model
        product_name = product_name
        product_desc = product_desc

        self.sys_prompt = SYS_PROMPT.format(product_name=product_name, product_description=product_desc)

        # In most pages at begining only some meta infromaiton are saved
        self.txt_offset = 150 # chars

        self.summarizer = Summarizer(self.llm_model)
        self.classifier = ContentClassifier(self.llm_model)
    
    def chat(self, content):
        response = self.llm_model.chat(content, sys_prompt=self.sys_prompt, 
                                       max_token=8000, temp=0.)

        res = response.choices[0].message.content
        # Remove the newline character and the end-of-text identifier
        res = res.strip().replace("<|eot_id|>", "")
        return res

    def analyze(self, base_folder, name: str, allowed_domains: list[str], 
            start_urls: list[str], languages: list[str], 
            max_pages: int = 5):
        
        logger.info(f"Running competitor analysis for '{name}'.")

        crawler_file = f'{base_folder}/content_{name}.json'
        wordcloud_file = f'{base_folder}/wordcloud_{name}.png'
        summary_file = f"{base_folder}/summaries_{name}.json"
        res_file = f"{base_folder}/res_competitor_analysis_{name}.txt"
        
        # Start crawling
        process = BeautifulSoupCrawler(
            name=name,
            allowed_domains=allowed_domains,
            start_urls=start_urls,
            languages=languages,
            out_file=crawler_file,
            max_pages=max_pages
        )
        process.start()
        
        # Load the extracted data from the JSON file
        with open(crawler_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        ### Building the word cloud ###############################

        # Concatenate all the orignial text contents into a single string
        org_contents = " ".join([item['text_content'] for item in data])

        # normalize the text
        langs = [nltk_lan_mapper[lan] for lan in languages]
        org_contents = normalize_text(org_contents, langs)
        # remove also the name of the company
        org_contents = org_contents.replace(name, "")

        # Generate and save the word cloud
        logger.info("Generating word cloud.")
        wordcloud = WordCloud(width=800, height=800, background_color='white').generate(org_contents)
        wordcloud.to_file(wordcloud_file)

        ### Classifing the content and filtering ################

        filtered_data = []
        for item in data:
            txt = item['text_content'][self.txt_offset:]
            txt = f"url: {item['url']} \n\n {txt}"
            cls = self.classifier.classify(txt)
            if cls in self.classifier.exclude_types:
                continue
            item['class'] = cls
            filtered_data.append(item)


        ### Summarizing #########################################

        # Summarize the content of each page seperatly
        summaries = []
        for item in filtered_data:
            txt = item['text_content'][self.txt_offset:]
            summary = self.summarizer.summarize(txt)
            item['summary'] = summary
            summaries.append(item)

        # Concatenate all the text content into a single string
        content = " .".join([item['summary'] for item in summaries])
        
        content = content[:min(len(content), MAX_TXT_LENGTH)]

        # Summarize the entire company text
        summary = self.summarizer.summarize(content=content)
        summaries.append({"total_summary": summary})

        # Save the extracted data to a JSON file
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summaries, f, ensure_ascii=False, indent=4)

        ### Analyze the competitor #############################
        res = self.chat(content)

        with open(res_file, 'w', encoding='utf-8') as f:
            f.write(res)
        logger.info("Competitor analysis completed.")
        return res_file, wordcloud_file, summary_file, crawler_file

