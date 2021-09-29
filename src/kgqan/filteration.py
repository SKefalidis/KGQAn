import os
import re
from urllib.parse import urlparse

from .nlp.models import ner

def is_person(output):
    for tag in output['tags']:
        if 'PERSON' in tag:
            return True
    return False

def is_place(output):
    for tag in output['tags']:
        if 'GPE' in tag or 'FAC' in tag or 'LOC' in tag:
            return True
    return False

def is_language(output):
    for tag in output['tags']:
        if 'LANGUAGE' in tag:
            return True
    return False


def extract_resource_name_from_uri(uri: str):
    resource_URI = uri
    uri_path = urlparse(resource_URI).path
    resource_name = os.path.basename(uri_path)
    resource_name = re.sub(r'(:|_|\(|\))', ' ', resource_name)
    return resource_name


def update_results(results, answer_type):
    filtered_bindings = []
    if 'person' in answer_type:
        return filter_person(results)
    elif 'place' in answer_type:
        return filter_place(results)
    elif 'language' in answer_type:
        return filter_language(results)
    return results

def filter_person(results):
    filtered_bindings = []
    value = ""
    for binding in results['bindings']:
        if binding['uri']['type'] == 'typed-literal' and 'langString' in binding['uri']['datatype']:
            value = binding['uri']['value']
            allennlp_ner_output = ner.predict(sentence=value)
            if is_person(allennlp_ner_output):
                filtered_bindings.append(binding)
        elif binding['uri']['type'] == 'uri':
            value = extract_resource_name_from_uri(binding['uri']['value'])
            allennlp_ner_output = ner.predict(sentence=value)
            if is_person(allennlp_ner_output):
                filtered_bindings.append(binding)
        elif binding['uri']['type'] == 'literal':
            value = binding['uri']['value']
            if len(value.split()) > 5:
                continue
            allennlp_ner_output = ner.predict(sentence=value)
            if is_person(allennlp_ner_output):
                filtered_bindings.append(binding)

    return {'bindings': filtered_bindings}

def filter_place(results):
    filtered_bindings = []
    value = ""
    for binding in results['bindings']:
        if binding['uri']['type'] == 'typed-literal' and 'langString' in binding['uri']['datatype']:
            value = binding['uri']['value']
            allennlp_ner_output = ner.predict(sentence=value)
            if is_place(allennlp_ner_output) or is_person(allennlp_ner_output):
                filtered_bindings.append(binding)
        elif binding['uri']['type'] == 'uri':
            value = extract_resource_name_from_uri(binding['uri']['value'])
            allennlp_ner_output = ner.predict(sentence=value)
            if is_place(allennlp_ner_output) or is_person(allennlp_ner_output):
                filtered_bindings.append(binding)

    return {'bindings': filtered_bindings}

def filter_language(results):
    filtered_bindings = []
    value = ""
    for binding in results['bindings']:
        if binding['uri']['type'] == 'typed-literal' and 'langString' in binding['uri']['datatype']:
            value = binding['uri']['value']
            allennlp_ner_output = ner.predict(sentence=value)
            if 'language' in value or is_language(allennlp_ner_output):
                filtered_bindings.append(binding)
        elif binding['uri']['type'] == 'uri':
            value = extract_resource_name_from_uri(binding['uri']['value'])
            allennlp_ner_output = ner.predict(sentence=value)
            if 'language' in value or is_language(allennlp_ner_output):
                filtered_bindings.append(binding)
          
    return {'bindings': filtered_bindings}