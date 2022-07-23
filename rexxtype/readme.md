# Readme.

## Database set up.
If you have docker installed you can launch your own mysql instance with:
```
docker run -it -d -p 3306:3306 -e MYSQL_ROOT_PASSWORD=password mysql:8
```

Next you would want to create the database with your _db.sql_ file.  This is used to create your database and table.

## Docker Compose.

I will leverage docker compose to deliver this application.  I will run the following command:
```
docker-compose up -d
```
and it will launch daemons for the DB and the app being served. If there is a different hierarchy, you would need to just change around the referenced volumes.

## Changing things around
If you need to change the db around, you will need to update the compose and the db.php file accordingly so it will handle the correct references.