### Create the Conda Enviornment 
```
create env create -f pyspark_env.yml
```

### Running the Socket server file in windows 
```
python socket.server.py
```

### PYspark streaming that fetch socket streams and calculates the sentiments 
```
python process_stream.py
```