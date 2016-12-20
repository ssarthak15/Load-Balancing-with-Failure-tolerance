For Description of the project:
Goto SHARD HTML > index.html

Running the project:

1) Place the folders 'client' and 'shard1', 'shard2', 'shard3' and 'monitor'(can be found in p1 folder) into your home directory
2) Open Five instances of the terminal/putty
3) In first, second and third Terminal/putty instances change directory to shard1, shard2 and shard3 respectively

	cd shard1
	cd shard2
	cd shard3

4) run the shards

	python shard1.py -config configfile.json
	python shard1.py -config configfile.json
	python shard1.py -config configfile.json

5) In fourth and fifth Terminal/putty instance change directory to client and monitor respectively

	cd client
	cd monitor

6) run the client and monitor

	python client.py -config configfile.json -upload file1.jpg
	python monitor.py -config configfile.json

NOTE:
file1.jpg is included in client directory as a sample file that can be uploaded
file2.jpg is included in shard directories as a sample file that can be downloaded

The metadata file(included in shards) contains some information about file2.jpg this is done so as to help the tester to understand the structure of the metadata file.
The tester if need be can delete the contents of the metadata file and replce it with '0'(total byets stored) remember if you do this you won't be able to download file2.jgp(delete it as well)

Special Function:
To delete all files on the shards and reset the metadata file use the folling command

python client.py -config configfile.json -eraseall

The monitor will generate a .csv file which can be viewed by using microsoft Excel.
