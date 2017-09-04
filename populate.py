# populate.py

from app.models import *

# list of courses in EIE department
cous = [
    Course(101, "F17", 'Physics A'),
    Course(111, "F17", 'Applied Mathematics A'),
    Course(121, "F17", 'Pure Mathematics A'),
    Course(131, "F17", 'Computer Science I'),
    Course(141, "F17", 'Communication Skills'),
    Course(151, "F17", 'Elements Of Philosophy'),
    Course(161, "F17", 'Mechanical Workshop Technology'),
    Course(102, "F17", 'Physics B'),
    Course(112, "F17", 'Applied Mathematics B'),
    Course(122, "F17", 'Pure Mathematics B'),
    Course(132, "F17", 'Computer Science II'),
    Course(142, "F17", 'Electrical Measurements'),
    Course(152, "F17", 'The Development Process'),
    Course(162, "F17", 'Electrical Workshop Technology'),
    Course(201, "F17", 'Physical Electronics A'),
    Course(221, "F17", 'Electric Circuit Theory I  A'),
    Course(231, "F17", 'Computer Science III'),
    Course(241, "F17", 'Engineering Drawing A'),
    Course(251, "F17", 'Thermodynamics For Electrical Engineers'),
    Course(261, "F17", 'Mechanics Of Machines And Strengths Of Materials A'),
    Course(271, "F17", 'Mathematics II A'),
    Course(281, "F17", 'Laboratory II A'),
    Course(202, "F17", 'Physical Electronic B'),
    Course(222, "F17", 'Electric Circuit Theory I B'),
    Course(232, "F17", 'Computer Science IV'),
    Course(242, "F17", 'Engineering Drawing B'),
    Course(252, "F17", 'Fluid Mechanics For Electrical Engineers'),
    Course(262, "F17", 'Mechanics Of Machines And Strengths Of Materials B'),
    Course(272, "F17", 'Mathematics II B'),
    Course(282, "F17", 'Laboratory II B'),
    Course(301, "F17", 'Analogue Electronic A'),
    Course(321, "F17", 'Electrical Circuit Theory II A'),
    Course(331, "F17", 'Digital Electronics A'),
    Course(341, "F17", 'Electrical Machines I A'),
    Course(351, "F17", 'Electromagnetic Fields A'),
    Course(371, "F17", 'Mathematics III A'),
    Course(381, "F17", 'Laboratory III A'),
    Course(302, "F17", 'Analogue Electronics B'),
    Course(322, "F17", 'Electrical Circuit Theory II B'),
    Course(332, "F17", 'Digital Electronics B'),
    Course(342, "F17", 'Electrical Machines I B'),
    Course(352, "F17", 'Electromagnetic Fields B'),
    Course(362, "F17", 'Instrumentation'),
    Course(372, "F17", 'Mathematics III B'),
    Course(382, "F17", 'Laboratory III B'),
    Course(401, "F17", 'Electronics A'),
    Course(411, "F17", 'Control Systems A'),
    Course(421, "F17", 'Telecommunications And Electroacoustics A'),
    Course(431, "F17", 'Electrical Power Systems I A'),
    Course(441, "F17", 'Electrical Machines II A'),
    Course(451, "F17", 'Electrodynamics And Insulating Materials A'),
    Course(471, "F17", 'Statistics'),
    Course(481, "F17", 'Laboratory IV A'),
    Course(402, "F17", 'Electronics B'),
    Course(412, "F17", 'Control System B'),
    Course(422, "F17", 'Telecommunications And Electroacoustics B'),
    Course(432, "F17", 'Electrical Power Systems I B'),
    Course(442, "F17", 'Electrical Machines Iib'),
    Course(452, "F17", 'Electrodynamics And Insulating Materials B'),
    Course(472, "F17", 'Numerical Methods'),
    Course(482, "F17", 'Laboratory IV B'),
    Course(501, "F17", 'Applied Electronics A'),
    Course(511, "F17", 'Control Engineering A'),
    Course(521, "F17", 'Telecommunications A'),
    Course(531, "F17", 'Electrical Power Systems II A'),
    Course(541, "F17", 'Power Electronics & Variable Machine Drives A'),
    Course(551, "F17", 'Microwaves And Antennas A'),
    Course(560, "F17", 'Engineering Project'),
    Course(571, "F17", 'Mathematical Methods'),
    Course(591, "F17", 'Laboratory V A'),
    Course(502, "F17", 'Applied Electronics B'),
    Course(512, "F17", 'Control Engineering B'),
    Course(522, "F17", 'Telecommunications B'),
    Course(532, "F17", 'Electrical Power Systems II B'),
    Course(542, "F17", 'Power Electronics & Variable Machine Drives B'),
    Course(552, "F17", 'Microwaves And Antennas B'),
    Course(582, "F17", 'Management For Engineers'),
    Course(592, "F17", 'Laboratory V B')]

# days of the week
dayz = [
    DaysOfTheWeek(1, 'Sunday'),
    DaysOfTheWeek(2, 'Monday'),
    DaysOfTheWeek(3, 'Tuesday'),
    DaysOfTheWeek(4, 'Wednesday'),
    DaysOfTheWeek(5, 'Thursday'),
    DaysOfTheWeek(6, 'Friday'),
    DaysOfTheWeek(7, 'Saturday')
]


# dictionary of courses offered and their course codes
courses = {
    '': "None",
    'F17': "B.sc. (Electrical And Electronic Engineering)",
    'F16': "B.sc. (Civil Engineering)",
    'F18': "B.sc. (Mechanical Engineering)",
    'F19': "B.sc. (Geospatial Engineering)",
    'F21': "B.sc. (Environmental and Biosystems Engineering)",
    'B04': "Bachelor of Real Estate",
    'B66': "Bachelor Of Quantity Surveying",
    'B76': "Bachelor Of Construction Management",
    'B65': "B.A. (Urban & Regional Planning)"
}

# dictionary of various staff roles in a department
staff_roles = {
    0: "None",
    1: 'Chairman',
    2: 'Professor',
    3: 'Associate Professor',
    4: 'Graduate Assistant',
    5: 'Lab Technician'
}

# dictionary for years
year_of_study = {
    0: "None",
    1: 'I',
    2: 'II',
    3: 'III',
    4: 'IV',
    5: 'V',
    6: 'VI',
}

verification = {1: {"description": "Verified", "error_message": "Successful recognition"},
                2: {"description": "Missing Face", "error_message": "No face detected"},
                3: {"description": "Multiple Faces", "error_message": "Multiple faces detected"},
                4: {"description": "Unidentified Face", "error_message": "Unidentified face detected"},
                5: {"description": "Other", "error_message": "Other error detected"},
                }


def dict_to_tuple(courses_dict):
    """
    Function that converts a dict to a list of tuple containing each key and its corresponding value
    :param courses_dict: Dictionary to be converted
    :return: List of tuples
    """
    list_ = []
    for course in courses_dict:
        list_.append((course, courses_dict.get(course)))
    return list_
