import os
from celery import Celery
from celery.utils.log import get_task_logger
import datetime
from meter_list import all_meters
import base64
# from influxdb_client_3 import InfluxDBClient3

app = Celery('tasks', broker=os.getenv("CELERY_BROKER_URL"))
logger = get_task_logger(__name__)


@app.task
def add(x, y):
    logger.info(f'Adding {x} + {y}')
    return x + y

def get_label_dict(dictionary, hm_sn):
        
    for k, v in dictionary.items():
        if hm_sn in v:
            return k
    return 'unknown'  # If sn is not found


@app.task
def elvaco_data_handler(site, content):

    content = base64.b64decode(content)

    #decoded_content = content.decode('cp855').split('\r\n')

    return content

    # token = "jXnUO24O5Dk5H6L7uzWEDXTaBbzOdg5zq06mD1BAaCaEDFEoqbbPTQmt0L6Y8as4Y-9t1af4v7t-VWeElZyzBw=="
    # org = "j.wright@pinnaclepower.co.uk"
    # host = "https://westeurope-1.azure.cloud2.influxdata.com"
    # bucket = "Elvaco_Data"

    ### Define Influx measurement and fields

    influx_measurement = site + '_meter_data'

    ### Create empty shell for inital meter json list

    all_meters_json = []

    ### Extract content line by line and define headers from values

    for line in content:

        if '#serial-number' in line:

            headers = line.split(";")

        else:

            values = line.split(";")

            if len(headers) == len(values):

                all_meters_json.append(dict(zip(headers, values)))

    ### Start creating influx object for each meter in file

    influx_json_body = []

    for meter in all_meters_json:

        read_TS = meter['created']

        utc_time = int(datetime.datetime.strptime(read_TS, "%Y-%m-%d %H:%M:%S").timestamp())

        del meter['created']

        influx_tag_headers = ['#serial-number', 'device-identification','device-position', 'value-data-count','manufacturer','version','device-type','access-number','status','signature']

        influx_tags = {x: meter[x] for x in influx_tag_headers}

        influx_field_headers = [x for x in list(meter.keys()) if x not in influx_tag_headers]

        influx_fields = {x: meter[x] for x in influx_field_headers}

        meter_sn = int(influx_tags['device-identification'])

        ## new label finder:



        label = get_label_dict(all_meters[site], meter_sn)

        influx_tags['meter_label'] = label

        for x in influx_fields:

            influx_fields[x] = influx_fields[x].replace(',','.')

            if isinstance(x, float):

                continue

            else: 
                try:

                    influx_fields[x] = float(influx_fields[x])

                except:

                    influx_fields[x] = influx_fields[x]


        influx_json_body.append(
            {
                "measurement": influx_measurement,
                "tags": influx_tags,
                "time": utc_time,
                "fields": influx_fields
            }
            )
        
    # client = influxdb_client.InfluxDBClient(
    # url=host,
    # token=token,
    # org=org
    # )

    # points = influx_json_body

    # client = InfluxDBClient3(token=token,
    #                 host=host,
    #                 database="Elvaco_Data",
    #                 org=org)
    
    # for point in points:
        
    #     write_influx = client.write(record=point, write_precision="s")

    #write_api = client.write_api(write_options=SYNCHRONOUS)

    #write_api.write(bucket, org, points)

    return influx_json_body
