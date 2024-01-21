import json

from flask import Flask, request, jsonify
import connect
import register

app = Flask(__name__)


@app.route('/api/userprofile', methods=['POST'])
def userinfo():
    titles = connect.query("SHOW COLUMNS FROM Students")
    data = request.get_json()
    if 'username' not in data:
        return jsonify({'error': 'Missing username field'}), 400

    username = data['username']
    count = connect.query(f"SELECT COUNT(*) FROM Students WHERE username = '{username}'")[0][0]
    if count == 0:
        return jsonify({'error': 'Username does not exist'}), 400

    results = connect.query(f"SELECT * FROM Students WHERE username = '{username}'")
    keys = []
    for title in titles:
        if title[0] != 'hashedPassword' and title[0] != 'salt':
            keys.append(title[0])

    values = []
    for entry in results[0]:
        values.append(entry)

    data_dict = dict(zip(keys, values))

    # Convert the dictionary to a JSON-formatted string
    return jsonify(data_dict)

@app.route('/api/friends', methods=['POST'])
def friends():
    friend_titles = connect.query("SHOW COLUMNS FROM Friends")
    data = request.get_json() #json body
    if 'username' not in data:
        return jsonify({'error': 'Missing username field'}), 400

    username = data['username']
    count = connect.query(f"SELECT COUNT(*) FROM Students WHERE username = '{username}'")[0][0]
    if count == 0:
        return jsonify({'error': 'Username does not exist'}), 400

    record_count = connect.query(f"SELECT COUNT(*) FROM Friends WHERE username = '{username}'")[0][0]
    results = connect.query(f"SELECT * FROM Friends WHERE username = '{username}'")
    dictionary = {}
    dictionary['count'] = record_count

    keys = []
    for j in range(1, len(friend_titles)):
        title = friend_titles[j]
        keys.append(title[0])

    all_friends = []

    for i in range(0, record_count):
        values = []
        if results:
            values.append(results[i][1])

        data_dict = dict(zip(keys, values))
        all_friends.append(data_dict)

    dictionary['results'] = all_friends

    # Convert the dictionary to a JSON-formatted string
    return jsonify(dictionary)

@app.route('/registeredcourses', methods=['POST'])
def registeredcourses():
    data = request.get_json() #json body

    if 'username' not in data:
        return jsonify({'error': 'Missing username field'}), 400

    username = data['username']

    enrolled_titles = connect.query("SHOW COLUMNS FROM Enrolled")
    section_titles = connect.query("SHOW COLUMNS FROM Sections")

    count = connect.query(f"SELECT COUNT(*) FROM Students WHERE username = '{username}'")[0][0]
    if count == 0:
        return jsonify({'error': 'Username does not exist'}), 400

    record_count = connect.query(f"SELECT COUNT(*) FROM Enrolled WHERE username = '{username}'")[0][0]

    dictionary = {}
    dictionary['count'] = record_count

    results = connect.query(f"SELECT * FROM Enrolled WHERE username = '{username}' AND Term = '2023W2'")
    sql_query = f"""
    SELECT
    Sections.term,
    Sections.section,
    Sections.courseNum,
    Sections.courseDept,
    Sections.daysOfWeek,
    Sections.startTime,
    Sections.endTime
FROM
    Sections
INNER JOIN
    Enrolled ON Sections.term = Enrolled.term
              AND Sections.section = Enrolled.section
              AND Sections.courseNum = Enrolled.courseNum
              AND Sections.courseDept = Enrolled.courseDept
    WHERE Enrolled.username = '{username}' AND Sections.term = '2023W2';
    """

    results = connect.query(sql_query)

    keys = []
    for j in range(1, len(enrolled_titles)):
         title = enrolled_titles[j]
         keys.append(title[0])
    for j in range(len(section_titles)):
        title = section_titles[j]
        if (not keys.__contains__(title[0])):
            keys.append(title[0])

    all_enrollments = []

    for i in range(0, record_count):
        values = []
        if results:
            current = results[i]
            for j in range(1, len(current)):
                values.append(current[j])

        data_dict = dict(zip(keys, values))
        all_enrollments.append(data_dict)

    dictionary['results'] = all_enrollments

    # Convert the dictionary to a JSON-formatted string
    return jsonify(dictionary)

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json() #json body
    if 'username' not in data:
        return jsonify({'error': 'Missing username field'}), 400
    if 'password' not in data:
        return jsonify({'error': 'Missing password field'}), 400

    username = data['username']
    password = data['password']

    count = connect.query(f"SELECT COUNT(*) FROM Students WHERE username = '{username}'")[0][0]
    if count == 0:
        return jsonify({'error': 'Username does not exist'}), 400

    if(register.authenticate_user(username, password)):
        return jsonify({'success': 'Login successful'}), 200
    else:
        return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/users', methods=['POST'])
def users():
    data = request.get_json()
    if 'username' not in data:
        return jsonify({'error': 'Missing username field'}), 400
    if 'searchName' not in data:
        return jsonify({'error': 'Missing searchName field'}), 400

    titles = connect.query("SHOW COLUMNS FROM Students")

    username = data['username']
    searchName = data['searchName']
    count = connect.query(f"SELECT COUNT(*) FROM Students WHERE username = '{username}'")[0][0]
    if count == 0:
        return jsonify({'error': 'Username does not exist'}), 400

    record_count = connect.query(f"SELECT COUNT(*) FROM Students WHERE username LIKE '%{searchName}%' AND username != '{username}'")[0][0]
    results = connect.query(f"SELECT * FROM Students WHERE username LIKE '%{searchName}%' AND username != '{username}'")

    dictionary = {}
    dictionary['count'] = record_count

    search_results = []
    keys = []
    for title in titles:
        if title[0] != 'hashedPassword' and title[0] != 'salt':
            keys.append(title[0])
    for i in range(0, record_count):
        values = []
        for entry in results[i]:
            values.append(entry)

        data_dict = dict(zip(keys, values))
        search_results.append(data_dict)

    dictionary['results'] = search_results

    return jsonify(dictionary), 200

@app.route('/degreeinfo', methods=['POST'])
def degreeinfo():
    data = request.get_json()
    if 'username' not in data:
        return jsonify({'error': 'Missing username field'}), 400

    username = data['username']
    count = connect.query(f"SELECT COUNT(*) FROM Students WHERE username = '{username}'")[0][0]
    if count == 0:
        return jsonify({'error': 'Username does not exist'}), 400

    results = connect.query(f"SELECT * FROM Students WHERE username = '{username}'")
    degree_name = results[0][4]
    faculty_name = results[0][3]
    if degree_name == None or faculty_name == None:
        return jsonify({'error': 'No degree declared'}), 400

    requirement_results = connect.query(f"SELECT * FROM Requirements WHERE degreeName = '{degree_name}' AND faculty = '{faculty_name}'")
    requirement_titles = connect.query("SHOW COLUMNS FROM Requirements")
    record_count = connect.query(f"SELECT COUNT(*) FROM Requirements WHERE degreeName = '{degree_name}' AND faculty = '{faculty_name}'")[0][0]

    dictionary = {}
    dictionary['count'] = record_count

    keys = []
    for j in range(0, len(requirement_titles)-2):
        title = requirement_titles[j]
        keys.append(title[0])

    results_list = []
    for i in range(0, record_count):
        values = []
        if requirement_results:
            current = requirement_results[i]
            for j in range(0, len(current)-2):
                values.append(current[j])

        data_dict = dict(zip(keys, values))
        results_list.append(data_dict)

    dictionary['results'] = results_list

    return jsonify(dictionary), 200

@app.route('/courses', methods=['POST'])
def courses():
    data = request.get_json()
    if 'department' not in data:
        return jsonify({'error': 'Missing department field'}), 400

    department = data['department']
    count = connect.query(f"SELECT COUNT(*) FROM Courses WHERE dept = '{department}'")[0][0]
    if count == 0:
        return jsonify({'error': 'Department does not exist'}), 400

    record_count = connect.query(f"SELECT COUNT(*) FROM Courses WHERE dept = '{department}'")[0][0]
    results = connect.query(f"SELECT * FROM Courses WHERE dept = '{department}'")

    titles = connect.query("SHOW COLUMNS FROM Courses")

    dictionary = {}
    dictionary['count'] = record_count

    search_results = []

    keys = []
    for title in titles:
        keys.append(title[0])

    for i in range(0, record_count):
        values = []
        for entry in results[i]:
            values.append(entry)

        data_dict = dict(zip(keys, values))
        search_results.append(data_dict)

    dictionary['results'] = search_results

    return jsonify(dictionary), 200

@app.route('/sections', methods=['POST'])
def sections():
    data = request.get_json()
    if 'courseNum' not in data:
        return jsonify({'error': 'Missing courseNum field'}), 400
    if 'courseDept' not in data:
        return jsonify({'error': 'Missing courseDept field'}), 400

    courseNum = data['courseNum']
    courseDept = data['courseDept']
    count = connect.query(f"SELECT COUNT(*) FROM Courses WHERE courseNum = '{courseNum}' AND dept = '{courseDept}'")[0][0]
    if count == 0:
        return jsonify({'error': 'Course does not exist'}), 400

    record_count = connect.query(f"SELECT COUNT(*) FROM Sections WHERE courseNum = '{courseNum}' AND courseDept = '{courseDept}'")[0][0]
    results = connect.query(f"SELECT * FROM Sections WHERE courseNum = '{courseNum}' AND courseDept = '{courseDept}'")

    titles = connect.query("SHOW COLUMNS FROM Sections")

    dictionary = {}
    dictionary['count'] = record_count

    search_results = []

    keys = []
    for title in titles:
        keys.append(title[0])

    for i in range(0, record_count):
        values = []
        for entry in results[i]:
            values.append(entry)

        data_dict = dict(zip(keys, values))
        search_results.append(data_dict)

    dictionary['results'] = search_results

    return jsonify(dictionary), 200


@app.route('/sectioninfo', methods=['POST'])
def sectioninfo():
    data = request.get_json()
    if 'courseNum' not in data:
        return jsonify({'error': 'Missing courseNum field'}), 400
    if 'courseDept' not in data:
        return jsonify({'error': 'Missing courseDept field'}), 400
    if 'sectionNum' not in data:
        return jsonify({'error': 'Missing sectionNum field'}), 400

    courseNum = data['courseNum']
    courseDept = data['courseDept']
    sectionNum = data['sectionNum']
    term = "2023W2"
    count = connect.query(f"SELECT COUNT(*) FROM Courses WHERE courseNum = '{courseNum}' AND dept = '{courseDept}'")[0][0]
    if count == 0:
        return jsonify({'error': 'Course does not exist'}), 400


    sql_query = sql_query = f"""
SELECT
    Teaches.profName,
    Teaches.profDept,
    Sections.term,
    Sections.section,
    Sections.daysOfWeek,
    Sections.startTime,
    Sections.endTime,
    Sections.courseNum,
    Sections.courseDept
FROM
    Teaches
INNER JOIN
    Sections ON Teaches.term = Sections.term
              AND Teaches.section = Sections.section
              AND Teaches.courseNum = Sections.courseNum
              AND Teaches.courseDept = Sections.courseDept
"""

    results = connect.query(sql_query)
    # section_results = connect.query(f"SELECT * FROM Sections WHERE courseNum = '{courseNum}'"
    #                              f" AND courseDept = '{courseDept}'"
    #                              f" AND section = '{sectionNum}'"
    #                              f" AND term = '{term}'")
    #
    # teaches_results = connect.query(f"SELECT * FROM Teaches WHERE courseNum = '{courseNum}'"
    #                              f" AND courseDept = '{courseDept}'"
    #                              f" AND section = '{sectionNum}'"
    #                              f" AND term = '{term}'")

    section_titles = connect.query("SHOW COLUMNS FROM Sections")
    prof_titles = connect.query("SHOW COLUMNS FROM Professors")

    data_dict = {}

    keys = []
    for i in range(0, len(prof_titles)-3):
        title = prof_titles[i]
        keys.append(title[0])
    for title in section_titles:
         keys.append(title[0])

    values = []
    for entry in results[0]:
         values.append(entry)

    data_dict = dict(zip(keys, values))

    return jsonify(data_dict), 200


if __name__ == '__main__':
    app.run(debug=True, port=5001)