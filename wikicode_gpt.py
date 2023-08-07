import pywikibot
import json
from sentence_transformers import SentenceTransformer, util
import sys

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
    pysite = pywikibot.Site("fr", 'wikidebates')
    wikipedia = pywikibot.Site("fr", 'wikipedia')
    wikicode = "{{Débat\n|avancement=Débat en construction\n|avertissements-débat=ChatGPT\n"
    model = SentenceTransformer('paraphrase-multilingual-mpnet-base-v2')
    debate_name = sys.argv[1]
    input_file = sys.argv[2]
    wb = open(input_file, "r", encoding="utf-8")
    content = json.load(wb)
    new_arguments = []

    arguments = list(content["Arguments"].keys())

    print("We will create "+ str(len(arguments)) +" arguments. ")
    paraphrases = util.paraphrase_mining(model, arguments)
    sorted_tuples = sorted(paraphrases, key=lambda x: x[0], reverse=True)
    tuple = sorted_tuples[0]
    c_int = 0
    while tuple[0] > 0.95:
        level_arg1 = 2
        if "level" in content["Arguments"][arguments[tuple[1]]]:
            level_arg1 = content["Arguments"][arguments[tuple[1]]]["level"]
        level_arg2 = 2
        if "level" in content["Arguments"][arguments[tuple[2]]]:
            level_arg2 = content["Arguments"][arguments[tuple[2]]]["level"]
        if level_arg1 <= level_arg2:
            content["Arguments"][arguments[tuple[1]]]["redirect"] = arguments[tuple[1]]
        else:
            content["Arguments"][arguments[tuple[2]]]["redirect"] = arguments[tuple[1]]
        print("Added redirect as similarity between arguments is larger than threshold: \n " + arguments[tuple[1]] + "\n"+ arguments[tuple[2]])
        c_int+=1
        tuple = sorted_tuples[c_int]
        #print(content["Arguments"])

    for key in content["Débat"]:
        element = content["Débat"][key]
        if key == "introduction":
            introduction=""
            list_parts = retrieve_list(element["reponse"], remove_column=False)
            for part in list_parts:
                sep =  part.find(":")
                intro = "{{Sous-partie d'introduction au débat\n|titre=" + part[0:sep] + "\n|contenu=" + part[sep+1:] + "\n}}"
                introduction+=intro
            wikicode+="|introduction="+ introduction+"\n"

        if key == "articles-Wikipédia":
            articles_wiki = ""
            list_parts = retrieve_list(element["reponse"], remove_column=False)
            for part in list_parts:
                sep = part.find(":")
                title_wiki = part[0:sep].strip()
                page_wiki = pywikibot.Page(wikipedia, title_wiki)
                if page_wiki.exists():
                    article = "{{Article Wikipédia\n|page=" + title_wiki + "\n}}"
                    articles_wiki += article
            if len(articles_wiki):
                wikicode += "|articles-Wikipédia=" + articles_wiki + "\n"

        if key == "rubriques":
            reponse = element["reponse"]
            if len(reponse):
                wikicode+="|rubriques=" + reponse.strip()+"\n"

        if key == "mots-clés":
            reponse = element["reponse"]
            if len(reponse):
                wikicode += "|mots-clés=" + reponse.strip() + "\n"

        if key == "sujet":
            reponse = element["reponse"]
            if len(reponse):
                wikicode += "|sujet=" + reponse[len("Arguments pour et contre "):-1].strip() + "\n"

        arguments = content["Arguments"]
        for_arguments=""
        if key == "arguments-pour":
            list_parts = retrieve_list(element["reponse"])
            for part in list_parts:
                arg = arguments[part]
                title = arg["page"]["reponse"].strip()
                if title.find(".") == len(title) - 1:
                    title = title[:-1]
                argument = "{{Argument pour\n|page=" + title + \
                           "\n|titre-affiché=" + title + "\n}}"
                for_arguments+=argument
            wikicode += "|arguments-pour=" + for_arguments + "\n"
        against_arguments = ""
        if key == "arguments-contre":
            list_parts = retrieve_list(element["reponse"])
            for part in list_parts:
                arg = arguments[part]
                title = arg["page"]["reponse"].strip()
                if title.find(".") == len(title) - 1:
                    title = title[:-1]
                argument = "{{Argument contre\n|page=" + title + \
                           "\n|titre-affiché=" + title + "\n}}"
                against_arguments += argument
            wikicode += "|arguments-contre=" + against_arguments + "\n"

    wikicode+="}}"
    print("finished debate")
    page = pywikibot.Page(pysite, debate_name)
    if not page.exists():
        page.text = wikicode
        page.save("ChatGPT created debate")

    #print(wikicode)

    for key in content["Arguments"]:
        if "redirect" in content["Arguments"][key]:
            to_redirect = content["Arguments"][key]["redirect"]
            argument = content["Arguments"][to_redirect]
            print("REDIRECT!!!")
        else:
            argument = content["Arguments"][key]

        title = argument["page"]["reponse"]
        if title.find(".") == len(title) - 1:
            title = title[:-1]
        page = pywikibot.Page(pysite, title)
        if not page.exists():
            wikicode_argument = "{{Argument\n"
            if "résumé" in argument:
                c_resume = argument["résumé"]["reponse"]
                if c_resume[-1]!='.':
                    c_resume+="."
                wikicode_argument+="|résumé="+c_resume+"\n"
            if "mots-clés" in argument:
                wikicode_argument+="|mots-clés="+argument["mots-clés"]["reponse"]+"\n"
            if "rubriques" in argument:
                wikicode_argument+="|rubriques="+argument["rubriques"]["reponse"]+"\n"
            if "justifications" in argument:
                justifications = retrieve_list(argument["justifications"]["reponse"])
                justifications_text = ""
                for just in justifications:
                    if just not in content["Arguments"]:
                        print(just + "not found in Arguments")
                        break
                    just_new = just
                    if "redirect" in content["Arguments"][just]:
                        just_new = content["Arguments"][just]["redirect"]

                    justifications_text += "{{Justification\n|page=" + content["Arguments"][just_new]["page"]["reponse"].strip() +  "\n|titre-affiché=" + content["Arguments"][just_new]["page"]["reponse"].strip() + "\n}}"

                if len(justifications_text):
                    wikicode_argument += "|justifications=" + justifications_text + "\n"
            if "objections" in argument:
                objections = retrieve_list(argument["objections"]["reponse"])
                objections_text = ""
                for obj in objections:
                    if obj not in content["Arguments"]:
                        print(obj + "not found in Arguments")
                        break
                    obj_new = obj
                    if "redirect" in content["Arguments"][obj]:
                        obj_new = content["Arguments"][obj]["redirect"]

                    objections_text += "{{Objection\n|page=" + content["Arguments"][obj_new]["page"]["reponse"].strip() + "\n|titre-affiché=" + content["Arguments"][obj_new]["page"]["reponse"].strip() + "\n}}"

                if len(objections_text):
                    wikicode_argument += "|objections=" + objections_text + "\n"
            wikicode_argument+="}}"
            #print(wikicode_argument)

            page.text = wikicode_argument
            page.save("ChatGPT created this argument")


