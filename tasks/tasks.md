# Current Sprint Tasks

## PATIENT-01: Implement User Authentication - User Creation
Status: In Progress
Priority: High
Dependencies: None

### Requirements
- Create a form for doctor to register/login, based on url
- Email/password authentication
- JWT token generation
- Password hashing with bcrypt

### Acceptance Criteria
1. Users can register with email/password
2. Users receive JWT on successful login
3. Passwords are securely hashed
4. UI Form with good looking and separate looking from doctor login, with a header for user to know what type of login they using.


## DOCTOR-01: Implement User Authentication - User Creation
Status: In Progress
Priority: High
Dependencies: None

### Requirements
- Create a form for doctor to register/login, based on url
- Email/password authentication
- JWT token generation
- Password hashing with bcrypt

### Acceptance Criteria
1. Users can register with email/password
2. Users receive JWT on successful login
3. Passwords are securely hashed
4. UI Form with good looking and separate looking from patient login, with a header for user to know what type of login they using.

## APPOINTMENT-01: Appointment logic
Status: In Progress
Priority: High
Dependencies: None
### Requirements
The appoinment flow is like this:
1. The doctor create an appointment, select time. The time of the appointment will be
morning 8:00 -> 9:30, 10:00 -> 11:30
afternoon 1:30 -> 3:00, 3:30 -> 5:00
So there is only 4 appointment pear days
2. The patient then select the appointment of the doctor they want
3. The appointment then will be updated with the above



## DOCTOR-02: Implement Doctor schedule calendar
Status: In Progress
Priority: High
Dependencies: None

### Requirements
- When login, doctor can go to dashboard to setup avaiable calendar for patient to set appoinments
- Doctor default calendar is always avaiable on every afternoon from monday to friday
- Doctor can create a new appointment
- Doctor can delete appoinment
- Doctor can view detail appoinment

### Acceptance Criteria
1. Doctor can see the appoinments
2. Doctor can create/delete appointment

## PATIENT-02: Implement Patient assign to appointment
Status: In Progress
Priority: High
Dependencies: None

### Requirements
- When login, patient can go to dashboard to select avaible apointment from calendar, this will make filter base on doctor
- patient when click on appointment can see the detail of the doctor, and information of that appointment
- patient can cancle a appointment
- patient UI must containt: a calendar with all avaible appontment, a list of current appointments

### Acceptance Criteria
1. patient can see the appoinments
2. patient can cancel appointment

## SELFTEST-01: Implement Patient health test by themself
Status: In Progress
Priority: High
Dependencies: None

### Requirements
- When login, patient can go to dashboard to select self test
- Patient need to enter all symptoms they currently facing
- The system then return the possible diseases, with what to do in that case

### Acceptance Criteria 
1. Patient can select from a list of symptoms (30+ symptoms available)
2. Patient see possible diseases with AI-powered confidence scoring
3. The symptoms and deases knowledge base need to split to .json file
4. Add automation test, adding preknow symptoms and get a correct return of diseases

### Implementation Details
- **AI Engine**: Advanced symptom analysis with disease prediction
- **Symptom Database**: 30+ comprehensive symptoms 
- **Disease Knowledge**: multiple (at leasts 30) common conditions with treatment recommendations
- **Risk Assessment**: 4-tier risk system (low/medium/high/urgent)
- **Interface**: 
    - Quick test option
    - The symptoms have a search box, when enter the text, it filter by the text, this search must not reload the page
    - When check a symptoms, it show as a list in the between symptoms check list and the submit button.
- **Dashboard**: Patient health analytics and test history
- **Responsive UI**: Bootstrap-styled mobile-friendly interface

## PATIENT-03: Implement Patient profile
Status: ✅ COMPLETED
Priority: High
Dependencies: None

### Requirements
- When login, patient can go to dashboard then select profile to modify information

### Acceptance Criteria 
1. Patient can modify information ✅ COMPLETED 

# DOCTOR-03: Implement doctor profile
Status: ✅ COMPLETED
Priority: High
Dependencies: None

### Requirements
- When login, doctor can go to dashboard then select profile to modify information

### Acceptance Criteria 
1. Doctor can modify information like (name, dob, etc), the key information can't change like license id, etc ✅ COMPLETED

## APPOINTMENT-02: Implement APPOINTMENT ai chatbot
Status: ✅ COMPLETED
Priority: High
Dependencies: None

### Requirements
- When login, patient can go to appointment, there will be a box for chatbot, here it will recommend the best doctor based on user diease, user can type the diese and other criteria

### Acceptance Criteria 
1. The doctor with Specialization will be recommened to user ✅ COMPLETED

## APPOINTMENT-03: Implement APPOINTMENT ai chatbot
Status: ✅ COMPLETED
Priority: High
Dependencies: None

### Requirements
- When login, patient can go to appointment, there will be a box for chatbot, here it will recommend the best doctor based on user diease, user can type the diese and other criteria


### Acceptance Criteria 
1. The doctor with Specialization will be recommened to user ✅ COMPLETED
2. The link to the doctor with corresponding specialization (or related specialization) will be send in the chat ✅ COMPLETED