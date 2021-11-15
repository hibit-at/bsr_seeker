import requests
import re


start = '1a000'
end = '1b000'

end_num = int(end, 16)

manu_range = 0

start_num = int(start, 16)

if manu_range > 0:
    start_num = end-manu_range

log_path = 'download_log.txt'

for i in range(start_num, end_num):
    bsr_key = hex(i)[2:]
    url = 'https://api.beatsaver.com/maps/id/' + bsr_key
    res = requests.get(url).json()
    if 'error' in res:
        continue
    name = res['name']
    author = res['uploader']['name']
    score = res['stats']['score']
    latest = res['versions'][0]
    dURL = latest['downloadURL']
    print(bsr_key, name, score)
    if score >= 0.75:
        get = requests.get(dURL)
        filename = f'{bsr_key} ({name}).zip'
        filename = re.sub(r'[\\/:*?"<>|]+', '', filename)
        open(filename, 'wb').write(get.content)
        print(filename, 'saved!')
        with open(log_path, mode='a') as f:
            f.write(f'{filename} saved!\n')
