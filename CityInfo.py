import cv2
import oracledb
from csv import writer
from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.by import By
from database_status import ShowDatabaseStatus
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import Select
from CaptchaDecode import ImageToWordModel  # Import ImageToWordModel
from mltu.configs import BaseModelConfigs
from pathlib import Path

v_process_user = 'U1'

#oracledb.init_oracle_client()
oracledb.init_oracle_client(lib_dir=r"D:\app\udaykumard\product\instantclient_23_6")
conn = oracledb.connect(user='RESULT', password='LOCALDEV', dsn='192.168.15.208:1521/orcldev')
cur = conn.cursor()

# Fetch the XPaths from the database
str_EleXpath = "SELECT NAME, PATH FROM NEET_CITYINFO_ELEMENT_XPATH_25"
cur.execute(str_EleXpath)
res_EleXpath = cur.fetchall()

# Create a dictionary for the elements and their XPaths
xpath_dict = {row[0]: row[1] for row in res_EleXpath}

#Login
def SubmitBtn():
    v_REGNO = driver.find_element(By.NAME, xpath_dict.get("Regno"))    
    v_REGNO.clear()  
    v_REGNO.send_keys(v_APPNO)

    v_Password = driver.find_element(By.NAME,xpath_dict.get("Password"))
    v_Password.clear()
    v_Password.send_keys(v_PASSWORD)
    
    Captchaimg = driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_captchaimage")
    Captchaimg.screenshot('Screenshotcaptcha.png')

    # Load model configurations
    configs = BaseModelConfigs.load("Models/02_captcha_to_text/202503051517/configs.yaml")
    model = ImageToWordModel(model_path=configs.model_path, char_list=configs.vocab)

    image = cv2.imread('Screenshotcaptcha.png')
    prediction_text = model.predict(image)

    v_Captcha = driver.find_element(By.NAME, xpath_dict.get("Captcha"))      
    v_Captcha.send_keys(prediction_text)
    
    #Button press
    Submit_button = driver.find_element(By.NAME, xpath_dict.get("SubmitBtn"))
    driver.execute_script("arguments[0].click();", Submit_button)
    
def Xpath_Elements_Data():
    o_ApplicationNumber	= driver.find_element(By.ID, xpath_dict.get("ApplicationNumber")).text 
    o_CandidateName	= driver.find_element(By.ID, xpath_dict.get("CandidateName")).text 
    o_FatherName =	driver.find_element(By.ID, xpath_dict.get("FatherName")).text 
    o_Gender =	driver.find_element(By.ID, xpath_dict.get("Gender")).text 
    o_Dob =	driver.find_element(By.ID, xpath_dict.get("Dob")).text 
    o_Category = driver.find_element(By.ID, xpath_dict.get("Category")).text 
    o_Pwd =	driver.find_element(By.ID, xpath_dict.get("Pwd")).text 
    o_ScribeRequired = driver.find_element(By.ID, xpath_dict.get("ScribeRequired")).text	
    o_Medium = driver.find_element(By.ID, xpath_dict.get("Medium")).text	
    o_DateofExamination = driver.find_element(By.ID, xpath_dict.get("DateofExamination")).text	
    o_ReportingTime	= driver.find_element(By.ID, xpath_dict.get("ReportingTime")).text	
    o_GateClosingTime = driver.find_element(By.ID, xpath_dict.get("GateClosingTime")).text	
    o_TimingofExamination = driver.find_element(By.ID, xpath_dict.get("TimingofExamination")).text	
    o_CityofExamination = driver.find_element(By.ID, xpath_dict.get("CityofExamination")).text 
    o_StateofExamination = driver.find_element(By.ID, xpath_dict.get("StateofExamination")).text	
    
    insert_stu_dtls = "INSERT INTO O_NEET_UG_CITYINFO_25 (ADMNO, APPNO, NAME, FATHERNAME, GENDER , DOB , CATEGORY, PWD, SCRIBEREQUIRED, \
    MEDIUM, DATEOFEXAMINATION, REPORTINGTIME, GATECLOSINGTIME, TIMEINGOFEXAMINATION, CITYOFEXAMINATION, STATEOFEXAMINATION, BRANCH ) \
    VALUES ('" + str(v_Admno) + "', '" + str(o_ApplicationNumber) + "', '" + str(o_CandidateName) + "', '" + str(o_FatherName) + "', '" + str(o_Gender) + "', '" + str(o_Dob) + "', \
    '" + str(o_Category) + "', '" + str(o_Pwd) + "', '" + str(o_ScribeRequired) + "', '" + str(o_Medium) + "', '" + str(o_DateofExamination) + "', '" + str(o_ReportingTime) + "', \
    '" + str(o_GateClosingTime) + "', '" + str(o_TimingofExamination) + "', '" + str(o_CityofExamination) + "', '" + str(o_StateofExamination) + "', '" + str(v_Branch) + "')"      
    cur.execute(insert_stu_dtls) # Execute an INSERT statement

    update_Status = "UPDATE I_NEET_UG_CITYINFO_25  SET PROCESS_STATUS = 'DONE', PROCESS_USER ='"+str(v_process_user)+"' WHERE APPNO = '"+ str(v_APPNO) +"'"
    cur.execute(update_Status)
    conn.commit()

driver = webdriver.Chrome()
driver.maximize_window()

#---------------Data Slots--------------------------------
str_dataslot = "SELECT PROCESS_USER, START_VAL, END_VAL FROM DATASLOTS_VAL_USER WHERE PROCESS_USER = '"+v_process_user+"'"
cur.execute(str_dataslot)
res_dataslot = cur.fetchall()

start_sno = res_dataslot[0][1]
end_sno = res_dataslot[0][2]

Sno = start_sno
#---------------------------------- End ---------------------------

str_Jeeappno = "SELECT SNO, APPNO, PASSWORD, ADMNO, BRANCH FROM I_NEET_UG_CITYINFO_25 WHERE PROCESS_STATUS = 'P' AND SNO >= '"+str(start_sno)+"' AND  SNO <='"+str(end_sno)+"' ORDER BY SNO"
cur.execute(str_Jeeappno)
res = cur.fetchall()

for row in res:
    v_APPNO = row[1]
    v_PASSWORD = row[2]
    v_Admno = row[3]
    v_Branch = row[4]
    successful_login = False 

    # Create an instance of the class
    db_status = ShowDatabaseStatus(cur)
    db_status.get_status()

    try:  
        driver.get("https://examinationservices.nic.in/NEET2025/DownloadAdmitCard/frmAuthforCityNEET.aspx?enc=Ei4cajBkK1gZSfgr53ImFcFR+natXIEjJ1rCf6DMgOr/hcv4rs34T5gNmvCx/R+a")
    
        SubmitBtn()

        i = 1
        try:
            v_Captcha = driver.find_element(By.ID, xpath_dict.get("CaptchaError")).text 
        except:
            v_Captcha = ""     

        if v_Captcha == "CAPTCHA did not match.Please enter correct CAPTCHA.":
            while i <= 100:       
                SubmitBtn()  

                try:
                    v_Captcha = driver.find_element(By.ID, xpath_dict.get("CaptchaError")).text 
                except:
                    v_Captcha = ""
                
                if v_Captcha =='Invalid Application Number or Password..':
                    update_Status = "UPDATE I_NEET_UG_CITYINFO_25  SET PROCESS_STATUS = 'INVALID', CREATEDDATE = SYSDATE, PROCESS_USER ='"+str(v_process_user)+"' WHERE APPNO = '"+ str(v_APPNO) +"'"
                    cur.execute(update_Status)
                    conn.commit()
                    login_successful = True
                    break
                elif v_Captcha in ['Examination Fee NOT paid/Incomplete Form.']:
                    update_Status = "UPDATE I_NEET_UG_CITYINFO_25  SET PROCESS_STATUS = 'NOT PAID', CREATEDDATE = SYSDATE, PROCESS_USER ='"+str(v_process_user)+"' WHERE APPNO = '"+ str(v_APPNO) +"'"
                    cur.execute(update_Status)
                    conn.commit()
                    login_successful = True
                    break
                else:
                    Xpath_Elements_Data()
                    login_successful = True
                    break

        elif v_Captcha in ['Examination Fee NOT paid/Incomplete Form.']:
            update_Status = "UPDATE I_NEET_UG_CITYINFO_25  SET PROCESS_STATUS = 'NOT PAID', CREATEDDATE = SYSDATE, PROCESS_USER ='"+str(v_process_user)+"' WHERE APPNO = '"+ str(v_APPNO) +"'"
            cur.execute(update_Status)
            conn.commit()
            login_successful = True
            
        elif v_Captcha =='Invalid Application Number or Password..':
            update_Status = "UPDATE I_NEET_UG_CITYINFO_25  SET PROCESS_STATUS = 'INVALID', CREATEDDATE = SYSDATE, PROCESS_USER ='"+str(v_process_user)+"' WHERE APPNO = '"+ str(v_APPNO) +"'"
            cur.execute(update_Status)
            conn.commit()
            login_successful = True
        else:
            Xpath_Elements_Data()
            login_successful = True

    except:
        try:
            Xpath_Elements_Data()
            login_successful = True
        except:
            update_Status = "UPDATE I_NEET_UG_CITYINFO_25  SET PROCESS_STATUS = 'NA', CREATEDDATE = SYSDATE, PROCESS_USER ='"+str(v_process_user)+"' WHERE APPNO = '"+ str(v_APPNO) +"'"
            cur.execute(update_Status)
            conn.commit()
            login_successful = True

driver.quit()