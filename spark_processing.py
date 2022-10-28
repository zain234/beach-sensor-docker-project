import json
from bson import json_util
from dateutil import parser
from pyspark import SparkContext, SparkConf
from kafka import KafkaConsumer, KafkaProducer

#Mongo DB
from pymongo import MongoClient
client = MongoClient('mongodb', 27017)
db = client['StreamingDataDB']
collection = db['StreamingDataCollection']
    
def structure_validate_data(msg):
    
    
    data_dict={}
    
    #create RDD
    rdd=sc.parallelize(msg.value.decode("utf-8").split())
    
    data_dict["RawData"]=str(msg.value.decode("utf-8"))
    print(data_dict)
    
    #data validation and create json data dict
    try:
        data_dict["TimeStamp"]=parser.isoparse(rdd.collect()[0])
        
    except Exception as error:
        
        
        data_dict["TimeStamp"]="Error"
    
    try:
        data_dict["WaterTemperature"]=float(rdd.collect()[1])
        
        if (((data_dict["WaterTemperature"])>99) | ((data_dict["WaterTemperature"])<-10)):
            
            data_dict["WaterTemperature"]="Sensor Malfunctions"
        
        
    except Exception as error:
        
        
        data_dict["WaterTemperature"]="Error"
        
        
    try:
        data_dict["Turbidity"]=float(rdd.collect()[2])
        
        if (((data_dict["Turbidity"])>5000)):
            
            data_dict["Turbidity"]="Sensor Malfunctions"
        
        
    except Exception as error:
        
        
        data_dict["Turbidity"]="Error"
        
    
        
    try:
        data_dict["BatteryLife"]=float(rdd.collect()[3])
        
    except Exception as error:
        
        data_dict["BatteryLife"]="Error"
    
    
    try:
        data_dict["Beach"]=str(rdd.collect()[4])
        
    except Exception as error:
            
        data_dict["Beach"]="Error"
        
    try:
        data_dict["MeasurementID"]=int(str(rdd.collect()[5]).replace("Beach",""))
        
    except Exception as error:
        
        data_dict["MeasurementID"]="Error"

    
    
    return data_dict

conf = SparkConf().setAppName("PySpark App").setMaster("spark://spark-master:7077")
sc=SparkContext(conf=conf).getOrCreate()
# sc=SparkContext().getOrCreate()
sc.setLogLevel("WARN")

consumer = KafkaConsumer('SensorData', auto_offset_reset='earliest',bootstrap_servers=['kafka:9093'], consumer_timeout_ms=1000)

producer = KafkaProducer(bootstrap_servers=['kafka:9093'])

for msg in consumer:
    print(msg.value.decode("utf-8"))
    if msg.value.decode("utf-8")!="Error in Connection":
        data=structure_validate_data(msg)       
        
        #push data to mongo db
        collection.insert_one(data)
        producer.send("CleanedData", json.dumps(data, default=json_util.default).encode('utf-8'))
        
        print(data)