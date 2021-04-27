import pywikibot
import requests
import pprint
import pandas as pd
import time

WIKI_DATA_API = 'https://www.wikidata.org/w/api.php'

class EntityClassification(object):

    def __init__(self):
        site = pywikibot.Site("wikidata", "wikidata")
        self.repo = site.data_repository()


    def search_wiki(self, item):
        params = {'action': 'wbsearchentities',
                  'format': 'json',
                  'language': 'en',
                  'type': 'item',
                  'search': item,
                  "limit": 2}

        response = requests.get(WIKI_DATA_API, params=params, )

        return response.json()


    def possible_ids(self, pd, col):
        possible_ids_pd = {}
        unique_ids = []
        for i in pd[col]:
            if i not in unique_ids:
                unique_ids.append(i)
                ID = self.search_wiki(i)
                possible_ids_pd[i] = []
                for l in range(len(ID['search'])):
                    possible_ids_pd[i].append(ID["search"][l]["id"])
        return possible_ids_pd

    def get_statements(self, item_identifier):
        item = pywikibot.ItemPage(self.repo, item_identifier)
        item_dict = item.get()  # Get the item dictionary
        clm_dict = dict(item_dict["claims"])  # Get the claim dictionary
        # dict_of_properties = {}
        if "P31" not in clm_dict.keys():
            return "none"
        else:
            for clm in clm_dict["P31"]:
                response_dict = clm.toJSON()
                if response_dict['mainsnak']['snaktype'] == 'value':
                    if response_dict['mainsnak']['datavalue']['type'] == 'wikibase-entityid':
                        p31_id = 'Q' + str(response_dict['mainsnak']['datavalue']['value']['numeric-id'])
            return p31_id

    def p31_count(self, dict_poss_ids, col):
        count_p31_col = {}
        for k2 in dict_poss_ids[col].keys():
            if len(dict_poss_ids[col][k2]) == 1:
                i_d = dict_poss_ids[col][k2][0]
                n = self.get_statements(i_d)
                if n in list(count_p31_col.keys()):
                    count_p31_col[n] += 1
                else:
                    count_p31_col[n] = 1
        return count_p31_col

    def get_entity_classif(self, input_data, nrows):
        start = time.time()

        pd1 = pd.read_csv(input_data, nrows=nrows, header=None)

        possible_ids_by_column = {}
        for c in list(pd1.columns):
            possible_ids_by_column[c] = self.possible_ids(pd1, c)

        p31_count_col = {}
        for c in list(pd1.columns):
            p31_count_col[c] = self.p31_count(possible_ids_by_column, c)
            p31_count_col[c] = sorted(p31_count_col[c].items(), key=lambda x: x[1], reverse=True)
        print("Entity classification per column: ")
        pprint.pprint(p31_count_col)

        end = time.time() - start
        m, s = divmod(end, 60)
        print("Time spent: {} min {} sec.".format(int(m), s))

        instance_ids = []
        for keyyy in p31_count_col.keys():
            instance_ids.append(p31_count_col[keyyy][0][0])

        return instance_ids


if __name__=="__main__":
    dd = EntityClassification()
    dd.get_entity_classif('Data\Input\input_data1.csv', 20)