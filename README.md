<h2>BLINK EYE</h2>

Our project focuses on the eye health and the performance analysis of the student or any corporate workers.
First , we are counting the blinks per minute of user and will show the blink per minute chart, if he is blinking frequently to keep his eye healthy.
We are also keeping a record of our facetime to get the knowledge about his concentration while facing the screen.

<h4>How to run:</h4>

git clone https://github.com/abhijeetmandloi/software_project.git</br>
Install flask, flask_sqlalchemy, psycopg2</br>
Create database in postgres by name “blink”</br>
Create two table blink_data, screentime</br>
CREATE TABLE blink_data(ID INT PRIMARY KEY NOT NULL,USERNAME CHAR(50),BLINK_COUNT INT,TIMEDURATION INT,TIME CHAR(50),SESSIONDATE CHAR(50));</br>
create table screentime(ID INT PRIMARY KEY NOT NULL,USERNAME CHAR(50),PERCENTAGE INT,TIMEDURATION INT,TIME CHAR(50),SESSIONDATE CHAR(50));</br>
Edit user and password in app.py at line 16 and 32.</br>


