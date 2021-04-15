DROP TABLE IF EXISTS staff;
DROP TABLE IF EXISTS student;
DROP TABLE IF EXISTS subjects;

CREATE TABLE staff (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  role TEXT NOT NULL,
  username TEXT UNIQUE,
  password TEXT ,
  subjects varchar,
  email TEXT UNIQUE,
  phoneNo INTEGER
);

CREATE TABLE student (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  prn INTEGER UNIQUE NOT NULL,
  name TEXT NOT NULL,
  course TEXT NOT NULL,
  year TEXT NOT NULL,
  rollNo INTEGER NOT NULL,
  email TEXT UNIQUE NOT NULL,
  phoneNo INTEGER UNIQUE
);

INSERT INTO staff (name, role, username, password)
VALUES ('admin', 'admin', 'admin', 'pbkdf2:sha256:150000$dKtPS1x6$2924ec7face4dc4cf1ae19ff5dbda2452cfcc1dbdcb5da4510b6179028f99d59');

CREATE TABLE subjects (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  subject TEXT UNIQUE NOT NULL,
  course TEXT NOT NULL,
  year TEXT NOT NULL
);