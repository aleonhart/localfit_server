
# Bulk Convert FIT to CSV
```bash
for f in `ls ~/Documents/garmindata/MONITOR/*.FIT`;do FILENAME=$(ls $f|cut -d"/" -f7|cut -d"." -f1); java -jar ~/Documents/code/fit_to_csv/java/FitCSVTool.jar -b ~/Documents/garmindata/MONITOR/${FILENAME}.FIT ~/Documents/garmindata/CSV/MONITOR_STRESS/${FILENAME}.csv;done
```

# Upload File
```python
import requests
r = requests.post('http://127.0.0.1:8000/app/gvamonitorupload/', data={"file": "testdata/monitor_testfile.csv"})
```
# Bulk upload files
```bash
for f in `ls ~/Documents/garmindata/MONITOR/*.FIT`;do FILENAME=$(ls $f|cut -d"/" -f7|cut -d"." -f1); echo "import requests; r = requests.post('http://127.0.0.1:8000/app/gvamonitorupload/', data={'file': '/Users/YOU/Documents/garmindata/CSV/MONITOR_STRESS/$FILENAME.csv'}); print(r)"|python;done
```

# Get data
```python
import requests
r = requests.get('http://127.0.0.1:8000/app/stress_data/')
r = requests.get('http://127.0.0.1:8000/app/stress_data/?start_date=2019-10-26&end_date=2019-10-27')
```


