#!/bin/bash 
# Load data into MySQL

# Wait for mysqld to be initalized
echo "Waiting for mysqld"
while ! mysqladmin ping -h localhost --user=${MYSQL_CUSTOM_USER} --password=${MYSQL_PASSWORD} 2> /dev/null; do
    echo "..."
    sleep 1
done
echo -e "\nmysqld ready !"

# Wait for the data
echo "Waiting for data"
while [ ! -f "${PYTHON_MYSQL_EOF}" ]; do sleep 1; done
echo "Zipped data uploaded"

# Unzip data
tar -xvf "${MYSQL_ZIP_DATA_PATH}.tar" -C "${MYSQL_DATA_PATH}"

IMPORT_REQUEST="""LOAD DATA INFILE '${MYSQL_DATA_PATH}/${DATES_TABLE_FILE}'
INTO TABLE ${DATES_TABLE}
IGNORE 1 ROWS
SET dataInsertTime = str_to_date(dataInsertTime, '%Y-%m-%d');

LOAD DATA INFILE '${MYSQL_DATA_PATH}/${BASIC_TABLE_FILE}'
INTO TABLE ${BASICS_TABLE}
IGNORE 1 ROWS;

LOAD DATA INFILE '${MYSQL_DATA_PATH}/${RATINGS_TABLE_FILE}'
INTO TABLE ${RATINGS_TABLE}
IGNORE 1 ROWS;
"""

# Load data into mysql
mysql -D ${DATABASE} --user=${MYSQL_CUSTOM_USER} --password=${MYSQL_PASSWORD} -e "${IMPORT_REQUEST}"
echo "Data loaded into ${DATABASE}"