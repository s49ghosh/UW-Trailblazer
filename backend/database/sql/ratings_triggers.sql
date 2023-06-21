DELIMITER //

CREATE TRIGGER update_ratings
AFTER UPDATE ON ratings
FOR EACH ROW
BEGIN
    DECLARE subjectCode VARCHAR(255);

    SELECT subject_code INTO subjectCode FROM courses WHERE course_code = NEW.course_code;

    UPDATE courses 
    SET rating = (SELECT AVG(rating) 
                  FROM ratings 
                  WHERE course_code = NEW.course_code) 
    WHERE course_code = NEW.course_code;

    UPDATE subject
    SET avg_rating = (SELECT AVG(eachrating)
                      FROM (SELECT AVG(rating) as eachrating
                            FROM ratings
                            WHERE course_code IN (SELECT course_code 
                                                  FROM courses 
                                                  WHERE subject_code = subjectCode)
                            GROUP BY course_code) as subquery)
    WHERE subject_code = subjectCode;
END; //

DELIMITER ;

DELIMITER //

CREATE TRIGGER insert_ratings
AFTER INSERT ON ratings
FOR EACH ROW
BEGIN
    DECLARE subjectCode VARCHAR(255);

    SELECT subject_code INTO subjectCode FROM courses WHERE course_code = NEW.course_code;

    UPDATE courses 
    SET rating = (SELECT AVG(rating) 
                  FROM ratings 
                  WHERE course_code = NEW.course_code) 
    WHERE course_code = NEW.course_code;

    UPDATE subject
    SET avg_rating = (SELECT AVG(eachrating)
                      FROM (SELECT AVG(rating) as eachrating
                            FROM ratings
                            WHERE course_code IN (SELECT course_code 
                                                  FROM courses 
                                                  WHERE subject_code = subjectCode)
                            GROUP BY course_code) as subquery)
    WHERE subject_code = subjectCode;
END; //

DELIMITER ;