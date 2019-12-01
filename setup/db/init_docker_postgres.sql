/* create table that contains couple of coordinates and initialise with
a million random points*/
CREATE TABLE points (
  id SERIAL UNIQUE NOT NULL,
  x1 FLOAT,
  y1 FLOAT,
  x2 FLOAT,
  y2 FLOAT
);

insert into points (x1,y1,x2,y2)
select
random() * 100 as i,
random() * 100 as i,
random() * 100 as i,
random() * 100 as i
from generate_series(1,1000000);