from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from datetime import datetime
import json

from src.variables.models import SEARCH_MODEL, PROMPT_PATH, TAGS
from src.variables.state_classes import MagazineState, Next_Article, Search_Queries, Search_Results, WorkerState
from src.tools.utils import load_text_file
from src.tools.logging_functions import log_node, log_worker_node

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model = SEARCH_MODEL
)

@log_node(
    message='I tag del prossimo articolo sono {}\nEcco il ragionamento: {}',
    extract=lambda r: [r.get('next_article_idea').get('next_article_tags'), r.get('next_article_idea').get('reasoning')]
)
def data_analyst_llm (state:MagazineState, config):

    structured_llm = llm.with_structured_output(schema=Next_Article)

    history = str(state.get('history'))

    prompt = load_text_file(PROMPT_PATH / 'data_analyst_llm.md')

    prompt = prompt.replace('{history}', history)
    prompt = prompt.replace('{tags}', TAGS)

    response = structured_llm.invoke(input = prompt)

    return {'next_article_idea': response}



@log_node(
        message='Sono state trovate le seguenti queries: \n> {}\nEcco il ragionamento: {}',
        extract=lambda r: ['\n> '.join(r.get('queries').get('query_list')), r.get('queries').get('reasoning')]
)
def query_generator_llm(state:MagazineState, config):

    structured_llm = llm.with_structured_output(schema=Search_Queries)

    tags = str(state.get('next_article_idea').get('next_article_tags'))
    reason = str(state.get('next_article_idea').get('reasoning'))

    if state.get('corrections'):

        prompt = load_text_file(PROMPT_PATH / "query_generator_retry_llm.md")

        corrections = state.get('corrections')
        query_precedenti = str(state.get('queries').get('query_list'))

        prompt = prompt.replace('{correzioni}', corrections)
        prompt = prompt.replace('{query_precedenti}', query_precedenti)

    else:

        prompt = load_text_file(PROMPT_PATH / "query_generator_llm.md")

    prompt = prompt.replace('{tags}', tags)
    prompt = prompt.replace('{motivazione}', reason)

    response = structured_llm.invoke(input=prompt)

    return{'queries': response}



@log_worker_node
def single_searcher_llm(state:WorkerState, config):
    
    structured_llm = llm.bind(
        tools=[{"google_search": {}}],
        response_mime_type='application/json',
        response_schema=Search_Results.model_json_schema()
    )

    query = state.get('query')
    tags = state.get('tags')
    id_number = state.get('id_number')
    date = config.get('configurable').get('date')

    prompt = load_text_file(PROMPT_PATH / "single_searcher_llm.md")

    prompt = prompt.replace('{query}', query)
    prompt = prompt.replace('{data_odierna}', date)
    prompt = prompt.replace('{tags}', str(tags))
    prompt = prompt.replace('{id}', str(id_number))

    response = structured_llm.invoke(input=prompt)
    

    return {'news': [json.loads(response.content[0]['text'])]}



@log_node(
    message='Prodotto un testo di {} battute',
    extract=lambda r: [len(r.get('next_article_content'))]
)
def specific_resercher_llm(state:MagazineState, config):

    tools_llm = llm.bind_tools([{"google_search": {}}])

    date = config.get('configurable').get('date')
    tags = state.get('next_article_idea').get('next_article_tags')
    title = state.get('next_article_news').get('titolo')
    url = state.get('next_article_news').get('url')

    for news in state.get('news'):
        for result in news.get('results'):
            if result.get('titolo') == title:
                query = news.get('query')

    prompt = load_text_file(PROMPT_PATH / "specific_resercher_llm.md")

    prompt = prompt.replace('{data_odierna}', date)
    prompt = prompt.replace('{tags}', str(tags))
    prompt = prompt.replace('{titolo}', title)
    prompt = prompt.replace('{URL}', url)
    prompt = prompt.replace('{query}', query)

    response = tools_llm.invoke(input=prompt)

    return {'next_article_content': response.content[0].get('text')}