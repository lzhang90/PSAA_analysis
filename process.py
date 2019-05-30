import lib.file_unzip as unzip

#unzip all the logfiles
unzip.unzip("./data/raw_data_zipped","./data/raw_data_unzipped")

#rename all the log files with student id
unzip.file_rename("./data/raw_data_unzipped")