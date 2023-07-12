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

INSERT INTO Users (uid, first_name, last_name)
VALUES
    (1, 'John', 'Doe'),
    (2, 'Jane', 'Smith'),
    (3, 'Michael', 'Johnson');

INSERT INTO UserFriends (uid, friend_id)
VALUES
    (1, 2),
    (1, 3),
    (2, 1),
    (3, 1);

SELECT * FROM courses ORDER BY rating DESC LIMIT 10;
SELECT * FROM subjects ORDER BY avg_rating DESC LIMIT 10;

INSERT INTO Ratings (course_code, rating, uid)
VALUES
    ('CS 240', 5, 2),
    ('CS 241', 3, 3),
    ('CS 341', 5, 2),
    ('CS 350', 4, 3),
    ('CS 245', 1, 1),
    ('CS 240', 3, 3),
    ('CS 136', 4, 2),
    ('CS 136', 3, 1),
    ('ECE 222', 2, 1),
    ('ECE 222', 3, 3);

SELECT * FROM courses ORDER BY rating DESC LIMIT 10;
SELECT * FROM subjects ORDER BY avg_rating DESC LIMIT 10;

INSERT INTO UserTakenCourses (uid, course_code) VALUES (2, "CS 240");
SELECT prereq FROM Requirements WHERE course_code = "CS 341";
SELECT course_code FROM UserTakenCourses WHERE uid = 2;
INSERT INTO UserPlannedCourses (uid, course_code) VALUES (2, "CS 341");

SELECT * FROM Courses
JOIN Subjects ON Courses.subject_code = Subjects.subject_code
WHERE course_code LIKE "341"
AND Subjects.subject_code LIKE "" 
LIMIT 10;

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
);

INSERT INTO logindetails (uid, password)
VALUES
    (1, 'jdoe123'),
    (2, 'jsjsjs');

SELECT * FROM LoginDetails WHERE uid = 1;
SELECT * FROM Users WHERE uid = 1;

SELECT course_name, rating FROM courses ORDER BY rating DESC LIMIT 10;