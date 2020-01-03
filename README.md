
# Local Development
This API is powered by [Python](https://www.python.org/) and [Django REST Framework](https://www.django-rest-framework.org/).

## Initial Project Setup
Initialize empty database schema. Note that this server has no data migrations. Data must be inserted by the user.
```bash
python manage.py migrate
```
## Start Local Server
```bash
python manage.py runserver
```
# Stress Monitor Files
## Upload a Single File
```python
import requests
r = requests.post('http://127.0.0.1:8000/monitor/gvamonitorupload/', data={"file": "testdata/monitor_testfile.csv"})
```
## Upload Files in Bulk
```bash
for f in `ls ~/Documents/garmindata/CSV/MONITOR_STRESS/*.csv`;do echo "import requests; r = requests.post('http://127.0.0.1:8000/app/gvamonitorupload/', data={'file': '$f'}); print(r)"|python;done
```

# Viewing Data from Database
```python
import requests
r = requests.get('http://127.0.0.1:8000/monitor/stress_data/')
r = requests.get('http://127.0.0.1:8000/monitor/stress_data/?start_date=2018-02-01&end_date=2018-03-01')
```

# Activity Files
## Upload a Single File
```python
import requests
r = requests.post('http://127.0.0.1:8000/activity/upload/', data={"file": "~/Documents/garmindata/CSV/ACTIVITY/9CUB1048.csv"})      
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