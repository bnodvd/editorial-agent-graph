from langgraph.types import Send
from langgraph.types import interrupt

from src.variables.state_classes import MagazineState
from src.tools.logging_functions import log_node

@log_node(
    message=None,
    extract=None
)
def assign_workers(state:MagazineState, config):

    tags = state.get('next_article_idea').get('next_article_tags')
    query_list = state.get('queries').get('query_list')

    print(f'Inizio lavoro in parallelo di {len(query_list)} llm')

    return [Send("single_searcher_llm", {"query": query, "tags": tags, 'id_number': i}) for i, query in enumerate(query_list)]


@log_node(
    message=None,
    extract=None
)
def user_choice_action(state: MagazineState):
    
    approved = interrupt('Controlla il file.txt che trovi nella cartella Output. Se ti piacciono questi articoli scegline uno indicando il suo numero, altrimenti digita "q" e nel\'input successivo indica le correzioni per la prossima ricerca')

    if approved.get('approved'):

        choice = approved.get('user_input')

        articolo_scelto = {}
        for news in state.get('news'): 
            for notizia in news.get('results'):
                if str(notizia.get('id')) == choice:
                    articolo_scelto = notizia

        print (f'Hai scelto {articolo_scelto.get('titolo')}')


        return {'next_article_news': articolo_scelto}

    else:
        
        return {'corrections': approved.get('user_input')}

@log_node(
    message=None,
    extract=None
)
def route_after_choice(state: MagazineState):
    if state.get('next_article_news') is not None:
        return 'specific_resercher_llm'
    else:
        return 'query_generator_llm'