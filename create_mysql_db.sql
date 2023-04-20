USE films;

CREATE TABLE IF NOT EXISTS basics (
        tconst VARCHAR(12) NOT NULL, titleType VARCHAR(12), primaryTitle VARCHAR(200),
        originalTitle VARCHAR(200), isAdult BOOLEAN, startYear INT,
        endYear DATETIME, runtimeMinutes FLOAT, genres VARCHAR(50),
        PRIMARY KEY (tconst)
        );

CREATE TABLE IF NOT EXISTS ratings (
        tconst VARCHAR(12) NOT NULL, averageRating FLOAT, numVotes INT,
        PRIMARY KEY (tconst)
        );
        
CREATE TABLE IF NOT EXISTS dates (
        tconst VARCHAR(12) NOT NULL, dataInsertTime DATE, PRIMARY KEY (tconst)
        );