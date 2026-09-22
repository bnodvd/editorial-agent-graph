from langgraph.graph import START, END, StateGraph
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command
from langgraph.graph.state import CompiledStateGraph

from src.nodes.data_nodes import get_article_history_data, save_articles_data, save_article_content_data
from src.nodes.llm_nodes import data_analyst_llm, query_generator_llm, single_searcher_llm, specific_resercher_llm
from src.nodes.action_nodes import assign_workers, route_after_choice, user_choice_action
from src.variables.state_classes import MagazineState
from src.variables.models import CONFIG


def setup_graph()-> CompiledStateGraph[MagazineState, None, MagazineState, MagazineState]:

    magazine_graph = StateGraph(MagazineState)

    magazine_graph.add_node('get_article_history_data', get_article_history_data)
    magazine_graph.add_node('data_analyst_llm', data_analyst_llm)
    magazine_graph.add_node('query_generator_llm', query_generator_llm)
    magazine_graph.add_node('single_searcher_llm', single_searcher_llm)
    magazine_graph.add_node('save_articles_data', save_articles_data)
    magazine_graph.add_node('user_choice_action', user_choice_action)
    magazine_graph.add_node('specific_resercher_llm', specific_resercher_llm)
    magazine_graph.add_node('save_article_content_data', save_article_content_data)

    magazine_graph.add_edge(START, 'get_article_history_data')
    magazine_graph.add_edge('get_article_history_data', 'data_analyst_llm')
    magazine_graph.add_edge('data_analyst_llm', 'query_generator_llm')
    magazine_graph.add_conditional_edges(
        'query_generator_llm', assign_workers, ['single_searcher_llm']
    )
    magazine_graph.add_edge('single_searcher_llm', 'save_articles_data')
    magazine_graph.add_edge('save_articles_data', 'user_choice_action')
    magazine_graph.add_conditional_edges(
        'user_choice_action', route_after_choice, ['query_generator_llm', 'specific_resercher_llm'])
    magazine_graph.add_edge('specific_resercher_llm', 'save_article_content_data')
    magazine_graph.add_edge('save_article_content_data', END)

    memory = MemorySaver()
    return magazine_graph.compile(checkpointer=memory)


def interrupt_handling(result:dict):

    limite = sum([len(news['results']) for news in result.get('news', [])])
    human_response = Command()

    print('─'*40)
    print ('Interruzione:')
    print (f"{result['__interrupt__'][0].value}")

    while True:
        user_input = input(f"->| ")

        if user_input.lower() == 'q':

            user_corrections = input(f"""Indica gentilmente le correzioni per la prossima ricerca
->|""")
            
            human_response = Command(
                resume={
                    "approved": False,
                    "user_input":user_corrections
                }
            )     
            break

        elif user_input.isdigit() and 1 <= int(user_input) <= limite:
            human_response = Command(
                resume={
                    "approved": True,
                    "user_input": user_input
                }
            )
            break
        else:
            print(f"Input non valido. Per favore inserisci un numero tra 1 e {limite} altrimenti 'q' per rieseguire la ricerca")

    return human_response


def logic(app:CompiledStateGraph[MagazineState, None, MagazineState, MagazineState], initial_state:MagazineState, initial_config = None):

    state = initial_state
    config = initial_config
        
    while True:

        result =  app.invoke(input=state, config=config)

        if result.get('__interrupt__'):
            
            state = interrupt_handling(result=result)
        else:
            break


def main():
    
    app = setup_graph()    

    logic(app, MagazineState(), CONFIG)

if __name__ == '__main__':
    main()