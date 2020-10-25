import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
from data_collection import *

pd.set_option('display.max_rows', 3000)


def main():
    get_provinces_dataframe()
    change_id()
    data_to_excel()
    get_VHI_for_year("Rivne", 2001)
    get_VHI_for_region("Kiev")


main()
