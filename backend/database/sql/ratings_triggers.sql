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