#!/bin/bash 
# Waiting for the EOF
echo "Waiting for the data"
while [ ! -f "${PYTHON_MONGODB_EOF}" ]
 do sleep 1
done
echo "Zipepd data uploaded"

#Unzip the data
#chmod 755 "${EXPORT_PATH}"
tar -k -xvf "${MONGODB_ZIP_DATA_PATH}.tar" -C "${MONGODB_DATA_PATH}"

# Load data into MongoDB
mongoimport --db=${MONGO_INITDB_DATABASE} --collection=basics --type=tsv --file="${MONGODB_DATA_PATH}/${BASICS_TABLE_FILE}" --headerline --username=${MONGODB_USER} --password=${MONGODB_PASSWORD} --authenticationDatabase=admin
mongoimport --db=${MONGO_INITDB_DATABASE} --collection=ratings --type=tsv --file="${MONGODB_DATA_PATH}/${RATINGS_TABLE_FILE}" --headerline --username=${MONGODB_USER} --password=${MONGODB_PASSWORD} --authenticationDatabase=admin
mongoimport --db=${MONGO_INITDB_DATABASE} --collection=dates --type=tsv --file="${MONGODB_DATA_PATH}/${DATES_TABLE_FILE}" --headerline --username=${MONGODB_USER} --password=${MONGODB_PASSWORD} --authenticationDatabase=admin

