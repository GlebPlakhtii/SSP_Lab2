import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import os
from matplotlib import pyplot
from flask import Flask



def get_mean_data(country_code, province_id):
    try:
        response = requests.get("https://www.star.nesdis.noaa.gov/smcd/emb/vci/VH/get_TS_admin.php",
                                params={"country_code": country_code, "provinceID": province_id, "year1": 1981,
                                        "year2": 2020, "type": "Mean"})

    except:
        print("response error")
        return
    return response


def get_provinces_dataframe():
    response = requests.get(
        "https://www.star.nesdis.noaa.gov/smcd/emb/vci/VH/vh_browseByCountry_province.php?country_code=UKR")
    soup = BeautifulSoup(response.content, 'lxml')
    provinces = []
    id = []
    for province in soup.find("select", id="Province").find_all('option'):
        provinces.append(province.text.split(" ")[-1])
        id.append(int(province.text.split(":")[0]))

    dataframe = pd.DataFrame({'provinces': provinces, 'id': id})
    dataframe.to_excel("provinces.xlsx")


def get_provinces():
    provinces = []
    dataframe = pd.read_excel("provinces.xlsx")

    for i in range(len(dataframe)):
        provinces.append({'province': dataframe['provinces'][i], 'id': dataframe['id'][i]})
    return provinces


def data_to_excel():
    for province in get_provinces():
        content = get_mean_data("UKR", province['id']).content
        soup = BeautifulSoup(content, "lxml")
        mean_data = soup.find("pre").text
        data = {'year': [], 'week': [], 'SMN': [], 'SMT': [], 'VCI': [], 'TCI': [], 'VHI': []}
        for row in mean_data.split("\n")[:-1]:
            row_list = row.split(",")

            try:

                data['year'].append(row_list[0])
                data['week'].append(row_list[1])
                data['SMN'].append(row_list[2].strip())
                data['SMT'].append(row_list[3].strip())
                data['VCI'].append(row_list[4].strip())
                data['TCI'].append(row_list[5].strip())
                data['VHI'].append(row_list[6].strip())


            except:
                pass

        frame = pd.DataFrame(data)
        frame.index.name = 'id'
        try:
            os.makedirs('Data')
        except:
            pass
        frame.to_excel(os.getcwd() + '/' + 'Data/' + province['province'] + "_" + str(datetime.now().date()) + '.xlsx')


def change_id():
    dataframe = pd.read_excel("provinces.xlsx")
    for i in range(len(dataframe)):
        dataframe['id'][i] = len(dataframe) - i

    dataframe.to_excel('changed_provinces.xlsx')


def get_VHI_for_year(region, year):
    files = os.listdir("Data")

    region_data = [x for x in files if x.split("_")[0].lower() == str(region).lower()][-1]
    dataframe = pd.read_excel("Data/" + region_data)
    print("Data for ", region, " in ", year, "year\nLast update :", region_data.split('_')[-1].split('.')[0])
    data_for_year = dataframe[dataframe['year'] == year]
    print(data_for_year, '\n\n')

    print("Max VHI for ", year, " year:")
    print(data_for_year[data_for_year.index == data_for_year["VCI"].idxmax()], '\n')

    print("Min VHI for ", year, " year:")
    print(data_for_year[data_for_year.index == data_for_year["VCI"].idxmin()])


def get_VHI_for_region(region):
    files = os.listdir("Data")

    region_data = [x for x in files if x.split("_")[0].lower() == str(region).lower()][-1]
    dataframe = pd.read_excel("Data/" + region_data)
    print("Data for ", region, "\nLast update :", region_data.split('_')[-1].split('.')[0])
    print(dataframe, '\n\n')

    extreme_drought = dataframe[dataframe["VHI"] < 15]
    extreme_drought = extreme_drought[extreme_drought["VHI"] != -1]

    print('\n\n', "Data during extreme drought (VHI <15)")
    print(extreme_drought)

    modarate_drought = dataframe[dataframe["VHI"] < 35]
    modarate_drought = modarate_drought[modarate_drought["VHI"] != -1]
    print('\n\n', "Data during modarate drought (VHI <35)")
    print(modarate_drought)
