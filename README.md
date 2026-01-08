प्रकल्प आराखडा: ग्राम महसूल अधिकारी (GMA) दप्तर तपासणी प्रणाली
१. प्रकल्पाचे स्वरूप (Project Scope)
वापरकर्ते: अ‍ॅडमिन (उच्च पदस्थ अधिकारी), ग्राम महसूल अधिकारी (ग्रा.म.अ.).

उद्देश: दप्तर तपासणी प्रश्नावली तयार करणे, अधिकारी अभिप्राय नोंदवणे आणि ग्रा.म.अ. यांच्याकडून अनुपालन (Compliance) प्राप्त करणे.

प्लॅटफॉर्म: Python Flask (Backend), Bootstrap (Frontend), Google Sheets (Database).

२. तांत्रिक संरचना (Tech Stack)
Framework: Flask (Python).

Database: Google Sheets API.

Storage: Google Drive API (दस्तऐवज अपलोडसाठी).

Deployment: GitHub & Render/Heroku.

३. डेटाबेस आराखडा (Sheet Structure)
Sheet 1 (Master_Q): प्रश्नांची यादी (ID, विभाग, प्रश्न, अपलोड आवश्यक आहे का?).

Sheet 2 (Inspections): तपासणीचा मुख्य डेटा (ID, सजा, नाव, तारीख, एकूण ग्रेड).

Sheet 3 (Compliance): अनुपालन डेटा (Log_ID, अधिकारी शेरा, वरिष्ठ मत, ग्रा.म.अ. स्पष्टीकरण, फाईल लिंक, स्थिती).

४. मराठी इंटरफेस शब्दकोश (System Labels)
Status: स्थिती (पूर्तता मान्य / अमान्य / प्रलंबित).

Remarks: अधिकारी अभिप्राय.

Compliance: ग्रा.म.अ. अनुपालन अहवाल.