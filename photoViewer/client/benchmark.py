import requests
import base64
import time
import threading
import configparser
import queue
import matplotlib.pyplot as plt
import json

config = configparser.ConfigParser()
config.read('benchmark.config')
TEMPLATE = "http://{ip}:{port}/runLambda/{command}"

def worker(queue, s3_queue, server_ip, server_port, aws_access_key_id, aws_secret_access_key, file_name, command, test_period):
    test_period_start = time.time()
    tokens = command.split(' ')
    url = TEMPLATE.format(ip=server_ip, port=server_port, command=tokens[0])
    data = {'aws_access_key_id': aws_access_key_id,
            'aws_secret_access_key': aws_secret_access_key,
            'file_name': file_name}
    if tokens[0] == 'resize':
        data['width'] = int(tokens[1])
        data['height'] = int(tokens[2])
    while time.time() - test_period_start < test_period:
        # send the request
        start = time.time()
        r = requests.post(url, json = data)
        end = time.time()
        json_result = json.loads(r.text)
        s3_time = float(json_result['time'])
        result = json_result['result']
        if (len(result) >= 200):
            result = result[:200] + '...'
        print("Result: {}".format(result))
        print("S3 Time: {}".format(s3_time))
        print("Request Time: {}".format(end - start))
        queue.put(end - start)
        s3_queue.put(s3_time)

def send_requests(config_name, repeat_times):
    thread_group = []
    q = queue.Queue()
    s3_q = queue.Queue()
    for i in range(repeat_times):
        test_thread = threading.Thread(
          target=worker, kwargs=dict(queue = q,
                                     s3_queue = s3_q,
                                     server_ip = config[config_name]['SERVER_IP'],
                                     server_port = config[config_name]['SERVER_PORT'],
                                     aws_access_key_id = config[config_name]['AWS_ACCESS_KEY_ID'],
                                     aws_secret_access_key = config[config_name]['AWS_SECRET_ACCESS_KEY'],
                                     file_name = config[config_name]['FILE_NAME'],
                                     command = config[config_name]['COMMAND'],
                                     test_period = int(config[config_name]['TEST_PERIOD'])));
        test_thread.start()
        thread_group.append(test_thread)
    for t in thread_group:
        t.join()
    print('Finished.')
    return list(q.queue), list(s3_q.queue)


if __name__ == "__main__":
    x = []
    y = []
    final_result = {}
    for i in range(1, int(config['DEFAULT']['REPEAT']) + 1):
        result, s3_result = send_requests('DEFAULT', i)
        avg = sum(result)/len(result)
        avg_s3 = sum(s3_result)/len(s3_result)
        final_result[i] = {'time': avg, 's3_time': avg_s3}
        print("request count: {}, avg time: {}, avg s3 time: {}".format(i, avg, avg_s3))
        x.append(i)
        y.append(avg)
    with open('result.json', 'w') as fw:
        json.dump(final_result, fw)
