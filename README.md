
# FIT to CSV Jar from ANT
java -jar fit_to_csv/java/FitCSVTool.jar -b testdata/monitor_testfile.FIT testdata/monitor_testfile.csv

# Upload File
r = requests.post('http://127.0.0.1:8000/app/gvamonitorupload/', data={"file": "testdata/monitor_testfile.csv"})

# Get data
r = requests.get('http://127.0.0.1:8000/app/stress_data/')

