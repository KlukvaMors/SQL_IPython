from IPython.core.display import display, HTML
from IPython.display import display, Markdown, Latex
from pygments.lexers import  get_lexer_by_name
from pygments.formatters import HtmlFormatter
from pygments import highlight

import pandas as pd

import sqlite3
import glob
from pathlib import Path
import re

conn = sqlite3.connect(":memory:")

def display_sql(query):
    sql_lexer = get_lexer_by_name('SQL')
    html_fmt = HtmlFormatter()
    style_def = html_fmt.get_style_defs('.highlight')
    content = f'<style>{style_def}</style>{highlight(query, sql_lexer, html_fmt)}'
    display(HTML(content))


def sql(query: str, connection=conn):
    '''Просто функция с коротким именем,
    для наглядного представления и исполнения SQL запросов'''
    display_sql(query)
    if re.search(r'^\s*select', query, re.IGNORECASE | re.MULTILINE):
        return pd.read_sql_query(query, connection)
    connection.execute(query)

 
def show(query, connection=conn):
    '''Просто функция с коротким именем,
    для наглядного представления SELECT запросов
    в виде pandas dataframe
    '''
    display_sql(query)
    return pd.read_sql_query(query, connection)


def table(table_name:str, connection=conn):
    '''Показывает содержимое таблицы 
    '''
    return show(f'SELECT * FROM {table_name}', connection)


def schema(name, connection=conn):
    '''Показывает схему таблицы'''
    c = connection.cursor()
    c.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{name}'")
    sql_schema = c.fetchall()[0][0]
    display_sql(query)


def load_sql(file_name:str, connection=conn):
    path = Path(file_name)
    if not path.exists():
        raise Exception("Указаный путь не существует")
    if not path.is_file():
        raise Exception("Указаный путь не указывает на файл")
    with path.open() as file:
        sql_schema = file.read()
        connection.executescript(sql_schema)
        display_sql(sql_schema)

def load_csv(file_name, table_name=None, connection=conn):
    path = Path(file_name)
    if not path.exists():
        raise Exception("Указаный путь не существует")
    if not path.is_file():
        raise Exception("Указаный путь не указывает на файл")
    if not table_name:
        table_name = path.stem
    df = pd.read_csv(file_name)
    df.to_sql(table_name, connection, if_exists="append", index=False)
    return df
    
