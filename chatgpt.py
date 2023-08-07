import openai
import json
import copy
import sys
from sentence_transformers import SentenceTransformer, util
import linecache

api_key = json.load(open("openai-key.json","r"))
openai.api_key = api_key["key"]

def PrintException():
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    print('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))


def create_debate(debate_questions, debate_intro):
    answers = {}
    answers["debate_intro"] = debate_intro

    context= {"debate_intro": debate_intro}
    for elem in debate_questions:
        history = []
        key = list(elem.keys())[0]
        for to_add in elem[key]["context"]:
            history.extend(context[to_add])
        history.append({"role": "user", "content": elem[key]["question"]})

        while True:
            error = False
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo-16k",
                    messages=history,
                    temperature=0)
            except:
                error= True
            if not error:
                break
        new_elem = copy.deepcopy(elem)
        new_elem[key]["reponse"] = response['choices'][0]['message']['content']
        answers[key]=new_elem[key]

        context[key]=[
            {"role": "user", "content": elem[key]["question"]},
            {"role": "assistant", "content": response['choices'][0]['message']['content']}]

    return {"Débat":answers}

def create_argument(argument_questions, argument_intro):
    print("CREATE ARGUMENT")
    sys.stdout.flush()
    answers = {}
    answers["argument_intro"] = argument_intro
    context= {"argument_intro": argument_intro}
    for elem in argument_questions:
        history = []
        key = list(elem.keys())[0]
        for to_add in elem[key]["context"]:
            history.extend(context[to_add])
        history.append({"role": "user", "content": elem[key]["question"]})

        while True:
            error = False
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo-16k",
                    messages=history,
                    temperature=0)
            except:
                error= True
            if not error:
                break
        new_elem = copy.deepcopy(elem)
        new_elem[key]["reponse"] = response['choices'][0]['message']['content']
        answers[key]=new_elem[key]
        context[key]=[
            {"role": "user", "content": elem[key]["question"]},
            {"role": "assistant", "content": response['choices'][0]['message']['content']}]

    return answers


def retrieve_list(content, remove_dot = True, remove_column=True):
    count = 1
    to_find = str(count) + ". "
    index = content.find(to_find)
    list_args = []
    while index != -1:
        end_arg = content.find("\n", index)
        if end_arg == -1:
            end_arg = len(content)
        argument = content[index + len(str(count))+2:end_arg].strip()
        if argument.find(".")==len(argument)-1 and remove_dot:
            argument = argument[:-1]
        if argument.find(":") and remove_column:
            argument = argument[argument.find(":")+1:]
        beginning = end_arg
        list_args.append(argument.strip())
        count += 1
        to_find = str(count) + ". "
        index = content.find(to_find, beginning)

    return list_args



if __name__ == '__main__':
    # Load your API key from an environment variable or secret management service
    #openai.api_key = os.getenv("OPENAI_API_KEY")
    debate_name = sys.argv[1]
    print("Starting a conversation with ChatGPT on the debate: "+debate_name)
    wb = open("questions.json", "r", encoding="utf-8")
    questions = json.load(wb)
    outputfile = sys.argv[2]
    debate_intro = questions["Débat"]["debate_intro"]
    debate_intro.append({"role": "user", "content": "Voilà le débat : " + debate_name})
    debate = create_debate(questions["Débat"]["champs"], questions["Débat"]["debate_intro"])
    print("Created the debate, moving on to the arguments")
    # the title of the argument is the key and I put a level in the argument fields, together with the answers to the questions
    correspondance = {}
    identifiers = {1:debate_name}
    count = 2
    max_level = 1
    level = 1
    future_args = []
    debate["Arguments"]={}
    try:
        while level <= max_level:
            if level == 1:
                arguments_for = retrieve_list(debate["Débat"]['arguments-pour']["reponse"])
                arguments_against = retrieve_list(debate["Débat"]['arguments-contre']["reponse"])
                correspondance[debate_name]={"for":arguments_for, "against":arguments_against}
                args = arguments_for + arguments_against
                future_args = []
                for arg in args:
                    argument_intro = [{"role": "user", "content": "Etant donné l'argument"+arg}]
                    content = create_argument(questions["Argument"]["champs"], debate_intro + argument_intro)
                    content["level"]= level
                    debate["Arguments"][arg] = content
                    identifiers[count] = arg
                    count +=1
                    arguments_for = retrieve_list(content["justifications"]["reponse"])
                    arguments_against = retrieve_list(content["objections"]["reponse"])
                    arguments_for_title = retrieve_list(content["justifications-titre-affiché"]["reponse"])
                    arguments_against_title = retrieve_list(content['objections-titre-affiché']["reponse"])
                    arguments_for_page = retrieve_list(content["justifications-page"]["reponse"])
                    arguments_against_page = retrieve_list(content["objections-page"]["reponse"])
                    arguments_for_summary = retrieve_list(content["justifications-résumé"]["reponse"], remove_dot=False)
                    arguments_against_summary = retrieve_list(content["objections-résumé"]["reponse"], remove_dot=False)
                    for i in range(len(arguments_for)):
                        if i < len(arguments_for_summary) and i < len(arguments_for_page) and i < len(arguments_for_title):
                            debate["Arguments"][arguments_for[i]] = {"level":2, "résumé": {"reponse":arguments_for_summary[i]}, "page": {"reponse":arguments_for_page[i]},"titre-affiché":{"reponse":arguments_for_title[i]}}

                    for i in range(len(arguments_against)):
                        if i < len(arguments_against_summary) and i < len(arguments_against_page) and i < len(
                                arguments_against_title):
                            debate["Arguments"][arguments_against[i]] = {"level":2, "résumé": {"reponse":arguments_against_summary[i]}, "page": {"reponse":arguments_against_page[i]},"titre-affiché": {"reponse": arguments_against_title[i]}}

                    future_args.extend(arguments_for)
                    future_args.extend(arguments_against)

                print(level)
                print(len(future_args))
                sys.stdout.flush()

            else:
                args = []
                for arg in future_args:
                    count+=1
                    identifiers[count] = arg
                    count += 1
                    argument_intro = [{"role": "user", "content": "Etant donné l'argument"+arg}]
                    content = create_argument(questions["Argument"]["champs"],  debate_intro + argument_intro)
                    content["level"] = level
                    if arg in debate["Arguments"]:
                        content["titre-affiché"] = debate["Arguments"][arg]["titre-affiché"]
                        content["page"] = debate["Arguments"][arg]["page"]
                    else:
                        debate["Arguments"][arg] = content
                    arguments_for = retrieve_list(content["justifications"]["reponse"])
                    arguments_against = retrieve_list(content["objections"]["reponse"])
                    arguments_for_title = retrieve_list(content["justifications-titre-affiché"]["reponse"])
                    arguments_against_title = retrieve_list(content['objections-titre-affiché']["reponse"])
                    arguments_for_page = retrieve_list(content["justifications-page"]["reponse"])
                    arguments_against_page = retrieve_list(content['objections-page']["reponse"])

                    for i in range(len(arguments_for)):
                        debate["Arguments"][arguments_for[i]] = {"page": {"reponse": arguments_for_page[i]},
                                                                 "titre-affiché": {"reponse": arguments_for_title[i]}}

                    for i in range(len(arguments_against)):
                        debate["Arguments"][arguments_against[i]] = {"page": {"reponse": arguments_against_page[i]},
                                                                     "titre-affiché": {
                                                                         "reponse": arguments_against_title[i]}}

                    args.extend(arguments_for)
                    args.extend(arguments_against)
                future_args = args
                print(level)
                print(len(future_args))
                sys.stdout.flush()
            level +=1
    except Exception as error:
        PrintException()

    wb = open(outputfile,"w", encoding="utf-8")
    json.dump(debate, wb)