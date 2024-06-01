import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Hospital and Doctor Information
HOSPITAL_NAME = "Ameer Muhammad Physiotherapy Clinic - Kot Chutta
DOCTOR_NAME = "Doctor's name: Dr. Taimoor Ameer"
HOSPITAL_EMAIL = "info@ameer-hospital.com"
HOSPITAL_PHONE = "+92-334-4147322"
HOSPITAL_WEBSITE = "www.ameer-hospital.com"
ADMIN_EMAIL = "admin@dr-javed-hospital.com"  # Email to notify hospital administration

# Check-up timings
START_TIME = 9
END_TIME = 21
LUNCH_START = 13
LUNCH_END = 15
APPOINTMENT_DURATION = 15  # in minutes

# File to store appointments
APPOINTMENTS_FILE = "appointments.csv"

# Load existing appointments
def load_appointments():
    try:
        return pd.read_csv(APPOINTMENTS_FILE)
    except FileNotFoundError:
        return pd.DataFrame(columns=["Date / تاریخ", "Time / ٹائم", "Name / مریض کا نام", "Age / مریض کی عمر", 
                                     "Gender / مریض کی جنس", "History / بیماری کے بارے میں تھوڑا بیان کریں", 
                                     "Contact Number / رابطہ نمبر"])

appointments_df = load_appointments()

# Save appointments to CSV
def save_appointment(date, time, name, age, gender, history, contact_number):
    global appointments_df
    new_appointment = pd.DataFrame({
        "Date / تاریخ": [date],
        "Time / ٹائم": [time],
        "Name / مریض کا نام": [name],
        "Age / مریض کی عمر": [age],
        "Gender / مریض کی جنس": [gender],
        "History / بیماری کے بارے میں تھوڑا بیان کریں": [history],
        "Contact Number / رابطہ نمبر": [contact_number],
    })
    appointments_df = pd.concat([appointments_df, new_appointment], ignore_index=True)
    appointments_df.to_csv(APPOINTMENTS_FILE, index=False)

# Send email notification
def send_email_notification(date, time, name, age, gender, history, contact_number):
    msg = MIMEMultipart()
    msg['From'] = HOSPITAL_EMAIL
    msg['To'] = ADMIN_EMAIL
    msg['Subject'] = "New Appointment Booking"
    body = f"New appointment booked:\n\nDate / تاریخ: {date}\nTime / ٹائم: {time}\nName / مریض کا نام: {name}\nAge / مریض کی عمر: {age}\nGender / مریض کی جنس: {gender}\nHistory / بیماری کے بارے میں تھوڑا بیان کریں: {history}\nContact Number / رابطہ نمبر: {contact_number}"
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(HOSPITAL_EMAIL, 'your_app_specific_password')  # Use the app-specific password here
        text = msg.as_string()
        server.sendmail(HOSPITAL_EMAIL, ADMIN_EMAIL, text)
        server.quit()
    except Exception as e:
        st.error(f"Failed to send email notification: {e}")

# Generate available time slots
def generate_time_slots():
    time_slots = []
    current_time = datetime.now().replace(hour=START_TIME, minute=0, second=0, microsecond=0)
    end_time = datetime.now().replace(hour=END_TIME, minute=0, second=0, microsecond=0)
    
    while current_time < end_time:
        if current_time.hour < LUNCH_START or current_time.hour >= LUNCH_END:
            time_slots.append(current_time.strftime("%H:%M"))
        current_time += timedelta(minutes=APPOINTMENT_DURATION)
    
    return time_slots

# Streamlit App
st.title("Appointment Booking")
st.title(HOSPITAL_NAME)
st.subheader(DOCTOR_NAME)

st.info(f"Email: {HOSPITAL_EMAIL}\nPhone: {HOSPITAL_PHONE}\nWebsite: {HOSPITAL_WEBSITE}")

# Collect patient information
st.sidebar.header("Patient Information")
patient_name = st.sidebar.text_input("Name / مریض کا نام")
patient_age = st.sidebar.number_input("Age / مریض کی عمر", min_value=0, max_value=120)
patient_gender = st.sidebar.selectbox("Gender / مریض کی جنس", ["Male", "Female", "Other"])
patient_history = st.sidebar.text_area("Medical History / بیماری کے بارے میں تھوڑا بیان کریں")
patient_contact = st.sidebar.text_input("Contact Number / رابطہ نمبر")

# Select date
selected_date = st.date_input("Select a date for the appointment / تاریخ کا انتخاب کریں", min_value=datetime.now().date())

# Generate and display available time slots
available_slots = generate_time_slots()
selected_slot = st.selectbox("Select an available time slot / وقت کا انتخاب کریں", [slot for slot in available_slots if f"{selected_date} {slot}" not in appointments_df['Time / ٹائم'].values])

if st.button("Book Appointment"):
    if patient_name and patient_age and patient_gender:
        save_appointment(selected_date, selected_slot, patient_name, patient_age, patient_gender, patient_history, patient_contact)
        send_email_notification(selected_date, selected_slot, patient_name, patient_age, patient_gender, patient_history, patient_contact)
        st.success(f"Appointment booked successfully for {selected_date} at {selected_slot}")
    else:
        st.error("Please fill in all the details.")

# Display booked appointments
if st.checkbox("Show booked appointments"):
    st.write(appointments_df)

# Add footer
st.markdown("The system developed by Qadir Materials Tech, for more services contact us: awais.qadir980@gmail.com")
