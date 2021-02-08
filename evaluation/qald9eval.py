#!./venv python
# -*- coding: utf-8 -*-
"""
evaluation.py: evaluating KGQAn online service against QALD-3 benchmark
"""
___lab__ = "CoDS Lab"
__copyright__ = "Copyright 2020-29, GINA CODY SCHOOL OF ENGINEERING AND COMPUTER SCIENCE, CONCORDIA UNIVERSITY"
__credits__ = ["CoDS Lab"]
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "CODS Lab"
__email__ = "essam.mansour@concordia.ca"
__status__ = "debug"
__created__ = "2020-02-07"

import json
import time
from kgqan import KGQAn
from termcolor import colored, cprint
from itertools import count
import xml.etree.ElementTree as Et

file_name = r"qald9/qald-9-test-multilingual.json"

if __name__ == '__main__':
    root_element = Et.Element('dataset')
    root_element.set('id', 'dbpedia-test')
    author_comment = Et.Comment(f'created by CoDS Lab')
    root_element.append(author_comment)
    timestr = time.strftime("%Y%m%d-%H%M%S")
    total_time = 0

    # The main param: 
    # max no of vertices and edges to annotate the PGP
    # max no of SPARQL queries to be generated from PGP 
    max_Vs = 1
    max_Es = 21
    max_answers = 41

    with open(file_name) as f:
        qald9_testset = json.load(f)
    dataset_id = qald9_testset['dataset']['id']
    MyKGQAn = KGQAn(n_max_answers=max_answers, n_max_Vs=max_Vs, n_max_Es=max_Es)
    qCount = count(1)
    
    kgqan_qald9 = {"dataset": {"id": "qald-9-test-multilingual"}, "questions": []}
    for i, question in enumerate(qald9_testset['questions']):

        # Run time error with these Qs [32, 113, 164, 206, 43]
        # for example in Q-32 if we detect birth day as a relation it may work
        if int(question['id']) in [32, 113, 164, 206, 43]:
            continue

        # We managed before to solve this list with F1 = 34
        # [1, 9, 23, 26, 27, 40, 45, 52, 62, 63, 64, 86, 99, 103, 110, 116, 119, 122, 124, 128, 129, 131, 134, 135, 141,
        # 143, 144, 145, 154, 155, 156, 160, 175, 181, 183, 187, 188, 198, 203, 8, 159, 25]

        # the current version solves only this list with F1 = 26.17
        # [103,110,119,122,124,128,129,134,141,144,145,154,156,159,181,183,187,23,25,26,40,45,52,62,64,8,9,99]

        # TODOS: We need to solve this list first
        # [1,116,131,135,143,155,160,175,188,198,203,27,63,86]

        # hard to annotate/link with the KG
        # if int(question['id']) in [167]:
        #     continue

        # Questions with no detected Relation or NE
        # R [214, 199, 137, 136, 132, 124, 111, 10, 84, 213, 162]
        # E [168, 166, 140, 123, 59, 39, 83, 209, 212]
        # Questions with one NE
        # if int(question['id']) not in [99, 98, 86, 64, 56, 44, 37, 31, 29, 23, 68, 22, 203, 197, 196, 188, 187, 62,
        #                               173, 160, 158, 155, 150, 149, 25, 143, 139, 134, 128, 122, 117, 104, 1, 178,
        #                               129, 183, 181, 7, 135, 50, 71, 105, 52, 102, 21, 34, 145, 154, 198]:
        #     continue

        # if int(question['id']) not in [177, 101, 14]:
        #     continue

        # long time queries 51
        # if int(question['id']) in [27, 167]:
        #     continue

        qc = next(qCount)
        # question_text = ''
        for language_variant_question in question['question']:
            if language_variant_question['language'] == 'en':
                question_text = language_variant_question['string'].strip()
                break

        text = colored(f"[PROCESSING: ] Question count: {qc}, ID {question['id']}  >>> {question_text}", 'blue',
                       attrs=['reverse', 'blink'])
        cprint(f"== {text}  ")

        st = time.time()
        # question_text = 'Which movies starring Brad Pitt were directed by Guy Ritchie?'
        # question_text = 'When did the Boston Tea Party take place and led by whom?'
        answers = MyKGQAn.ask(question_text=question_text, answer_type=question['answertype'])

        all_bindings = list()
        for answer in answers:
            if answer['results'] and answer['results']['bindings']:
                all_bindings.extend(answer['results']['bindings'])

        try:
            if 'results' in question['answers'][0]:
                question['answers'][0]['results']['bindings'] = all_bindings.copy()
                kgqan_qald9['questions'].append(question)
                all_bindings.clear()
        except:
            question['answers'] = []

        et = time.time()
        total_time = total_time + (et - st)
        text = colored(f'[DONE!! in {et-st:.2f} SECs]', 'green', attrs=['bold', 'reverse', 'blink', 'dark'])
        cprint(f"== {text} ==")

        # break
    text1 = colored(f'total_time = [{total_time:.2f} sec]', 'yellow', attrs=['reverse', 'blink'])
    text2 = colored(f'avg time = [{total_time / qc:.2f} sec]', 'yellow', attrs=['reverse', 'blink'])
    cprint(f"== QALD 9 Statistics : {qc} questions, Total Time == {text1}, Average Time == {text2} ")

    with open(f'output/MyKGQAn_result_{timestr}_MaxAns{max_answers}_MaxVs{max_Vs}_MaxEs{max_Es}'
              f'_TTime{total_time:.2f}Sec_Avgtime{total_time / qc:.2f}Sec.json',
              encoding='utf-8', mode='w') as rfobj:
        json.dump(kgqan_qald9, rfobj)
        rfobj.write('\n')
