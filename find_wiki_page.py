import pywikibot
import json
import requests
import re
import logging
import time

"""
Sometimes pywikibot is not working so it's better to write own code in sparql!
if there is sleep ..... try to use this:
pywikibot.config.verbose_output = 1
pywikibot.config.debug_log = True

if it won't help - try to wait two hours -_-
"""

WIKI_DATA_API = 'https://www.wikidata.org/w/api.php'

# INSTANCE_OF = "P31"  # e.g. gene ==> Q7187
ENCODES = "P688"  # which protein encodes
BIOLOGICAL_PROCESS = "P682"
MOLECULAR_FUNCTION = "P680"
CELL_COMPONENT = "P681"

'''
Sample data: 
data = ["nrdF","nrdF","deoxyribonucleotide biosynthetic process","ribonucleoside-diphosphate reductase activity, "
                                                                "thioredoxin disulfide as acceptor","membrane"]
data = ["Hypothetical protein CT_423", "hypothetical protein",
        "oxidation-reduction process", "oxidoreductase activity, acting on CH-OH group of donors", "Cell membrane"]

data = ["L137446", "L137446", "teichoic acid transport", "ATPase activity", "Cell membrane"]
data = ["Hypothetical protein CELE_Y116A8B.1","Y116A8B.1","","",""]

data = ["Tc00.1047053507991.70","Zinc finger, C3HC4 type (RING finger)/EF-hand domain pair, putative","","","cytoplasm"]

data = ["1,6-dihydroxycyclohexa-2,4-diene-1-carboxylate dehydrogenase BPSS1906","BPSS1906",
        "oxidation-reduction process","oxidoreductase activity",""]

data= ["Cell division ATP-binding protein FtsE Smed_2543","cell division ATP-binding protein FtsE Smed_2543",
"cell cycle","ATPase activity","Cell membrane"]

'''


class FindWikiPage(object):
    def __init__(self):
        logging.basicConfig(filename='find_wiki.log', level=logging.DEBUG,
                            filemode='w+', format='%(asctime)s:%(levelname)s:%(message)s')

        print("FindWikiPage initiated...")
        logging.info("FindWikiPage initiated...")
        self.site = pywikibot.Site("wikidata", "wikidata")
        self.repo = self.site.data_repository()

    # searching items by expressions by using API
    def search_entities(self, itemtitle):
        params = {'action': 'wbsearchentities',
                  'format': 'json',
                  'language': 'en',
                  'type': 'item',
                  'search': itemtitle,
                  "limit": 50}

        response = requests.get(
            WIKI_DATA_API,
            params=params,
        )

        if response.status_code != 200:
            logging.error(f"Error while searching for information, response: {response.status_code}")
            raise Exception("Bad response:(")

        return response.json()

    # just prints pretty
    def pretty_response(self, json_obj):
        print(json.dumps(json_obj, indent=4))

    # Searching statement_value by property_id and returns list of property_id's
    def search_statements(self, item_identifier, property_id):
        try:
            item = pywikibot.ItemPage(self.repo, item_identifier)
            item_dict = item.get()  # Get the item dictionary
            clm_dict = item_dict["claims"]  # Get the claim dictionary

            prop_id_list = []
            for clm in clm_dict[property_id]:
                response_dict = clm.toJSON()
                prop_id_list.append(response_dict['mainsnak']['datavalue']['value']['numeric-id'])

            return prop_id_list

        except KeyError as err:
            logging.error(f"There is no: {err} in {item_identifier}")
            return None

    # Gets the item dictionary with information: dict_keys(['aliases', 'sitelinks', 'descriptions', 'claims', 'labels'])
    def get_item_info(self, statement_id):
        item = pywikibot.ItemPage(self.repo, statement_id)
        item_dict = item.get()  # Get the item dictionary
        return item_dict

    # Gets the item label (in English)
    def get_item_label(self, statement_id):
        try:
            item_dict = self.get_item_info(statement_id)
            clm_dict = item_dict["labels"]  # Get the claim dictionary
            item_label = clm_dict.toJSON()['en']['value']
            return item_label
        except:
            logging.warning(f"{statement_id} No label were found")
            return ""

    # Gets the item description(in English)
    def get_item_descriptions(self, item_id):
        try:
            item_dict = self.get_item_info(item_id)
            clm_dict = item_dict["descriptions"]  # Get the claim dictionary
            item_description = clm_dict.toJSON()['en']['value']

            return item_description
        except:
            logging.warning(f"{item_id} No description were found")
            return ""

    # Gets the item aliases(in English)
    def get_item_aliases(self, statement_id):
        try:
            item_dict = self.get_item_info(statement_id)
            clm_dict = item_dict["aliases"]  # Get the claim dictionary
            item_aliases = clm_dict['en']
            return item_aliases

        except:
            logging.warning(f"{statement_id} No aliases were found")
            return ""

    # receiving id of item where to search, id of statement which we want to search, and value which we are searching
    # returns id if value is found
    def search_by_property(self, item_id, property_id, value):
        logging.info(f"Searching for value: {value} | by property id: {property_id} | in item: {item_id} ")
        print(f"Searching for value: {value} | by property id: {property_id} | in item: {item_id} ")
        statement_id_list = self.search_statements(item_id, property_id)  # searching statement value by property id
        if statement_id_list:
            for statement_id in statement_id_list:
                statement_id_full = 'Q' + str(statement_id)

                leb = self.get_item_label(statement_id_full)
                dis = self.get_item_descriptions(statement_id_full)
                aka_list = self.get_item_aliases(statement_id_full)

                if self.is_in_text(leb, value):
                    return statement_id_full
                for aka in aka_list:
                    if self.is_in_text(aka, value):
                        return statement_id_full
                if self.is_in_text(dis, value):
                    return statement_id_full
        else:
            logging.info("Value in property id not found, or property id not found")
            print("Value in property id not found, or property id not found")

    # used for method in text finding
    # need to be better done !!!
    def preprocess_text(self, text):
        text = text.lower().strip()
        text = re.sub("[^A-Za-z0-9 ]+", '', text)
        return text

    # checks if is RexEx in the text
    def is_in_text(self, original_text, text_to_find):

        original_text = self.preprocess_text(original_text)
        text_to_find = self.preprocess_text(text_to_find)

        x = re.findall(text_to_find, original_text)
        if x:
            return True
        # return False
        x = re.findall(original_text, text_to_find)
        if x:
            return True
        return False

    def search_info_by_property(self, item_id, property_id, value):
        if value != '':
            return self.search_by_property(item_id, property_id, value)
        else:
            return ""

    def gene_search(self, text_list):
        found_entities = self.search_entities(text_list[0])
        nr_found = 0
        t_start = time.time()
        for found_item_id in found_entities["search"]:
            if (time.time() - t_start) > 60:
                return ["", "", "", "", ""]
            print(f"searching whether {found_item_id['id']} is a gene")
            nr_found += 1
            logging.info(f"number of items found by searching: {nr_found} ")
            protein = self.search_by_property(found_item_id["id"], ENCODES, text_list[1])
            if protein:
                id_list = [found_item_id["id"], protein,
                           self.search_info_by_property(protein, BIOLOGICAL_PROCESS, text_list[2]),
                           self.search_info_by_property(protein, MOLECULAR_FUNCTION, text_list[3]),
                           self.search_info_by_property(protein, CELL_COMPONENT, text_list[4])]

                logging.info(f"List found: {id_list}")

                if None not in id_list:
                    return id_list

        logging.info(f"Nothing found in items: {found_entities['search']}")
        return None

    # changing place first and second element
    # has to be improved !!!
    def try_different_configuration(self, text_list):
        print("Searching by different list configuration")
        logging.info(f"try_different_configuration for: {text_list}")
        text_list1 = text_list
        text_list1[0], text_list1[1] = text_list1[1], text_list1[0]
        item_id_list = self.gene_search(text_list1)
        if item_id_list:
            return item_id_list

    def try_by_splitting_values(self, text_list):
        print("Searching by splitting values list configuration")
        logging.info(f"trying to find some values by splitting: {text_list}")
        for new_item in reversed(text_list[0].split()):
            text_list_new = text_list
            text_list_new[0] = new_item
            item_id_list = self.gene_search(text_list_new)

            if item_id_list:
                return item_id_list
            item_id_list = self.try_different_configuration(text_list)
            if item_id_list:
                return item_id_list

    def start(self, text_list):
        print(f"Searching for: {text_list}")
        logging.info("Start searching first item")
        t_start = time.time()
        item_id_list = self.gene_search(text_list)
        if not item_id_list:  # if found nothing splitting first value of row to separate words

            item_id_list = self.try_different_configuration(text_list)

            if item_id_list:

                logging.info("Found list of items with success!")
                return item_id_list

            item_id_list = self.try_by_splitting_values(text_list)
            if item_id_list:
                logging.info("Found list of items with success!")
                return item_id_list
        else:
            logging.info("Found list of items with success!")
            return item_id_list

        print("Finished: nothing found ")
        logging.info("Finished: nothing found ")
        return None


if __name__ == "__main__":
    data = ["Hypothetical protein CELE_Y116A8B.1", "Y116A8B.1", "", "", ""]
    # data = ['BMAA1331', 'short chain dehydrogenase', 'oxidation-reduction process', 'oxidoreductase activity', '']
    find_wiki = FindWikiPage()
    id_found = find_wiki.start(data)
    print(f"Id found: {id_found} ")
