# -*- coding: utf-8 -*-
from elsapy.elssearch import ElsSearch
from elsapy.elsdoc import AbsDoc
import re
import sys
from pymed import PubMed
import pandas as pd
from elsapy.utils import recast_df

## попробовать грузить инфу с помощью requests и html (beautifulsoup)
fields = ['ID', 'TH', 'AU', 'TI', 'JN', 'PY', 'VL', 'PG', 'RL', 'EA', 'AD',
          'AB', 'ST1', 'ST2', 'ST3', 'SL', 'AG', 'MF', 'NMRH', 'NMRC', 'NMRT', 'NMRS',
          'SO', 'KD', 'OTI', 'DSS', 'HO', 'NC', 'CC', 'MT', 'BA', 'EI', 'BG', 'SY', 
          'KW', 'NT', '3D', 'RR', 'DB', 'TAX', 'U1', 'U2', 'U3', 'U4', 'U5', 'U6']

class LoadInfo:
    def __init__(self, article, ID, name, data, mode, _output = None, _input = None):
        self.template = {field : '' for field in fields}
        self.template['ID'] = ID
        self.template['U1'] = name
        self.template['U2'] = data
        self.article = article
        self.PMID = None
        self.data = None
        self.DOI = None
        self.mode = mode
        self.counter = 0
        self.tim = _output
        if _input:
            self.tims = _input
        else:
            self.tims = sys.stdin
        
        
        
    def load_data_scopus(self, client):
        ##load data from scopus
        if self.mode == 'name':
            doc_srch = ElsSearch(f"Title({self.article})",'scopus')
            try:
                doc_srch.execute(client)
                result = doc_srch.results
                if 'error' in result[0]:
                    doc_srch = ElsSearch(f"Title-abs-key({self.article})", 'scopus')
                    doc_srch.execute(client, get_all = True)
                    result = doc_srch.results
                    if 'error' in result[0]:
                        self.tim.write(f'Не найдено ни одной статьи для "{self.article}".')
                        return
                elif len(result) >= 20:
                    self.tim.write(f'Найдено больше 20 статей для "{self.article}". Скорее всего, название неспецифично, используйте DOI.')
                    return
                else:
                    if len(result) > 1:
                        article = self.article.lower()
                        count = 0
                        index = None
                        for ind in range(len(result)):
                            art =  result[ind]['title'].lower()
                            if art[-1] == '.':
                                art = art[:-1]
                            if art == article:
                                count +=1
                                index = ind
                        if count >1:
                            self.tim.write(f'Найдено {count} статей с такими же именами как "{self.article}". Используйте DOI.')
                            return
                        elif index is None:
                            self.tim.write(f'Не найдено ни одной статьи для "{self.article}".')
                            return
                        else:
                            result = result[ind]
                    else:
                        result = result[0]
                return re.findall(r'[0-9]+', result['dc:identifier'])[0]
            except:
                self.tim.write(f'Ошибка при поиске "{self.article}".')
                return 
        if self.mode == 'doi':
            doc_srch = ElsSearch(f"DOI({self.article})", 'scopus')
            doc_srch.execute(client, get_all = True)
            result = doc_srch.results
            if 'error' in result[0]:
                self.tim.write(f'Не найдено статей для "{self.article}".')
                return
            result = result[0]
            try:
                return re.findall(r'[0-9]+', result['dc:identifier'])[0]
            except KeyError as e:
                self.tim.write('Кажется, вы не подключены к SCOPUS. Для корректного доступа к нужной информации необходима подписка на SCOPUS.')
                return e
            
    def check_PMID(self, result):
        return result['doi'].upper() == self.DOI.upper()
        
            
    def load_data_pubmed(self):
        pubmed = PubMed(tool="MyTool", email="my@email.address")
        if self.mode == 'name':
            query = f"{self.article}[Title]"
            results_pub = pubmed.query(query, max_results=500)
            result = []
            for artic in results_pub:
                result.append(artic.toDict())
            if len(result) == 0:
                return
            elif len(result) > 1:
                article = self.article.lower()
                count = 0
                index = None
                for ind in range(len(result)):
                    art= result[ind]['title'].lower()
                    if art[-1] == '.':
                        art = art[:-1]
                    if art == article:
                        count +=1
                        index = ind
                if count >1:
                    self.tim.write(f'Не удалось подгрузить PMID для "{self.article}". Используйте DOI.')
                    return -1
                elif index is None:
                    return
                else:
                    if self.check_PMID(result[index]):
                        return result[index]
                    else:
                        self.tim.write('Не удалось подгрузить PMID для "{self.article}". Используйте DOI.')
                        return -1
            else:
                return result[0]
        if self.mode == 'doi':
            query = f"{self.article}[DOI]"
            results_pub = pubmed.query(query, max_results=500)
            result = []
            for artic in results_pub:
                result.append(artic.toDict())
            return result[0] if len(result) >0 else None
        
    def find_article_scopus(self, scopus_id, client):
        scp_doc = AbsDoc(scp_id = scopus_id)
        scp_doc.read(client)
        self.data = scp_doc.data
        
    def load_author(self):
        list_auth = self.data['authors']['author']
        AU = ''
        for author in list_auth:
            name = author['preferred-name']['ce:indexed-name']
            name = name.replace('.', '')
            AU += f'{name}, '
        AU = AU[:-2]
        self.template['AU'] = AU
    
    def load_title(self):
        TI = self.data['item']['bibrecord']['head']['citation-title']
        self.template['TI'] = TI
        
    def load_journal(self):
        JN = self.data['coredata']['prism:publicationName']
        self.template['JN'] = JN
        
    def load_year(self):
        PY = self.data['item']['bibrecord']['head']['source']['publicationdate']['year']
        self.template['PY'] = PY
        
    def load_volume(self):
        volume = self.data['item']['bibrecord']['head']['source']['volisspag']['voliss']
        if '@issue' in volume:
            VL = f"{volume['@volume']}({volume['@issue']})"
        else:
            VL = volume['@volume']
        self.template['VL'] = VL
        
    def load_pages(self):
        p1 = self.data['item']['bibrecord']['head']['source']['volisspag']['pagerange']['@first']
        p2 = self.data['item']['bibrecord']['head']['source']['volisspag']['pagerange']['@last']
        PG = f'{p1}-{p2}'
        self.template['PG'] = PG
        
    
    def load_RL(self):
        self.DOI = self.data['coredata']['prism:doi']
        result = self.load_data_pubmed()
        if result == -1:
            return -1
        elif result:
            self.PMID = result['pubmed_id']
            if len(result['pubmed_id']) >10:
                self.tim.write(f'\nПРЕДУПРЕЖДЕНИЕ! Не удалось подгрузить PMID для статьи "{self.article}". Необходимо заполнить его вручную.')
                RL = f'DOI: {self.DOI}'
                self.PMID=None
            else:
                RL = f'PMID: {self.PMID}, DOI: {self.DOI}'
        else:
            RL = f'DOI: {self.DOI}'
        self.template['RL'] = RL
         
    def load_address(self):
        Ad = self.data['item']['bibrecord']['head']['author-group']
        AD = ''
        if type(Ad) == list:
            for group in Ad:
                if 'affiliation' in group:
                    new = group['affiliation']
                    AD += self.parse(new)
        elif type(Ad) == dict:
            if 'affiliation' in Ad:
                new = Ad['affiliation']
                AD += self.parse(new)
        AD = AD[:-2]
        AD = AD.replace('United States', 'US')
        AD = AD.replace('United Kingdom', 'UK')
        AD = AD.replace('The Republic of China', 'China')
        self.template['AD'] = AD
        
    def parse(self, new):
        if 'organization' not in new:
            return ''
        else:
            try:
                if type(new['organization']) == list:
                    return f'{new["organization"][0]["$"]}, {new["organization"][1]["$"]}, {new["city-group"]}, {new["country"]}; '
                elif type(new['organization']) == dict:
                    return f'{new["organization"]["$"]}, {new["city-group"]}, {new["country"]}; '
            except:
                if self.counter == 0:
                    self.tim.write(f'ПРЕДУПРЕЖДЕНИЕ! Адреса для "{self.article}" могут быть указаны неверно из за некорректности данных в SCOPUS API. Сверьте AD со статьей.')
                    self.counter +=1
                return ''
 

    def load_abstract(self):
        AB = self.data['item']['bibrecord']['head']['abstracts']
        self.template['AB'] = AB
        
    def load_keyw(self):
        if self.data['authkeywords']:
            lz = self.data['authkeywords']['author-keyword']
            KW = ''
            for keyword in lz:
                KW += keyword['$'] + ', '
            self.template['KW'] = KW[:-2]
        
    def last_fields(self):
        if self.PMID:   
            U6 = f'{self.PMID}.pdf'
        else:
            U6 = f"id_{self.template['ID']}.pdf"
        self.template['U6'] = U6 





