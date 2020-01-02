
# File Conversion
## Convert FIT files to CSV
Use the [Fit SDK](https://www.thisisant.com/developer/ant/ant-fs-and-fit1/) to understand the FIT protocol and to 
convert FIT files to CSV files.
```bash
java -jar ~/Documents/code/fit_to_csv/java/FitCSVTool.jar -b /Users/YOU/Documents/garmindata/MONITOR/<filename>.FIT /Users/YOU/Documents/garmindata/CSV/MONITOR_STRESS/<filename>.csv
```

## Bulk Convert FIT to CSV
```bash
for f in `ls ~/Documents/garmindata/MONITOR/*.FIT`;do FILENAME=$(ls $f|cut -d"/" -f7|cut -d"." -f1); java -jar ~/Documents/code/fit_to_csv/java/FitCSVTool.jar -b ~/Documents/garmindata/MONITOR/${FILENAME}.FIT ~/Documents/garmindata/CSV/MONITOR_STRESS/${FILENAME}.csv;done
```
# Local Server
This API is powered by [Python](https://www.python.org/) and [Django REST Framework](https://www.django-rest-framework.org/).

## Initial Project Setup
Initialize empty database schema. Note that this server has no data migrations. Data must be inserted by the user.

```bash
python manage.py migrate
```
## Start Server
```bash
python manage.py runserver
```
# Stress Monitor Files
## Upload a Single Stress Monitor File
```python
import requests
r = requests.post('http://127.0.0.1:8000/monitor/gvamonitorupload/', data={"file": "testdata/monitor_testfile.csv"})
```
## Upload Stress Monitor Files in Bulk
```bash
for f in `ls ~/Documents/garmindata/CSV/MONITOR_STRESS/*.csv`;do echo "import requests; r = requests.post('http://127.0.0.1:8000/app/gvamonitorupload/', data={'file': '$f'}); print(r)"|python;done
```

# Viewing Stress Monitor Data
```python
import requests
r = requests.get('http://127.0.0.1:8000/monitor/stress_data/')
r = requests.get('http://127.0.0.1:8000/monitor/stress_data/?start_date=2018-02-01&end_date=2018-03-01')
```

# Activity Files

java -jar ~/Documents/code/fit_to_csv/java/FitCSVTool.jar -b ~/Documents/garmindata/ACTIVITY/82DI0102.FIT ~/Documents/garmindata/CSV/ACTIVITY/82DI0102