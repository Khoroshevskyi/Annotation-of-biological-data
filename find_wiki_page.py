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

'''
Sample data: 
data = ["nrdF","nrdF","deoxyribonucleotide biosynthetic process","ribonucleoside-diphosphate reductase activity, "
                                                                "thioredoxin disulfide as acceptor","membrane"]
data = ["Hypothetical protein CT_423", "hypothetical protein",
        "oxidation-reduction process", "oxidoreductase activity, acting on CH-OH group of donors", "Cell membrane"]

data = ["L137446", "L137446", "teichoic acid transport", "ATPase activity", "Cell membrane"]
data = ["Hypothetical protein CELE_Y116A8B.1","Y116A8B.1","","",""]

data = ["Tc00.1047053507991.70","Zinc finger, C3HC4 type (RING finger)/EF-hand domain pair, putative","","","cytoplasm"]

data = ["1,6-dihydroxycyclohexa-2,4-diene-1-carboxylate dehydrogenase BPSS1906","BPSS1906","oxidation-reduction process","oxidoreductase activity",""]

data= ["Cell division ATP-binding protein FtsE Smed_2543","cell division ATP-binding protein FtsE Smed_2543","cell cycle","ATPase activity","Cell membrane"]

'''


class FindWikiPage(object):
    def __init__(self, config=None):
        print("FindWikiPage initiated...")
        self.site = pywikibot.Site("wikidata", "wikidata")
        self.repo = self.site.data_repository()
        self.gebe_searched_list = []


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
        #self.pretty_response(json_response)
        return json_response

    # just prints pretty
    def pretty_response(self, json_obj):
        print(json.dumps(json_obj, indent=4))

    # Searching pages linked by reference number and returns list of id's (of linked pages)
    def search_statements(self, item_identifier, reference_nr):
        try:
            item = pywikibot.ItemPage(self.repo, item_identifier)

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
        item = pywikibot.ItemPage(self.repo, id)
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
            print(f"{id} No label were found")
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
            print(f"{id} No description were found")
            return ""

    # Gets the item aliases(in English)
    def get_item_aliases(self, id):
        try:
            item_dict = self.get_item_info(id)
            clm_dict = item_dict["aliases"]  # Get the claim dictionary
            item_description = clm_dict['en']
            # print(item_description)
            return item_description
        except:
            print(f"{id} No aliases were found")
            return ""

    # receiving id of item where to search, id of statement which we want to search, and value which we are searching
    # returns id if value is found
    def search_by_property(self, id_info, property_id, value):
        statements = self.search_statements(id_info, property_id)
        if statements:
            for output in statements:
                output1 = 'Q' + str(output)

                leb = self.get_item_label(output1)
                dis = self.get_item_descriptions(output1)
                aka_list = self.get_item_aliases(output1)

                if self.is_in_text(leb, value):
                    return output1
                for aka in aka_list:
                    if self.is_in_text(aka, value):
                        return output1
                if self.is_in_text(dis, value):
                    return output1
        else:
            print("None")

    # used for method in text finding
    def preprocess_text(self, text):
        text = text.lower().strip()
        text = re.sub('[^A-Za-z0-9 ]+', '', text)
        return text

    # checks if is RexEx in the text
    def is_in_text(self, text_to_find, original_text):
        original_text = self.preprocess_text(original_text)
        text_to_find = self.preprocess_text(text_to_find)
        print("1"+original_text)
        print("2"+text_to_find)
        x = re.findall(text_to_find, original_text)
        print(original_text)
        print(text_to_find==original_text)
        if x:
            return True
        return False

    def search_info_by_property(self, item_id, property_id, value):
        if value != '':
            return self.search_by_property(item_id, property_id, value)
        else:
            return ""

    def gene_search(self, text_list):
        print("repositories are searching")
        print(text_list)
        resps = self.search_entities(text_list[0])
        # print(json.dumps(resps, indent=2))
        all_outputs = []
        a = 0
        for respon in resps["search"]:
            a += 1
            print(f"Blablabla: {a}")
            protein = self.search_by_property(respon["id"], ENCODES, text_list[1])
            if protein:
                id_list = [respon["id"], protein]
                # print("####################")
                id_list.append(self.search_info_by_property(protein, BIOLOGICAL_PROCESS, text_list[2]))

                # print("####################")
                id_list.append(self.search_info_by_property(protein, MOLECULAR_FUNCTION, text_list[3]))

                # print("####################")
                id_list.append(self.search_info_by_property(protein, CELL_COMPONENT, text_list[4]))
                print(id_list)
                all_outputs.append(id_list)
                if None not in id_list:
                    return id_list

        return None

    def try_different_cinfiguration(self, text_list):
        print("try_different_cinfiguration",str(text_list))
        text_list1 = text_list
        text_list1[0], text_list1[1] = text_list1[1], text_list1[0]
        item_id_list = self.gene_search(text_list1)
        if item_id_list:
            return item_id_list

    def try_split_values(self, text_list):
        print("try_split_values", str(text_list))
        for new_item in reversed(text_list[0].split()):
            text_list1 = text_list
            text_list1[0] = new_item
            item_id_list = self.gene_search(text_list1)
            if item_id_list:
                return item_id_list

    def start_process(self, text_list):
        item_id_list = self.gene_search(text_list)
        if not item_id_list:            # if found nothing splitting first value of row to separate words

            item_id_list = self.try_different_cinfiguration(text_list)
            if item_id_list:
                return item_id_list

            item_id_list = self.try_split_values(text_list)
            if item_id_list:
                return item_id_list
        else:
            return item_id_list

        print("Finished: found nothing")
        return None


if __name__ == "__main__":
    data = ["Hypothetical protein CELE_Y116A8B.1", "Y116A8B.1", "", "", ""]
    find_wiki = FindWikiPage()
    end = find_wiki.start_process(data)
