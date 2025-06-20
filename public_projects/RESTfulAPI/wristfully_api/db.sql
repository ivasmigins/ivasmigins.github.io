-- Create Database
CREATE DATABASE IF NOT EXISTS wristfullydb;

USE wristfullydb;

-- Create tables
CREATE TABLE IF NOT EXISTS users (
	username VARCHAR(20) NOT NULL PRIMARY KEY,
	password VARCHAR(255) NOT NULL,
	firstname VARCHAR(50) NOT NULL,
	lastname VARCHAR(50) NOT NULL,
	birthdate DATE NOT NULL
);

CREATE TABLE IF NOT EXISTS doctors (
	doctor_id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
	password VARCHAR(255) NOT NULL,
	firstname VARCHAR(50) NOT NULL,
	lastname VARCHAR(50) NOT NULL
);

CREATE TABLE IF NOT EXISTS watch (
	watch_id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
	version INT NOT NULL,
	api_key VARCHAR(255) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS watch_user (
	username VARCHAR(20) NOT NULL REFERENCES users (username),
	watch_id INT NOT NULL REFERENCES watch (watch_id),
	PRIMARY KEY(username, watch_id)
);

CREATE TABLE IF NOT EXISTS patients_doctor (
	username VARCHAR(20) NOT NULL REFERENCES users (username),
	doctor_id INT NOT NULL REFERENCES doctors (doctor_id),
	PRIMARY KEY(username, doctor_id)
);

-- Statistics
CREATE TABLE IF NOT EXISTS falls (
	falls_id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
	watch_id INT NOT NULL REFERENCES watch (watch_id),
	date DATETIME NOT NULL,
	stopped BIT NOT NULL -- BIT is a boolean
);

CREATE TABLE IF NOT EXISTS steps (
	steps_id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
	watch_id INT NOT NULL REFERENCES watch (watch_id),
	date DATE NOT NULL, -- Exact time not important		
	steps INT NOT NULL
);

CREATE TABLE IF NOT EXISTS blood_oxygen (
	blood_oxygen_id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
	watch_id INT NOT NULL REFERENCES watch (watch_id),
	date DATETIME NOT NULL,
	percentage INT NOT NULL
);

CREATE TABLE IF NOT EXISTS heart_rate (
	heart_rate_id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
	watch_id INT NOT NULL REFERENCES watch (watch_id),
	date DATETIME NOT NULL,
	bpm INT NOT NULL
);