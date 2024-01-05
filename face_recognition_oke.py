import cv2
import face_recognition
import datetime
import mysql.connector
import os

# Connect to MySQL database
conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='',
    database='face_reg'
)
cursor = conn.cursor()

# Load face data from the database
cursor.execute("SELECT * FROM siswa")
rows = cursor.fetchall()

# Extract data into lists
student_ids = []
student_names = []
student_image_paths = []

for row in rows:
    student_ids.append(row[0])
    student_names.append(row[1])

known_encodings = []
known_names = student_names

# Load and encode faces from the images folder
for student_id in student_ids:
    # Construct the path to the image file
    image_path = f"images/{student_id}.jpg"

    if not os.path.isfile(image_path):
        print(f"Warning: Image file not found for student with ID {student_id}. Please capture the photo.")
        continue


    # Read image from path
    img = cv2.imread(image_path)
    # Convert image from BGR to RGB (as face_recognition expects RGB format)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    # Find face locations and encodings
    face_locations = face_recognition.face_locations(img_rgb)
    #face_locations = face_recognition.face_locations(image_path, number_of_times_to_upsample=0, model="cnn")
    face_encoding = face_recognition.face_encodings(img_rgb, face_locations)[0]
    known_encodings.append(face_encoding)

font = cv2.FONT_HERSHEY_COMPLEX

cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

# Get today's date
today_date = datetime.date.today()
current_time = datetime.datetime.now().time()


# declare valible attendance_recorded and set default False
attendance_recorded = False

start_time = datetime.time(1, 0)
end_time = datetime.time(23, 30)

while True:
    success, img_original = cap.read()

    if start_time <= current_time <= end_time:

        # Find faces in the frame
        face_locations = face_recognition.face_locations(img_original)
        face_encodings = face_recognition.face_encodings(img_original, face_locations)

        for face_location, face_encoding in zip(face_locations, face_encodings):
            # Compare the current face with known faces
            matches = face_recognition.compare_faces(known_encodings, face_encoding)
            name = "Tidak dikenal"
            message = f"{name}"

            if True in matches:
                first_match_index = matches.index(True)
                name = known_names[first_match_index]
                student_id = student_ids[first_match_index]

                # Check if attendance has been recorded for today
                if not attendance_recorded:
                    cursor.execute("SELECT * FROM absen WHERE tanggal=%s AND nis=%s", (today_date, student_id))
                    existing_record = cursor.fetchone()

                    if existing_record:
                        message = f"{name} - Sudah Absen"
                        attendance_recorded = True
                    else:
                        # Record attendance in the database
                        cursor.execute("INSERT INTO absen (tanggal, jam, nis) VALUES (%s, %s, %s)", (today_date, current_time, student_id))
                        conn.commit()
                        message = f"{name} - Absen Berhasil"
                        attendance_recorded = True

                else:
                    message = f"{name} - Sudah Absen"

            # Draw rectangle and display name
            y1, x2, y2, x1 = face_location
            cv2.rectangle(img_original, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(img_original, message, (x1, y2 + 20), font, 0.75, (0, 255, 0), 1, cv2.LINE_AA)
    else:
        # Display a message that attendance is not allowed at the current time
        cv2.putText(img_original, "Diluar waktu absensi", (50, 50), font, 1, (0, 0, 255), 2, cv2.LINE_AA)

    cv2.imshow("Result", img_original)

    k = cv2.waitKey(1)
    if k == ord('q'):
        break

# Release the camera and close the database connection
cap.release()
cv2.destroyAllWindows()
conn.close()