-- Creates tables for the dataset
-- Creates relevent schemas and datatypes for each column

CREATE TABLE Users (
    uid INT PRIMARY KEY NOT NULL,
    first_name TEXT,
    last_name TEXT,
);


CREATE TABLE Subjects (
    subject_code VARCHAR(10) PRIMARY KEY NOT NULL,
    subject_name VARCHAR(100),
    num_courses INT,
    avg_rating DECIMAL(3,2)
    
);

CREATE TABLE Terms (
    term_id INT PRIMARY KEY NOT NULL,
    start_date DATE,
    end_date DATE,
    term_season VARCHAR(10)
);


CREATE TABLE Courses (
    course_code VARCHAR(10) PRIMARY KEY NOT NULL,
    course_name VARCHAR(100),
    subject_code VARCHAR(10),    
    course_level INT,
    enroll_cap INT,
    FOREIGN KEY (subject_code) REFERENCES Subjects(subject_code)
);

CREATE TABLE UserFriends (
    uid INT NOT NULL,
    friend_id INT NOT NULL,
    PRIMARY KEY (uid, friend_id),
    FOREIGN KEY (uid) REFERENCES Users(uid),
    FOREIGN KEY (friend_id) REFERENCES Users(uid)
);

CREATE TABLE UserPlannedCourses (
    uid INT,
    course_code VARCHAR(10),
    PRIMARY KEY (uid, course_code),
    FOREIGN KEY (uid) REFERENCES Users(uid),
    FOREIGN KEY (course_code) REFERENCES Courses(course_code)
);


CREATE TABLE UserTakenCourses (
    uid INT,
    course_code VARCHAR(10),
    PRIMARY KEY (uid, course_code),
    FOREIGN KEY (uid) REFERENCES Users(uid),
    FOREIGN KEY (course_code) REFERENCES Courses(course_code)
);


CREATE TABLE Ratings (
    course_code VARCHAR(10) PRIMARY KEY NOT NULL,
    rating INT NOT NULL,
    uid INT NOT NULL,
    FOREIGN KEY (uid) REFERENCES Users(uid),
    FOREIGN KEY (course_code) REFERENCES Courses(course_code)
);
