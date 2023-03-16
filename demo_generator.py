import requests
import json
import openpyxl
import time

# load the Excel file
wb = openpyxl.load_workbook('HISTORIC_TETRA_202302161246.xlsx')

url = 'http://localhost:5000/api/coords'

headers = {'Content-Type': 'application/json'}

# select the first worksheet
ws = wb.active

# iterate through each row
for row in ws.iter_rows(min_row=2):  # start from row 2 to skip the header row
    # parse each column value
    col1 = row[1].value
    col2 = row[2].value
    col3 = row[3].value

    col2 = col2.replace(",", ".")
    col3 = col3.replace(",", ".")

    lat = float(col2)
    lon = float(col3);
    
    print(f"timestamp: {col1}, lat: {col2}, lon: {col3}")
    
    #data = {'latitude': 37.7749, 'longitude': -122.4194}
    data = {'latitude': lat, 'longitude': lon }
    response = requests.post(url, data=json.dumps(data), headers=headers)
    time.sleep(0.1)
    
    if response.status_code == 200:
      print(response.json())
else:
      print('Error:', response.status_code)
    


