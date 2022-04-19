import os
import json
import sys
import pandas as pd

raw = '''1. Item 
    2. SalePriceBeforePromo
    3. SalePriceTimePromo
    4. DatePriceBeforePromo
    5. ObjCode
    6. DiscountType
    7. DiscountValue
    8. DateBegin
    9. DateEnd
    10. PWCcode
    11. Value
    12. FirstValue
    13. LessOrEqual'''
required_cols = [item.strip() for item in raw.split() if item.isalpha()]


def decompose(file, filename):
    goodlists = []
    for goodlist in file['Information']['GoodsLists']:
        prices = []
        for price in goodlist['Prices']:
            price_df = pd.DataFrame(data=price['Data'], columns=price['ColumnsName'])
            price_df['ObjCode'] = price['StoreCode']
            prices.append(price_df)
        df_prices = pd.concat(prices, ignore_index=True)
        df_prices['DiscountType'] = goodlist['DiscountType']
        df_prices['DiscountValue'] = goodlist['DiscountValue']
        try:
            df_prices['Value'] = goodlist['GoodsComposition'][0]['Value']
        except Exception:
            df_prices['Value'] = None
        try:
            df_prices['FirstValue'] = goodlist['PriceOptions'][0]['FirstValue']
        except Exception:
            df_prices['FirstValue'] = None
        try:
            df_prices['LessOrEqual'] = goodlist['PriceOptions'][0]['Operator']
        except Exception:
            df_prices['LessOrEqual'] = None
        goodlists.append(df_prices)
    df = pd.concat(goodlists, ignore_index=True)
    df['DateBegin'] = file['GeneralInfo']['DateBegin']
    df['DateEnd'] = file['GeneralInfo']['DateEnd']
    df['PWCcode'] = file['GeneralInfo']['PWCcode']
    df['file'] = filename
    return df


if __name__ == '__main__':
    cwd = os.getcwd()
    path = os.path.join(cwd, 'promo')
    if os.path.exists(path):
        filenames = [name for name in os.listdir(path) if '.json' in name]
    else:
        filenames = [name for name in os.listdir(cwd) if '.json' in name]
    if not filenames:
        print(f'Файлы .json не найдены.\nРазместите файлы в {path}, либо непосредственно в {cwd}')
        sys.exit()
    dfs = []
    for filename in filenames:
        full_path = os.path.join(path, filename)
        with open(full_path, 'r') as file:
            json_file = json.load(file)
            df = decompose(json_file, filename)
            dfs.append(df)

    final_df = pd.concat(dfs, ignore_index=True)
    final_df = final_df[required_cols + ['file']]
    final_df.to_excel('result.xlsx', na_rep='None', index=False)
    print('Обработка завершена.')


