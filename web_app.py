from flask import Flask, render_template
from flask import request
from data_collection import get_provinces
import os
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from io import BytesIO
import base64

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'plots')


data = {}
provinces = get_provinces()


def get_data(region, row, week_interval=None):
    if week_interval == '' or week_interval is None:
        week_interval = [1, 52]
    files = os.listdir("Data")

    region_data = [x for x in files if x.split("_")[0].lower() == str(region).lower()][-1]
    dataframe = pd.read_excel("Data/" + region_data)
    df = dataframe[['year', 'week', row]]
    file_path = create_plot(df, row, region)
    data = []
    for d in df.iterrows():
        if d[1]['week'] >= week_interval[0] and d[1]['week'] <= week_interval[1]:
            data.append([d[1]['year'], d[1]['week'], d[1][row]])
    return data, file_path


def create_plot(data, row, region):
    x_label = []
    for d in data.iterrows():
        x_label.append((d[1]['year'] - 1982) * 52 + d[1]['week'])
        # x_label.append(str((d[1]['year']) + "_" + str(d[1]['week'])))
    plt.close()
    plt.plot(x_label, data[row], label=row)
    plt.xlabel('year')
    plt.ylabel(row)
    # file_name = region + "_" + row + "_" + str(datetime.now().date()) + '.jpg'
    # file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_name)
    # plt.savefig(file_path)

    io_file = BytesIO()
    plt.savefig(io_file, format='png', dpi=100)
    base64_string = base64.b64encode(io_file.getvalue()).decode()

    return base64_string


@app.route('/', methods=['GET', 'POST'])
def hello_world():
    if request.method == 'POST':
        data['time_row'] = request.form['time_row']
        data['province'] = request.form['province']
        data['week_interval'] = '' if request.form['week_interval'] == '' else list(
            map(int, request.form['week_interval'].split('-')))
        df, file_path = get_data(provinces[int(data['province']) - 1]['province'], data['time_row'],
                                 data['week_interval'])

        return render_template('index_temp.html',
                               title=provinces[int(data['province']) - 1]['province'],
                               row=data['time_row'],
                               data=df,
                               img=file_path)



    else:
        return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
