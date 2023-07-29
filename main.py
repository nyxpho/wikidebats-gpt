# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.

from pagefromfile import *
import mwparserfromhell
import deepl
import pywikibot
import requests
from bs4 import BeautifulSoup
from pywikibot import pagegenerators
from pywikibot.bot import ExistingPageBot
# Press ⌘F8 to toggle the breakpoint.

def get_soup_by_url(url):
    page = requests.get(url)
    page.encoding = 'utf-8'
    soup = BeautifulSoup(page.text, 'lxml')
    return soup

def get_link_debates(page):
    mydivs = soup.find_all("div", {"class": "mw-category-group"})
    for el in mydivs:
        ans = el.find_all('li')
        for el1 in ans:
            page.append(el1.text)
    return page

def translate_arguments(wikicode, cur_name_french):
    fl = 0
    for template in wikicode.filter_templates():

        if template.name == 'Argument\n':
            try:
                result1 = translator.translate_text(str(template.get('résumé').value), target_lang="EN-US")
                template.get('résumé').value = result1.text
            except Exception:
                fl = 0
        if template.name == 'Argument POUR\n':
            try:
                result1 = translator.translate_text(str(template.get('titre-alternatif').value), target_lang="EN-US")
                template.get('titre-alternatif').value = result1.text
            except Exception:
                result1 = translator.translate_text(str(template.get('nom').value), target_lang="EN-US")
                template.get('nom').value = result1.text

            result1 = translator.translate_text(str(template.get('nom').value), target_lang="EN-US")
            template.get('nom').value = result1.text

        if template.name == 'Argument CONTRE\n':

            try:
                result1 = translator.translate_text(str(template.get('titre-alternatif').value), target_lang="EN-US")
                template.get('titre-alternatif').value = result1.text
            except Exception:
                result1 = translator.translate_text(str(template.get('nom').value), target_lang="EN-US")
                template.get('nom').value = result1.text

            result1 = translator.translate_text(str(template.get('nom').value), target_lang="EN-US")
            template.get('nom').value = result1.text

        if template.name == 'Citation\n':
            result1 = translator.translate_text(str(template.get('citation').value), target_lang="EN-US")
            template.get('citation').value = result1.text

    wb = open("pages3.txt", "w", encoding="utf-8")
    wb.write(str(wikicode))
    wb.close()

    cur_name = translator.translate_text(cur_name_french, target_lang="EN-US")
    main_page('-file:pages3.txt', '-textonly', f'-title:{cur_name}')

    return True

if __name__ == '__main__':
    auth_key = "928c0890-6797-ab69-cc74-409868ef7d80:fx"
    translator = deepl.Translator(auth_key)

    base_url = 'https://dev.wikidebates.org/wiki/Catégorie:Débats'
    soup = get_soup_by_url(base_url)
    page_test = get_link_debates([])
    page_for_remove = ['Distance learning', 'Does God exist?',
                       'Is Ecosia an ecological search engine?','Test de débat (LUA)', 'Testing', 'Is it advisable to do the classes online?',
                       "Is it necessary to elect a representative people's assembly accessible to all?","Is there a national identity?",
                       'Should cannabis be legalized? Test', 'Should legalise','Should men join the feminist fight?','Spaces or tabs?'] #Pages that i don't need
    for el in page_for_remove:
        page_test.remove(el)
    #page_test = page[4:7]
    print(len(page_test))


    site = pywikibot.Site('dev', 'wikidebates')  # The site we want to run our bot on
    page1 = pywikibot.Page(site, 'La Convention citoyenne pour le Climat prouve le contraire')
    page2 = pywikibot.Page(site, "Faut-il généraliser le vote électronique ?")
    text1 = page1.get()
    text2 = page2.get()

    templates1 = page1.raw_extracted_templates
    templates2 = page2.raw_extracted_templates
    wikicode1 = mwparserfromhell.parse(text1)
    wikicode2 = mwparserfromhell.parse(text2)

    '''wb = open("pages3.txt", "w", encoding="utf-8")
    wb.write(str(wikicode1))
    wb.close()'''
    fl = 0
    #wikicode = translate_arguments(wikicode1, "L'existence de Dieu est contenue dans son concept")
    #page_test = ['Espaces ou tabulations ?']


    for i in range(len(page_test)):
        cur_page = page_test[i]
        page1 = pywikibot.Page(site, cur_page)
        text1 = page1.get()
        wikicode = mwparserfromhell.parse(text1)

        for template in wikicode.filter_templates(): # тут код который меняет поля

            if template.name == 'Argument POUR\n':
                try:
                    page = pywikibot.Page(site, str(template.get('nom').value))
                    text1 = page.get()
                    wikicode1 = mwparserfromhell.parse(text1)
                    translate_arguments(wikicode1, str(template.get('nom').value)) #translate subargument page for pour
                except Exception:
                    fl = 0 # there is no such a page => do nothing

            if template.name == 'Argument CONTRE\n':
                try:
                    page = pywikibot.Page(site, str(template.get('nom').value))
                    text1 = page.get()
                    wikicode1 = mwparserfromhell.parse(text1)
                    translate_arguments(wikicode1, str(template.get('nom').value)) #translate subargument page for contre
                except Exception:
                    fl = 0 # there is no such a page => do nothing


            if template.name == 'Argument POUR\n': #translate argument-for
                try:
                    result1 = translator.translate_text(str(template.get('titre-alternatif').value),target_lang="EN-US")
                    template.get('titre-alternatif').value = result1.text
                except Exception:
                    result1 = translator.translate_text(str(template.get('nom').value), target_lang="EN-US")
                    template.get('nom').value = result1.text
                    
                result1 = translator.translate_text(str(template.get('nom').value), target_lang="EN-US")
                template.get('nom').value = result1.text




            if template.name == 'Argument CONTRE\n':  #translate argument-against
                try:
                    result1 = translator.translate_text(str(template.get('titre-alternatif').value),target_lang="EN-US")
                    template.get('titre-alternatif').value = result1.text
                except Exception:
                    result1 = translator.translate_text(str(template.get('nom').value), target_lang="EN-US")
                    template.get('nom').value = result1.text
                    
                result1 = translator.translate_text(str(template.get('nom').value), target_lang="EN-US")
                template.get('nom').value = result1.text

            if template.name == "Sous-partie d'introduction au débat\n": #translate beginning of the page
                try:
                    result1 = translator.translate_text(str(template.get('titre').value), target_lang="EN-US")
                    template.get('titre').value = result1.text
                except Exception:
                    if (str(template.get('contenu').value)).find("Note") > 1:
                        ans = str(template.get('contenu').value).split('{{')
                        result1 = translator.translate_text(ans[0], target_lang="EN-US")
                        template.get('contenu').value = result1.text
                    else:
                        result1 = translator.translate_text(str(template.get('contenu').value), target_lang="EN-US")
                        template.get('contenu').value = result1.text

                try:
                    if (str(template.get('contenu').value)).find("Note") > 1:
                        ans = str(template.get('contenu').value).split('{{')
                        result1 = translator.translate_text(ans[0], target_lang="EN-US")
                        template.get('contenu').value = result1.text
                    else:
                        result1 = translator.translate_text(str(template.get('contenu').value), target_lang="EN-US")
                        template.get('contenu').value = result1.text

                except Exception:

                    result1 = translator.translate_text(str(template.get('titre').value), target_lang="EN-US")
                    template.get('titre').value = result1.text

            if template.name == "Exemple de débat connexe\n": #rename connected debates
                result1 = translator.translate_text(str(template.get('nom').value), target_lang="EN-US")
                template.get('nom').value = result1.text

        wb = open("pages3.txt", "w", encoding="utf-8")
        wb.write(str(wikicode))
        wb.close()

        cur_name = translator.translate_text(cur_page, target_lang="EN-US")
        main_page('-file:pages3.txt', '-textonly', f'-title:{cur_name}') #create translated page

    #code that uses information from arguments for POUR
    '''for (template, fielddict) in templates1:
        if template == "Argument POUR":
            try:
                print(fielddict['titre-alternatif'])
                try:
                    page = pywikibot.Page(site, fielddict['titre-alternatif'])
                    text1 = page.get()
                    print(text1)
                except Exception:
                    continue
            except KeyError:
                print(fielddict['nom'])
                try:
                    page = pywikibot.Page(site, fielddict['nom'])
                    text1 = page.get()
                    print(text1)
                except Exception:
                    continue'''


    #for template in wikicode1.filter_templates():
    #    print(template.name)




