# How does this work?
## Containers
when in the directory with docker-compose in it, you will call the command: `docker-compose up -d` which will launch the 3 containers.  Most of the data you need will be in the compose file.

### Application
This Container will run the app and serve everything inside of `./src` to `/var/www/html` and will serve on port 80.

### Database:
This container, is accessible to port 3306 like all Mysql Instances.  It is also known as db for dns or ip lookups for things.  I reccomend using db, though you can rename this to something better suited for you as long as you update the phpmyadmin reference.

### PHPMyAdmin
By Default this application will serve on port 8080, though you can change it as necessary

## Passwords
Make sure you change your password. I set up a sample pw in there for the `root` user, but you would want to add other user/passwords or update it accordingly to log into phpmyadmin proper.

## Folders
These are the key folders used in docker-compose, which you may want to adjust as needed.

### mysqlfolder
Any of the following files will be run in here, in alphabetical order.  This can be used to INIT your db. `.sh, .sql, .sql.gz, .sql.xz, .sql.zxt` and sh files arent run, they are sourced.  For more information about MariaDB please reference: https://hub.docker.com/_/mariadb

### currentdb
This is where the current db is being stored.  While you can do things like mysql dump etc, the live data will live in the folder currentdb

### src
This folder will contain all of your php files.  All items in here is equivalent to putting things in `/var/www/html/`.  You can also update location in the docker-compose file, if you like to point somewhere else.
