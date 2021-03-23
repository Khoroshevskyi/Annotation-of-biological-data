import pywikibot
import json
import requests
import re

"""
Sometimes pywikibot is not working so it's better to write own code in sparql!
if there there is sleep ..... try to use this:
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
# data = ["nrdF","nrdF","deoxyribonucleotide biosynthetic process","ribonucleoside-diphosphate reductase activity, "
#                                                                 "thioredoxin disulfide as acceptor","membrane"]
# data = ["Hypothetical protein CT_423", "hypothetical protein",
#         "oxidation-reduction process", "oxidoreductase activity, acting on CH-OH group of donors", "Cell membrane"]

data = ["L137446", "L137446", "teichoic acid transport", "ATPase activity", "Cell membrane"]


class FindWikiPage(object):
    def __init__(self, config=None):
        print("Starting program")

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
            raise Exception("Bad response:(")
        json_response = response.json()

        return json_response

    # just prints pretty
    def pretty_response(self, json_obj):
        print(json.dumps(json_obj, indent=4))

    # Searching pages linked by reference number and returns list of id's (of linked pages)
    def search_statements(self, item_identifier, reference_nr):
        try:
            site = pywikibot.Site("wikidata", "wikidata")
            repo = site.data_repository()
            item = pywikibot.ItemPage(repo, item_identifier)

            item_dict = item.get()  # Get the item dictionary
            # print(item_dict.keys())
            # for dd in item_dict["sitelinks"]:
            #    print(dd)
            # print(item_dict["claims"])
            clm_dict = item_dict["claims"]  # Get the claim dictionary

            clm_dict1 = clm_dict[reference_nr]
            resp_arr = []
            for clm in clm_dict1:
                response_dict = clm.toJSON()
                # pretty_response(response_dict)
                # print(response_dict)
                resp_arr.append(response_dict['mainsnak']['datavalue']['value']['numeric-id'])
            return resp_arr
        except KeyError as err:
            print(f"There is no: {err}")
            return None

    # Gets the item dictionary with information: dict_keys(['aliases', 'sitelinks', 'descriptions', 'claims', 'labels'])
    def get_item_info(self, id):
        site = pywikibot.Site("wikidata", "wikidata")
        repo = site.data_repository()
        item = pywikibot.ItemPage(repo, id)
        item_dict = item.get()  # Get the item dictionary
        return item_dict

    # Gets the item label (in English)
    def get_item_label(self, id):
        try:
            item_dict = self.get_item_info(id)
            clm_dict = item_dict["labels"]  # Get the claim dictionary
            item_label = clm_dict.toJSON()['en']['value']
            # print(item_label)
            return item_label
        except:
            print("No label found")
            return ""

    # Gets the item description(in English)
    def get_item_descriptions(self, id):
        try:
            item_dict = self.get_item_info(id)
            clm_dict = item_dict["descriptions"]  # Get the claim dictionary
            item_description = clm_dict.toJSON()['en']['value']
            # print(item_description)
            return item_description
        except:
            print("No description found")
            return ""

    def get_item_aliases(self, id):
        try:
            item_dict = self.get_item_info(id)
            clm_dict = item_dict["aliases"]  # Get the claim dictionary
            item_description = clm_dict['en']
            # print(item_description)
            return item_description
        except:
            print("No aliases found")
            return ""

    # receiving id of item where to search, id of statement which we want to search, and value which we are searching
    # returns id if value is found
    def search_by_statement(self, id_info, statement, value):
        statements = self.search_statements(id_info, statement)
        if statements:
            for output in statements:
                output1 = 'Q' + str(output)
                # print(output1)

                leb = self.get_item_label(output1)
                dis = self.get_item_descriptions(output1)
                aka_list = self.get_item_aliases(output1)
                # print(f"leb:: {leb}")
                # print(f"dis:: {dis}")
                # print(f"aka:: {aka_list}")
                # print(self.is_in_text(leb, value))
                if self.is_in_text(leb, value):
                    return output1
                for aka in aka_list:
                    # print(aka)
                    if self.is_in_text(aka, value):
                        return output1
                if self.is_in_text(dis, value):
                    return output1
        else:
            print("None")

    def is_in_text(self, original_text, text_to_find):
        original_text = original_text.lower().strip()
        text_to_find = text_to_find.lower().strip()

        x = re.findall(text_to_find, original_text)
        if x:
            # print(x)
            return True
        return False

    def gene_search(self):

        resps = self.search_entities(data[0])
        # print(json.dumps(resps, indent=2))
        for respon in resps["search"]:

            protein = self.search_by_statement(respon["id"], ENCODES, data[1])
            if protein:
                id_list = [respon["id"], protein]
                print("####################")
                a = self.search_by_statement(protein, BIOLOGICAL_PROCESS, data[2])
                id_list.append(a)
                print("####################")
                b = self.search_by_statement(protein, MOLECULAR_FUNCTION, data[3])
                id_list.append(b)
                print("####################")
                c = self.search_by_statement(protein, CELL_COMPONENT, data[4])
                id_list.append(c)

                if None not in id_list:
                    return id_list


find_wiki = FindWikiPage()
end = find_wiki.gene_search()
print(f"end::: {end}")
# original_text = "hypothetical protein CT_423"
# text_to_find = "Hypothetical protein"
#
# find_in_text(original_text, text_to_find)

"""
Write if statement with RegEx
# maybe we can write all code by using sparql
def find_myself(id='@Q21150101'):
    params = {'action': 'wbsearchentities',
              'search': id,
              'format': "json",
              'language': 'en'}

    response = requests.get(
        WIKI_DATA_API,
        params=params,
    )

    json_response = response.json()
    print(json_response)
find_myself()
"""
