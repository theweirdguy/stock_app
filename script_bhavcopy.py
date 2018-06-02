import zipfile, urllib.request, csv
import redis
import os

"""
The Algorithm is pretty simple. I use the urllib library to download the zip_csv file.
Next, I extract it with the ZIPFILE module and read it using the csv reader.
The data structure for the redis environment being used to store is a key, value pair of string and list.
Name is the key and the rest is list[Code, Open, High, Low, Close]
To calculate the top 10 stocks I used, an ordered set of Redis. 
The difference was being calculated as the rank for storing the set and name.
We finally use the set to fetch the top 10 keys based on the set rank and lastly queried this keys to fetch the list of top 10 data.
"""
def download_parse_csv(url):
    zip_obj, headers = urllib.request.urlretrieve(url)
    with zipfile.ZipFile(zip_obj) as zf:
        csv_files = [name for name in zf.namelist() if name.endswith('.CSV')]
        for filename in csv_files:
            with zf.open(filename) as source:
                reader = csv.reader(
                    [line.decode('iso-8859-1')
                     for line in source]
                )
                next(reader, None)      # Skip the header of CSV while storing the data to redis
                for item in reader:
                    """
                    Send the csv data, to redis as key, value pair where key is the name of the stock
                    and value is the rest of the data.
                    """
                    connection.lpush(item[1].strip(), item[0], item[4], item[5], item[6], item[7])

                    """
                    Capture also the difference between opening and closing price, to calculate the rank of 
                    stock so as to get the top ten names of company.
                    """
                    connection.zadd("stock_rank", item[1].strip(), float(item[7]) - float(item[4]))


if __name__ == '__main__':
    connection = redis.Redis('localhost')
    #connection = redis.from_url(os.environ.get("REDIS_URL"))
    connection.flushall()

    url = "https://www.bseindia.com/download/BhavCopy/Equity/EQ290518_CSV.ZIP"
    download_parse_csv(url)