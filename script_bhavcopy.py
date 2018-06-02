import zipfile, urllib.request, csv
import redis


connection = redis.Redis('localhost')
connection.flushall()


url = "https://www.bseindia.com/download/BhavCopy/Equity/EQ290518_CSV.ZIP"
zip, headers = urllib.request.urlretrieve(url)

with zipfile.ZipFile(zip) as zf:
    csv_files = [name for name in zf.namelist() if name.endswith('.CSV')]
    for filename in csv_files:
        with zf.open(filename) as source:
            reader = csv.reader(
                                    [line.decode('iso-8859-1')
                                    for line in source]
                                    )
            next(reader, None)
            for item in reader:
                print(float(item[7])-float(item[4]))
                connection.lpush(item[1].strip(), item[0], item[4], item[5], item[6], item[7])
                connection.zadd("stock_rank", item[1].strip(), float(item[7])-float(item[4]))
