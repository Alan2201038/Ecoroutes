import csv
import pandas as pd
import requests

# Read the original CSV file
original_csv_file = 'HDB.csv'
merged_csv_file = 'HDB_new.csv'

def create_new_csv(original, merged):
    # Store the merged data in a list of dictionaries
    csv_data = []
    with open(original_csv_file, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            merged_location = row['blk_no'] + ' ' + row['street']
            csv_data.append({'location': merged_location})

    # Write the merged data to a new CSV file
    with open(merged_csv_file, mode='w', newline='') as csvfile:
        fieldnames = ['location']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(csv_data)

def getcoordinates(address):
    req = requests.get('https://developers.onemap.sg/commonapi/search?searchVal='+address+'&returnGeom=Y&getAddrDetails=Y&pageNum=1')
    resultsdict = eval(req.text)
    if len(resultsdict['results'])>0:
        return resultsdict['results'][0]['LATITUDE'], resultsdict['results'][0]['LONGITUDE']
    else:
        pass

df = pd.read_csv(r"HDB_new.csv")
df.head()
addresslist = list(df['location'])
coordinateslist= []
count = 0
failed_count = 0
for address in addresslist:
    try:
        if len(getcoordinates(address))>0:
            count = count + 1
            print('Extracting',count,'out of',len(addresslist),'addresses')
            coordinateslist.append(getcoordinates(address))
    except:
        count = count + 1           
        failed_count = failed_count + 1
        print('Failed to extract',count,'out of',len(addresslist),'addresses')
        coordinateslist.append(None)
print('Total Number of Addresses With No Coordinates',failed_count)