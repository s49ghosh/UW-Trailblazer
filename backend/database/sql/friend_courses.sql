SELECT DISTINCT uf.friend_id, c.course_code, c.course_name, s.subject_name, s.avg_rating
FROM userfriends uf
JOIN users u ON uf.friend_id = u.uid
JOIN usertakencourses ut ON u.uid = ut.uid
JOIN courses c ON ut.course_code = c.course_code
JOIN subjects s ON c.subject_code = s.subject_code
WHERE uf.uid = 1
AND c.course_code IN (
    SELECT course_code
    FROM courses 
    WHERE u.uid = 2
)
