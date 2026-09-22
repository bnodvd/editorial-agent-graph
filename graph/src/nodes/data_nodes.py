from langchain_core.runnables import RunnableConfig
from langgraph.types import interrupt
from pathlib import Path
import csv

from src.variables.state_classes import Article, MagazineState
from src.tools.logging_functions import log_node



@log_node(
    message="Caricati {} articoli in history",
    extract=lambda r: [len(r.get('history', []))]
)
def get_article_history_data(state:MagazineState, config:RunnableConfig):

    path = config.get('configurable').get('input_path')
    lista_articoli = []

    with open(path, 'r', encoding='utf-8') as file:
        file_csv = csv.DictReader(file)
        for row in file_csv:
            articolo = Article(
                titolo=row['titolo'],
                tags=eval(row['tags']),
                news=bool(row['news']),
                date=row['date']
            )
            lista_articoli.append(articolo)

    return {'history': lista_articoli}



@log_node(
    message=None,
    extract=None
)
def save_articles_data(state:MagazineState, config:RunnableConfig):

    output_path = Path(config.get('configurable').get('output_path'))

    news_found = state.get('news', 'Nessuna notizia trovata')
    tags = state.get('next_article_idea', "Nessun_articolo").get('next_article_tags', "Nessun Tag")
    i = 1
    lines = []

    lines.append(f"I tag dell'articolo successivo sono: {', '.join(tags)}")
    lines.append("─" * 80)
    lines.append("Ecco i risultati delle ricerche effettuate:\n")

    for news in news_found:
        lines.append(f"→ Query di ricerca: {news['query']}")
        lines.append("#" * 80)
        
        for result in news['results']:
            result.update({'id': i})
            lines.append(f"Titolo:   {result['titolo']}")
            lines.append(f"Sintesi:  {result['sintesi']}")
            lines.append(f"URL:      {result['url']}")
            lines.append(f"ID:       {result['id']}")
            lines.append("─" * 80)
            i += 1

        
        lines.append("\n")

    output = "\n".join(lines)

    with open(output_path / 'notizie.txt', "w", encoding="utf-8") as f:
        f.write(output)
    
    print ('Notizie salvate nel file notizie.txt e pronte per essere consultati')
    
    return {'news': {'replace': True, 'value': news_found}}


@log_node(
    message=None,
    extract=None
)
def save_article_content_data(state:MagazineState, config:RunnableConfig):

    content = state.get('next_article_content')

    output_path = config.get('configurable').get('output_path')

    with open(output_path / 'content.txt', "w", encoding="utf-8") as f:
        f.write(content)

    print ('Testo salvato nel file content.txt e pronto per essere consultato')
    return {}
