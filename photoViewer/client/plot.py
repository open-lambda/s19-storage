import matplotlib.pyplot as plt
import json
import pandas as pd

def read_file(file_name):
    with open(file_name) as fr:
        data = json.load(fr)
        n = len(data)
        values_time = [data[str(i)]['time'] for i in range(1, n + 1)]
        values_s3_time = [data[str(i)]['s3_time'] for i in range(1, n + 1)]
        return range(1, n + 1), values_time, values_s3_time

x, y, y2 = read_file('result_fetch.json')
x2, y3, y4 = read_file('result_resize.json')
df=pd.DataFrame({'x': x,
                 'y': y,
                 'y2': y2,
                 'y3': y3,
                 'y4': y4})
                 # 'end-to-end time (resize)': y3,
                 # 's3 time (resize)': y4})
plt.plot( 'x', 'y', data=df, marker='', color='olive', linewidth=2, label="end-to-end time (fetch)")
plt.plot( 'x', 'y2', data=df, marker='', color='olive', linewidth=2, linestyle='dashed', label="s3 time (fetch)")
plt.plot( 'x', 'y3', data=df, marker='', color='r', linewidth=2, label="end-to-end time (resize)")
plt.plot( 'x', 'y4', data=df, marker='', color='r', linewidth=2, linestyle='dashed', label="s3 time (resize)")
plt.legend()
plt.show()
