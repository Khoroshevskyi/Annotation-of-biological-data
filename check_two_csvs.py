import pandas as pd


def check_two_csvs(results_path,ground_truth_path):
    results = pd.read_csv(results_path,header=None)
    ground_truth = pd.read_csv(ground_truth_path,header=None)

    num_of_results = len(results.index)
    ground_truth = ground_truth.iloc[0:num_of_results]

    # Only looking at last part of the uris as they subgroups don't match
    results = results.apply(lambda x: x.apply(last_part_of_uri))
    ground_truth = ground_truth.apply(lambda x: x.apply(last_part_of_uri))

    wrong_results = ground_truth[ground_truth != results]

    nans = wrong_results.isna().sum().sum()
    percentage_correctly_labelled = round((nans / wrong_results.size) * 100,2)

    print(percentage_correctly_labelled)

    return percentage_correctly_labelled,wrong_results

def last_part_of_uri(uri):
    try:
        uri_parts = uri.split('/')
        last_part = uri_parts[-1]
        stripped_last_part = last_part
    except:
        # print(uri)
        return ''

    return last_part

def check_only_last_part_of_uri(uri1,uri2):
    uri1_last_part = last_part_of_uri(uri1)
    uri2_last_part = last_part_of_uri(uri2)

    last_part_is_equal = uri1_last_part == uri2_last_part

    return last_part_is_equal


if __name__ == "__main__":
    check_two_csvs("Data\\new.csv",
                        "Data\\Ground Truth\\gt_data1.csv")