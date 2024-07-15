import json
from enum import Enum

from llm import LLMModel


SYS_PROMPT = """As a Content Classifier, your task is to classify the given text into one of 
    the predefined content types. The available content types are:

    {content_types}. 

    Read the text carefully and determine the most appropriate content type 
    based on the information provided. Output ONLY the classification result in 
    JSON format with the key "content_type" and the corresponding normalized value.
    Do not include any explanations or additional text. Exmaple output:

    ```json
    {{"content_type": "<product_description|service_description|blog_post|...|others>"}}
    ````
    """


class ContentTypes(str, Enum):
    product = "product_description"
    service = "service_description"
    blog = "blog_post"
    about = "about_us"
    contact = "contact_information"
    testimonial = "testimonial"
    faq = "faq"
    price = "pricing_information"
    team = "team_introduction"
    others = "others"


class ContentClassifier:
    def __init__(self, llm_model: LLMModel) -> None:        
        self.exclude_types = [ContentTypes.blog, ContentTypes.contact, 
                              ContentTypes.testimonial, ContentTypes.faq, 
                              ContentTypes.price, ContentTypes.team, 
                              ContentTypes.contact]
        
        content_types = [content_type.value for content_type in ContentTypes if content_type not in self.exclude_types]
        self.sys_prompt = SYS_PROMPT.format(content_types=", ".join(content_types))
        self.llm_model = llm_model
  
    def classify(self, content: str) -> ContentTypes:
        response = self.llm_model.chat(content, self.sys_prompt, 
                                       64, 0.) 

        res = response.choices[0].message.content
        # Remove the newline character and the end-of-text identifier
        res = res.strip().replace("<|eot_id|>", "")

        # Parse the JSON string
        res_dict = json.loads(res)
        return ContentTypes(res_dict['content_type'])