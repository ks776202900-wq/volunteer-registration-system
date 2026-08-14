-- schema.sql
-- Run this once against your MySQL server to set up the database and table.
-- Example:  mysql -u root -p < schema.sql

CREATE DATABASE IF NOT EXISTS volunteer_db
    CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE volunteer_db;

CREATE TABLE IF NOT EXISTS volunteers (
    id                 INT AUTO_INCREMENT PRIMARY KEY,
    name               VARCHAR(100)  NOT NULL,
    age                INT           NOT NULL,
    gender             VARCHAR(30)   NOT NULL,
    email              VARCHAR(150)  NOT NULL UNIQUE,
    phone              VARCHAR(20)   NOT NULL UNIQUE,
    address            VARCHAR(255),
    area_of_interest   VARCHAR(50)   NOT NULL,
    skills             VARCHAR(255),
    availability       VARCHAR(30)   NOT NULL,
    registered_on      DATETIME      NOT NULL,
    CONSTRAINT chk_age CHECK (age BETWEEN 15 AND 100)
) ENGINE=InnoDB;
