import pandas as pd


def store_montijd_database(fp_xlsx, fp_feather):
    """
    :param fp_xlsx:
        C:\Users\tombb\Downloads\montijd.xlsx
    :param fp_feather:
        data\hwl_montijd.feather
    :return:
    """
    keys_to_keep = ['Project', 'Monstercode', 'Monsterdatum']
    df = pd.read_excel(fp_xlsx)
    df[keys_to_keep].to_feather(fp_feather)
    pass



