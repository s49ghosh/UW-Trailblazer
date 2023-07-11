DELIMITER //

CREATE TRIGGER update_ratings
AFTER UPDATE ON Ratings
FOR EACH ROW
BEGIN
    DECLARE subjectCode VARCHAR(255);

    SELECT subject_code INTO subjectCode FROM Courses WHERE course_code = NEW.course_code;

    UPDATE Courses 
    SET rating = (SELECT AVG(rating) 
                  FROM Ratings 
                  WHERE course_code = NEW.course_code) 
    WHERE course_code = NEW.course_code;

    UPDATE Subjects
    SET avg_rating = (SELECT AVG(eachrating)
                      FROM (SELECT AVG(rating) as eachrating
                            FROM Ratings
                            WHERE course_code IN (SELECT course_code 
                                                  FROM Courses 
                                                  WHERE subject_code = subjectCode)
                            GROUP BY course_code) as subquery)
    WHERE subject_code = subjectCode;
END; //

DELIMITER ;

DELIMITER //

CREATE TRIGGER insert_ratings
AFTER INSERT ON Ratings
FOR EACH ROW
BEGIN
    DECLARE subjectCode VARCHAR(255);

    SELECT subject_code INTO subjectCode FROM Courses WHERE course_code = NEW.course_code;

    UPDATE Courses 
    SET rating = (SELECT AVG(rating) 
                  FROM Ratings 
                  WHERE course_code = NEW.course_code) 
    WHERE course_code = NEW.course_code;

    UPDATE Subjects
    SET avg_rating = (SELECT AVG(eachrating)
                      FROM (SELECT AVG(rating) as eachrating
                            FROM Ratings
                            WHERE course_code IN (SELECT course_code 
                                                  FROM Courses 
                                                  WHERE subject_code = subjectCode)
                            GROUP BY course_code) as subquery)
    WHERE subject_code = subjectCode;
END; //

DELIMITER ;

-- Insert sample data into Users table
INSERT INTO Users (uid, first_name, last_name)
VALUES
    (1, 'John', 'Doe'),
    (2, 'Jane', 'Smith'),
    (3, 'Michael', 'Johnson');

-- Insert sample data into Subjects table
INSERT INTO Subjects (subject_code, subject_name, num_courses, avg_rating)
VALUES
    ('SUB1', 'Mathematics', 5, 4.2),
    ('SUB2', 'Computer Science', 8, 4.5),
    ('SUB3', 'Physics', 3, 3.8);

-- Insert sample data into Courses table
INSERT INTO Courses (course_code, course_name, subject_code, course_level)
VALUES
    ('COURSE1', 'Calculus I', 'SUB1', 100),
    ('COURSE2', 'Introduction to Programming', 'SUB2', 200),
    ('COURSE3', 'Classical Mechanics', 'SUB3', 300);

-- Insert sample data into Terms table
INSERT INTO Terms (term_id, start_date, end_date, term_season)
VALUES
    (1 , '2023-01-01', '2023-04-30', 'Winter'),
    (1 , '2023-01-01', '2023-04-30', 'Winter'),
    (2 , '2023-05-01', '2023-08-31', 'Spring'),
    (3 , '2023-09-01', '2023-12-31', 'Fall');


-- Insert sample data into EnrollCapacity table
INSERT INTO EnrollCapacity (course_code, term_id, enroll_cap)
VALUES
    (1, 'COURSE1', 50),
    (1, 'COURSE2', 40),
    (2, 'COURSE3', 30);


-- Insert sample data into UserFriends table
INSERT INTO UserFriends (uid, friend_id)
VALUES
    (1, 2),
    (1, 3),
    (2, 1),
    (3, 1);

-- Insert sample data into UserTakenCourses table
INSERT INTO UserTakenCourses (uid, course_code)
VALUES
    (1, 'COURSE1'),
    (2, 'COURSE1'),
    (2, 'COURSE2'),
    (3, 'COURSE1'),
    (3, 'COURSE2'),
    (3, 'COURSE3');

SELECT * FROM Courses;
SELECT * FROM Subjects;

-- Insert sample data into Ratings table
INSERT INTO Ratings (course_code, rating, uid)
VALUES
    ('COURSE1', 4, 1),
    ('COURSE1', 2, 2);

SELECT * FROM Courses;
SELECT * FROM Subjects;

INSERT INTO Ratings (course_code, rating, uid)
VALUES
    ('COURSE2', 5, 2),
    ('COURSE3', 3, 3);

SELECT * FROM Courses;
SELECT * FROM Subjects;

-- Insert sample data into Requirements table
INSERT INTO Requirements (course_code, prereq)
VALUES
    ('COURSE2', 'COURSE1'),
    ('COURSE3', 'COURSE2');

INSERT INTO UserTakenCourses (uid, course_code) VALUES (2, "COURSE3");
SELECT prereq FROM Requirements WHERE course_code = "COURSE3";
SELECT course_code FROM UserTakenCourses WHERE uid = 1;
INSERT INTO UserPlannedCourses (uid, course_code) VALUES (1, "COURSE2");


SELECT * FROM Courses 
JOIN Subjects ON Courses.subject_code = Subjects.subject_code
WHERE course_code LIKE "course1"
AND Subjects.subject_code LIKE "sub1";

SELECT DISTINCT uf.friend_id, c.course_code, c.course_name, s.subject_name, s.avg_rating
FROM userfriends uf
JOIN users u ON uf.friend_id = u.uid
JOIN usertakencourses ut ON u.uid = ut.uid
JOIN courses c ON ut.course_code = c.course_code
JOIN subjects s ON c.subject_code = s.subject_code
WHERE uf.uid = 1
AND c.course_code NOT IN (
    SELECT course_code
    FROM courses 
    WHERE u.uid = 1
)

-- Insert sample data into CourseAvailability table
INSERT INTO CourseAvailability (term_id, course_code)
VALUES
    (2, 'COURSE1'),
    (1, 'COURSE2'),
    (2, 'COURSE3'),
    (1, 'COURSE1');

