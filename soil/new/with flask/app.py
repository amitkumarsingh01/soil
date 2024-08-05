import smtplib
import xlsxwriter
import requests
from datetime import datetime
import time
import os
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders

# Email settings
smtp_server = 'smtp.gmail.com'
smtp_port = 587
sender_email = 'aksmlibts@gmail.com'
receiver_email = 'aksdsce@gmail.com'
password = 'obzbhhkluaivnziu'

# Function to send email alert
def send_email_alert(sensor_id):
    subject = f"Alert: Sensor {sensor_id} Needs Watering"
    body = f"Sensor {sensor_id} has reported a value below 40%. Please water the plant."
    message = f"Subject: {subject}\n\n{body}"

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message)

# Function to send the Excel file via email
def send_excel_file(file_path):
    subject = "Sensor Data Report"
    body = "Attached is the latest sensor data report."
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    part = MIMEBase('application', 'octet-stream')
    part.set_payload(open(file_path, 'rb').read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', f'attachment; filename="{os.path.basename(file_path)}"')
    msg.attach(part)

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, msg.as_string())

# Function to fetch data from the ESP32 (modify the URL as needed)
def fetch_sensor_data():
    response = requests.get('http://192.168.150.82/data')
    if response.status_code == 200:
        data = response.json()
        return data['sensor1'], data['sensor2'], data['sensor3'], data['average']
    else:
        return None, None, None, None

# Create an Excel workbook and worksheet
def create_excel_workbook():
    workbook = xlsxwriter.Workbook('sensor_data.xlsx')
    worksheet = workbook.add_worksheet()
    # Write the header
    worksheet.write('A1', 'Timestamp')
    worksheet.write('B1', 'Sensor 1')
    worksheet.write('C1', 'Sensor 2')
    worksheet.write('D1', 'Sensor 3')
    worksheet.write('E1', 'Average')
    return workbook, worksheet

workbook, worksheet = create_excel_workbook()
row = 1

# Fetch and log data every minute, send the Excel file every 2 minutes
start_time = time.time()
while True:
    sensor1, sensor2, sensor3, average = fetch_sensor_data()
    if sensor1 is not None:
        # Log data
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        worksheet.write(row, 0, timestamp)
        worksheet.write(row, 1, sensor1)
        worksheet.write(row, 2, sensor2)
        worksheet.write(row, 3, sensor3)
        worksheet.write(row, 4, average)
        row += 1

        # Check if any sensor value is below 40% and send an email
        if sensor1 < 40:
            send_email_alert(1)
        if sensor2 < 40:
            send_email_alert(2)
        if sensor3 < 40:
            send_email_alert(3)

    time.sleep(60)

    if time.time() - start_time >= 120:
        workbook.close()
        send_excel_file('sensor_data.xlsx')
        os.remove('sensor_data.xlsx')  # Remove the old file to avoid conflicts
        workbook, worksheet = create_excel_workbook()
        start_time = time.time()
        row = 1
