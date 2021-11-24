# -*- coding: utf-8 -*-
from search_art import LoadInfo
import codecs
import sys

def load(client, article, ID=62000, name='Andreichuk', date='01.07.2021', mode='doi', _output= None, _input = None):
    if _output:
        tim= _output
    else:
        tim = sys.stdout
    if _input:
        tims = _input
    else:
        tims = sys.stdin
    loader = LoadInfo(article, ID, name, date, mode, _output, _input)
    scp_id = loader.load_data_scopus(client)
    if scp_id == None:
        return 0
    if scp_id.__class__ == KeyError:
        return 0
    loader.find_article_scopus(scp_id, client)
    try:
        loader.load_author()
        loader.load_title()
    
    except:
        tim.write("Possiibly, you are not connected to SCOPUS")
        return -1
    try:
        loader.load_journal()
    except:
        tim.write(f'\nПРЕДУПРЕЖДЕНИЕ! Не удалось загрузить журнал для "{loader.article}"')
    try:
        loader.load_year()
    except:
        tim.write(f'\nПРЕДУПРЕЖДЕНИЕ! Не удалось загрузить год для "{loader.article}"')
    try:
        loader.load_volume()
    except:
        tim.write(f'\nПРЕДУПРЕЖДЕНИЕ! Не удалось загрузить номер издания для "{loader.article}"')
    try:
        loader.load_pages()
    except:
        tim.write(f'\nПРЕДУПРЕЖДЕНИЕ! Не удалось загрузить страницы для "{loader.article}"')
    try:
        message = loader.load_RL()
        if message == -1:
            tim.write('Статья пропущена')
            return 0   
    except:
        tim.write(f'\nПРЕДУПРЕЖДЕНИЕ! Не удалось загрузить RL для "{loader.article}"')
    try:
        loader.load_address()
    except:
        tim.write(f'\nПРЕДУПРЕЖДЕНИЕ! Не удалось загрузить адреса для "{loader.article}"')
    try:
        loader.load_abstract()
    except:
        tim.write(f'\nПРЕДУПРЕЖДЕНИЕ! Не удалось загрузить абстракт для "{loader.article}"')
    try:
        loader.load_keyw()
    except:
       tim.write(f'\nПРЕДУПРЕЖДЕНИЕ! Не удалось загрузить ключевые слова для "{loader.article}"') 
    try:
        loader.last_fields()
    except:
        tim.write(f'ПРЕДУПРЕЖДЕНИЕ! Не удалось загрузить U6 для "{loader.article}"') 
    
    
    
    
    with codecs.open('template.txt', 'a', 'utf-8') as file:
        for (x, y) in loader.template.items():
            if y:
                file.write(f'{x}: {y}\n')
            else:
                file.write(f'{x}:\n')
        file.write('\n\n')
    tim.write(f'Шаблон для "{loader.article}" добавлен')

        