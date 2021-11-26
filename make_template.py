# -*- coding: utf-8 -*-
import download
import argparse
from utils import load_client
import codecs

def main():
    myparser = argparse.ArgumentParser()
    myparser.add_argument('-f', '--filepath', type=str, default = 'input.txt', help='input file in .txt format containing list of articles')
    myparser.add_argument('-id', '--id', type=int, default=1, help='starting ID')
    myparser.add_argument('-n', '--name', type=str, default='Dow', help='your name for U1 field')
    myparser.add_argument('-d', '--date', type=str, default='01.01.2021', help="data for U2 field in format 'dd.mm.yyyy'")
    myparser.add_argument('-m', '--mode', type=str, default='name', help='mode of search, possible options: name, doi')
    myparser.add_argument('-names', '--names', type = list, default = '')
    myparser.add_argument('-t', '--target', type = str, default = '.')
    pars = myparser.parse_args()
    return pars

def load(pars, _output=None, _input = None):
    client = load_client()
    pars.articles = []
    if pars.filepath:
        with codecs.open(pars.filepath, 'r', 'utf-8') as f:
            for line in f:
                pars.articles.append(line.rstrip())
    elif pars.names:
        pars.articles = pars.names
    for article in pars.articles:
        signal = download.load(client, article, pars.id, pars.name, pars.date, pars.mode, _output, _input)
        if signal ==-1:
            break
        elif signal == None:
            pars.id +=1
        
if __name__ == '__main__':
    pars = main()
    load(pars)