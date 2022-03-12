import pandas as pd
import os 

# STEP 1: Pre-processing
df_supplier_car = pd.read_json('supplier_car.json')
df_supplier_car = df_supplier_car.iloc[:,0:8]
new_index = ['ID', 'MakeText', 'TypeName', 'TypeNameFull', 'ModelText', 'ModelTypeText']
df_supplier_car = df_supplier_car.set_index(new_index)
df_supplier_car = df_supplier_car.pivot(columns='Attribute Names', values='Attribute Values')
df_supplier_car = df_supplier_car.reset_index()
 
#filepath = '/Users/brais/Documents/Job related/Onedot/data_processing.xlsx'
filepath = os.getcwd()+'/data_processing.xlsx'

writer = pd.ExcelWriter(filepath,engine='openpyxl')
df_supplier_car.to_excel(writer, sheet_name='pre_processing')

# STEP 2: Normalisation

def consumption_fun(df):
    consumption_array =[]
    for j in range(len(df['ConsumptionTotalText'])):
        data = {}
        data['fuel_comsumption_unit']= ''.join([i for i in df['ConsumptionTotalText'].iloc[j] if not i.isdigit() and i != '.' and i !=' ']) # deleting digits we don't use
        if (data['fuel_comsumption_unit'] != 'null'):
            data['fuel_comsumption_unit'] = data['fuel_comsumption_unit'].replace('/','_')  # changing format
            data['fuel_comsumption_unit']+=str('_consumption')                              # adapting the field to our format
        consumption_array.append(data)
    df['ConsumptionTotalText'] = pd.DataFrame(consumption_array)

def make_fun(df):
    for i in range(len(df['MakeText'])):
        if (df['MakeText'].iloc[i] != 'BMW'):
            df['MakeText'].iloc[i] = df['MakeText'].iloc[i].lower()
            df['MakeText'].iloc[i] = df['MakeText'].iloc[i].title()

def carType_fun(df):
    carTypeArray = []
    carTypeCount = df.groupby('BodyTypeText').size() 
    carTypeCount = carTypeCount[carTypeCount > 15] # for grouping purposes we consider groups under 15 elemnts as others

    for i in range(len(df['BodyTypeText'])):    
        if df['BodyTypeText'].iloc[i] not in carTypeCount:
            df['BodyTypeText'].iloc[i] = 'Other' # creating the "other" group under that conditions
        elif 'SUV' in df['BodyTypeText'].iloc[i]:
            df['BodyTypeText'].iloc[i] = 'SUV' # changing format to match out SUV category nomenclature
        elif df['BodyTypeText'].iloc[i] == 'Cabriolet':
            df['BodyTypeText'].iloc[i] = 'Convertible / Roadster' # Equivalence between categories

def normalisation_fun(df): # we group all the separate normalization functions in a global normalization function
    consumption_fun(df)
    make_fun(df)
    carType_fun(df)

normalisation_fun(df_supplier_car)

df_supplier_car.to_excel(writer, sheet_name='normalisation')

# STEP 3: INTEGRATION

def rename_fun(df):
    df.rename(columns={'MakeText': 'make','BodyTypeText':'carType', 'BodyColorText' : 'color', 'ConditionTypeText' : 'condition',
    'City': 'city', 'FirstRegYear': 'manufacture_year', 'Km': 'mileage', 'ModelText':'model',
    'ModelTypeText': 'model_variant','FirstRegMonth':'manufacture_month', 'ConsumptionTotalText':'fuel_consumption_unit'}, inplace = True)

def add_fields_fun(df):
    df['currency'] = 'null'
    df['country'] = 'CH'
    df['mileage_unit'] = 'kilometer' # we can get it from the consumption field, further updates
    df['price_on_request'] = 'null'  # we have to request this field to the supplier if its possible
    df['type'] = 'car'               # it seems like it's an standard but we must be sure ab
    df['zip'] = 'null'
    df['drive'] = 'null'

def delete_fields_fun(df):
    final_table_columns = ['carType', 'color', 'condition', 'currency', 'drive', 'city', 'country', 'make', 'manufacture_year', 'mileage', 
    'mileage_unit', 'model', 'model_variant', 'price_on_request', 'type', 'zip', 'manufacture_month' ,'fuel_consumption_unit']
    df = df[df.columns.intersection(final_table_columns)] # we take the necessary columns
    df = df.reindex(columns = final_table_columns)        # we reorder them to match the company architecture
    return df

def integration_fun(df): # we group all the integration functions inside a global one
    rename_fun(df)
    add_fields_fun(df)
    df = delete_fields_fun(df)
    return df

df_supplier_car = integration_fun(df_supplier_car) 

df_supplier_car.to_excel(writer, sheet_name='integration')

writer.save()
writer.close()

