from typing import TypedDict, Annotated
from pydantic import BaseModel
import operator

def replace_or_add(existing: list, new: list | dict) -> list:
    """Se riceve un dict con 'replace': True, sovrascrive. Altrimenti appende."""
    if isinstance(new, dict) and new.get("replace"):
        return new["value"]
    return existing + new

class Article(TypedDict):

    titolo:str
    tags:list[str]
    news: bool
    date: str


class Next_Article(TypedDict):

    next_article_tags:list[str]
    reasoning: str


class Search_Queries(TypedDict):

    query_list: list[str]
    reasoning: str


class Single_Result(TypedDict):

    titolo: str
    sintesi: str
    url: str
    id: str


class Search_Results(BaseModel):

    query: str
    results: list[Single_Result]
    

class MagazineState(TypedDict):

    history:list[Article] # prendo i dati dal csv

    next_article_idea: Next_Article # idea data dal data scientist

    queries: Search_Queries #queries per la ricerca delle notizie

    #---------------------------------

    news: Annotated[list[Search_Results], replace_or_add] #lista delle notizie divise per query

    next_article_news: Single_Result # singolo risultato scelto per essere pubblicato

    next_article_content: str #contenuto del prossimo articolo
    #---------------------------------
    
    corrections: str # correzioni per i retry



class WorkerState(TypedDict):

    tags: list[str] #-> tags dell'articolo

    query: str

    id_number: int

    date: str #-> data di oggi

    news: Annotated[list[Search_Results], replace_or_add]