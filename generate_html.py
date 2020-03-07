from jinja2 import Environment, FileSystemLoader
import glob
import re
import pandas as pd
from datetime import datetime, timedelta
import pytz

def dt2jstdt(dt):
    dt = pytz.utc.localize(dt).astimezone(pytz.timezone('Asia/Tokyo'))
    return dt

def iso2jstdt(iso_str):
    dt = datetime.strptime(iso_str, '%Y-%m-%dT%H:%M:%S.%fZ')
    dt = dt2jstdt(dt)
    return dt

BASE_DIR = './data'
VIDEOS_FILE = 'video_data.csv'
HTML_FILE = 'index.html'
TEMPLATE_FILE ='template.html'

paths = glob.glob(BASE_DIR + '/killed/*/line/*')

data = []
df1 = pd.read_csv(VIDEOS_FILE, sep=',')
df1 = df1.set_index('video_id')
for path in paths:
    names = re.split('[/.]', path)
    video_id = names[-4]
    frame_id, roi_id = names[-2].split('-')
    global_id = ':'.join([video_id, frame_id, roi_id])

    timestamp = iso2jstdt(df1.at[video_id, 'start']) + timedelta(seconds=int(frame_id)//30)
    timestamp = timestamp.strftime('%Y/%m/%d %H:%M:%S.%f')[:-4]
    
    url = 'https://www.youtube.com/watch?v=' + video_id + '&t=' + str(int(frame_id)//30)

    channel_title = df1.at[video_id, 'channel_title']

    print(global_id, channel_title, timestamp, path, url)
    data.append([global_id, channel_title, timestamp, path, url])

df2 = pd.DataFrame(data, columns=['id', 'channel_title', 'timestamp', 'image', 'url'])
df2 = df2.sort_values(['timestamp', 'id'])
data = df2.to_dict('records')

env = Environment(loader = FileSystemLoader('./', encoding='utf8'), autoescape='html')
tmpl = env.get_template(TEMPLATE_FILE)
html = tmpl.render(data=data)
with open(HTML_FILE,mode='w',encoding='utf-8') as f:
    f.write(str(html))
