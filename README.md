
# LocalFit
This is a REST API for uploading, storing, and viewing FIT data on your local computer. It pairs with 
[a ReactJS front end](https://github.com/aleonhart/localfit_frontend).

# Dependencies
This API is powered by [Python](https://www.python.org/) and [Django REST Framework](https://www.django-rest-framework.org/).

Examples in this documentation use the [python requests](https://requests.readthedocs.io) library.

## Credits
A special shout out to [python-fitparse](https://github.com/dtcooper/python-fitparse), a handy way to handle 
FIT data in Python.

## Initial Project Setup
Install the dependencies
```bash
pip install requirements.txt
```

Initialize empty database schema. Note that this server has no data migrations. Data must be inserted by the user.
```bash
python manage.py migrate
```

## Start Local Development Server
```bash
python manage.py runserver
```

# Monitor Files
## Upload a Single Monitor File
```python
requests.post('http://127.0.0.1:8000/monitor/upload/', data={'file': '/Users/YOU/Documents/garmindata/MONITOR/82AK4813.FIT'})
```
## Upload Monitor Files in Bulk
```bash
for f in `ls ~/Documents/garmindata/MONITOR/*.FIT`;do echo "import requests; r = requests.post('http://127.0.0.1:8000/monitor/upload/', data={'file': '$f'});print(r.json())"|python; echo $f;done
```

## Viewing Monitor Data
### Stress Data
View all data or a range of dates
```python
requests.get('http://127.0.0.1:8000/monitor/stress_data/')
requests.get('http://127.0.0.1:8000/monitor/stress_data/?start_date=2018-02-01%2000:00:00&end_date=2018-02-02%200:00:00')
```

### Heart Rate Data
View all data or a range of dates
```python
requests.get('http://127.0.0.1:8000/monitor/heart_rate/')
requests.get('http://127.0.0.1:8000/monitor/heart_rate/?start_date=2018-02-01%2000:00:00&end_date=2018-02-02%200:00:00')
```

### Resting Metabolic Rate Data
View all data or a range of dates
```python
requests.get('http://127.0.0.1:8000/monitor/resting_meta/')
requests.get('http://127.0.0.1:8000/monitor/resting_meta/?start_date=2018-02-01%2000:00:00&end_date=2018-02-02%200:00:00')
```

# Activity Files
## Upload a Single Activity File
```python
r = requests.post('http://127.0.0.1:8000/activity/upload/', data={"file": "/Users/YOU/Documents/garmindata/ACTIVITY/9CUB1048.FIT"})

r                                                                                                                                                                
<Response [201]> 
```

## Viewing Activity Data
### Activity MetaData
View metadata for all activities or a single activity
```python
r = requests.get('http://127.0.0.1:8000/activity/meta/')
r = requests.get('http://127.0.0.1:8000/activity/meta/<filename>/')
```

### Activity Heart Rate Data
View heart rate data for a single activity
```python
r = requests.get('http://127.0.0.1:8000/activity/heart_rate/<filename>/')

r                                                                                                                                                                
<Response [200]>

r.json()                                                                                                                                                         

{
    'start_time': '2018-02-14T15:05:43-08:00',
    'end_time': '2018-02-14T15:45:08-08:00',
    'heart_rate': [
        {
            't': '2018-02-14T15:05:43-08:00', 
            'y': 60
        },
        {
            't': '2018-02-14T15:05:44-08:00', 
            'y': 61
            },
    ]
}
```

### Activity Map Data
View map data for a single activity, for activities with GPS coordinates
```python
r = requests.get('http://127.0.0.1:8000/activity/map/<filename>/')

r                                                                                                                                                                
<Response [200]>

r.json()                                                                                                                                                         
{
    'activitydata': [
        {
            'lat': 00.000000, 
            'lng': 000.000000
        },
        {
            'lat': 00.000000, 
            'lng': 000.000000
        },
    ],
    'start_position_lat_deg': 00.000000,
    'start_position_long_deg': 000.000000,
    'midpoint_lat_deg': 00.000000,
    'midpoint_long_deg': 000.000000
}
```

### Activity Altitude Data
View altitude data for a single activity
```python
r = requests.get('http://127.0.0.1:8000/activity/altitude/<filename>/')

r                                                                                                                                                                
<Response [200]>

r.json()                                                                                                                                                         
{
    'start_time': '2018-02-14T15:05:43-08:00',
    'end_time': '2018-02-14T15:45:08-08:00',
    'altitude': [
        {
            't': '2018-02-14T15:05:43-08:00', 
            'y': 1000.0
        },
        {
            't': '2018-02-14T15:05:44-08:00', 
            'y': 1000.0
        },
    ]
}
```

# Totals Files
## Upload a single totals file
```python
r = requests.post('http://127.0.0.1:8000/totals/upload/', data={"file": "/Users/YOU/Documents/garmindata/TOTALS/TOTALS.FIT"})

r                                                                                                                                                                
<Response [201]>                   
```

## Viewing Totals Data
```python
r = requests.get('http://127.0.0.1:8000/totals/meta/')

r                                                                                                                                                                
<Response [200]>

r.json()                                                                                                                                                         
{
    'timer_time': 50, 
    'distance': 200.0, 
    'calories': '20,000'
}
```

# File Type Conversion
## Convert FIT files to CSV
Use the [Fit SDK](https://www.thisisant.com/developer/ant/ant-fs-and-fit1/) to understand the FIT protocol and to 
convert FIT files to CSV files.
```bash
java -jar ~/Documents/code/fit_to_csv/java/FitCSVTool.jar -b ~/Documents/garmindata/ACTIVITY/<filename>.FIT ~/Documents/garmindata/CSV/ACTIVITY/<filename>
java -jar ~/Documents/code/fit_to_csv/java/FitCSVTool.jar -b ~/Documents/garmindata/MONITOR/<filename>.FIT ~/Documents/garmindata/CSV/MONITOR_STRESS/<filename>
```

## Bulk Convert FIT to CSV
```bash
for f in `ls ~/Documents/garmindata/MONITOR/*.FIT`;do FILENAME=$(ls $f|cut -d"/" -f7|cut -d"." -f1); java -jar ~/Documents/code/fit_to_csv/java/FitCSVTool.jar -b ~/Documents/garmindata/MONITOR/${FILENAME}.FIT ~/Documents/garmindata/CSV/MONITOR_STRESS/${FILENAME}.csv;done
```




