-- Creates tables for the dataset
-- Creates relevent schemas and datatypes for each column

-- Creates a sample table of student (for testing purpose A0, will replace with picked dataset later).
CREATE TABLE IF NOT EXISTS Students (
    id INTEGER NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    gender VARCHAR(100) NOT NULL
    PRIMARY KEY (id)
);