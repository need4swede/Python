PURPOSE:
* This tool was designed to automate the documentation formatting necessary to single out students who have 'Never logged in' and place them all into a seperate organizational unit for the purpose of bulk edits

FUNCTION:
* The application takes an export of Google users as input and automatically formats it and inserts appropriate student information.
* Headers are organized such to match Google's template, Advanced Protection Program enrollment is disabled for all students.
* Students with log-in activity are excluded from the final survey, and the end user is prompted to provide a destination org unit, alongside a password. If left blank, the destination org unit defaults to '/The Bucket'.
* Verification checks are conducted to ensure the data is formulated accurately and that it meets the necessary standard for Google Admin for upload
