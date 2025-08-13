# MrSender

MrSender is a system for sending email to leads and call them soon after

## How does it work

MrSender takes information about a lead, generate a message according to a prompt and the information you have about the lead. At the same tima it creates a new contact on a MrCall phone assistant.

It then sends the message through sendgrid APIs. When the lead opens the email, MrSender is notified through a pixel download. At this point MrSender makes a call to MrCall's APIs and generate an outbound call to the lead.

## Configuration

The configuration file needs:

- OPENAI_KEY for generating the message
- SENDGRID_KEY for sending email messages
- MRCALL_USER, MRCALL_PASSWORD and MRCALL_BUSINESS_ID for making the calls
- EMAIL_PROMPT is the prompt used for generating the messages

## Data about tbe leads

The data about the lead are stored in a postgres table. Mandatory fields are:

phone_number, email_address, opt_in (true/false)

Other fields like name, company name etc are desirable and stored in a JSON field (other_info)

## Workflow details

MrSender offers a webservice (FastAPI) 

1. For each lead with opt_in == true, MrSender creates a new url which associates to this sender and allows the download of a pixel
2. Create an HTML email with subject etc, using the prompt stored in EMAIL_PROMPT. The email message alsoc contains the pixel associated to the lead with the correspondent URL
3. Send an email to each lead through sendgrid
4. When a lead opens the email, they download the pixel and MrSender knows the message has been opened
5. As soon as MrSender receives the opening notification, it calls mrcall.ai API for calling the lead
