BLINK EYE

Our project focuses on the eye health and the performance analysis of the student or any corporate workers.
First , we are counting the blinks per minute of user and will show the blink per minute chart, if he is blinking frequently to keep his eye healthy.
We are also keeping a record of our facetime to get the knowledge about his concentration while facing the screen.

How to run:

git clone https://github.com/abhijeetmandloi/software_project.git
Install flask, flask_sqlalchemy, psycopg2
Create database in postgres by name “blink”
Create two table blink_data, screentime
CREATE TABLE blink_data(ID INT PRIMARY KEY NOT NULL,USERNAME CHAR(50),BLINK_COUNT INT,TIMEDURATION INT,TIME CHAR(50),SESSIONDATE CHAR(50));
create table screentime(ID INT PRIMARY KEY NOT NULL,USERNAME CHAR(50),PERCENTAGE INT,TIMEDURATION INT,TIME CHAR(50),SESSIONDATE CHAR(50));
Edit user and password in app.py at line 16 and 32.


