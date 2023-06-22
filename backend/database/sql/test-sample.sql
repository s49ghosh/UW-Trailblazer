-- Insert sample data into Users table
INSERT INTO Users (uid, first_name, last_name, start_year)
VALUES
    (1, 'John', 'Doe', 2019),
    (2, 'Jane', 'Smith', 2020),
    (3, 'Michael', 'Johnson', 2018);

-- Insert sample data into Subjects table
INSERT INTO Subjects (subject_code, subject_name, num_courses, avg_rating)
VALUES
    ('SUB1', 'Mathematics', 5, 4.2),
    ('SUB2', 'Computer Science', 8, 4.5),
    ('SUB3', 'Physics', 3, 3.8);

-- Insert sample data into Terms table
INSERT INTO Terms (term_id, course_code, start_date, end_date, term_season)
VALUES
    (1, 'COURSE1' , '2023-01-01', '2023-04-30', 'Spring'),
    (1, 'COURSE2' , '2023-01-01', '2023-04-30', 'Spring'),
    (2, 'COURSE3' , '2023-05-01', '2023-08-31', 'Summer'),
    (3, 'COURSE3' , '2023-09-01', '2023-12-31', 'Fall');

-- Insert sample data into Courses table
INSERT INTO Courses (course_code, course_name, subject_code, course_level, enroll_cap)
VALUES
    ('COURSE1', 'Calculus I', 'SUB1', 100, 50),
    ('COURSE2', 'Introduction to Programming', 'SUB2', 200, 40),
    ('COURSE3', 'Classical Mechanics', 'SUB3', 300, 30);

-- Insert sample data into UserFriends table
INSERT INTO UserFriends (uid, friend_id)
VALUES
    (1, 2),
    (1, 3),
    (2, 1),
    (3, 1);

-- Insert sample data into UserPlannedCourses table
INSERT INTO UserPlannedCourses (uid, course_code)
VALUES
    (1, 'COURSE2'),
    (2, 'COURSE3'),
    (3, 'COURSE1');

-- Insert sample data into UserTakenCourses table
INSERT INTO UserTakenCourses (uid, course_code)
VALUES
    (1, 'COURSE1'),
    (2, 'COURSE2'),
    (3, 'COURSE3');

-- Insert sample data into Ratings table
INSERT INTO Ratings (course_code, rating, uid)
VALUES
    ('COURSE1', 4, 1),
    ('COURSE2', 5, 2),
    ('COURSE3', 3, 3);
