

* Configuration file with OPENAI_KEY, MRCALL_USER, MRCALL_PASSWORD and MRCALL_BUSINESS_ID, SENDGRID_KEY, all from system variable
* Input data: A CSV file with phone number, email, opt_in (true/false) and other information about a lead
* The script must digest all the "other information" and produce a short email text for proposing a business
* The script must read the CSV file and send emails to all lead with opt_in true
* All email are HTML, no pictures but a pixel to downloaded from...
* ...a webapp which receive a GET when a pixel is downloaded: this to understand when the recipient opens the email (if they are not blocking images download of course)
* When the webapp receives the call it calls MRCALL api and MrCall calls the lead
