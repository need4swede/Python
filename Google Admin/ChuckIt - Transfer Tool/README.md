PURPOSE:
* This tool was designed to automate the documentation formatting necessary to single out students who have 'Never logged in' and place them all into a seperate organizational unit for the purpose of bulk edits

FUNCTION:
* The application takes an export of Google users as input and automatically formats it and inserts appropriate student information.
* Headers are organized such to match Google's template, Advanced Protection Program enrollment is disabled for all students.
* Students with log-in activity are excluded from the final survey, and the end user is prompted to provide a destination org unit, alongside a password.
* Verification checks are conducted to ensure the data is formulated accurately and that it meets the necessary standard for Google Admin for upload

FAQ:
1. What is this really useful for?

* My company had a lot of users who had never logged into their accounts that we needed to get rid of. Because Google Admin doesn't let you sort users by sign-in activity (even though it is listed as a criteria on their table), I had to figure out an alernative method. My solution was to export our users to a file and then create a tool that parses through the users that haven't signed in and put them all into one single org unit. Google Admin requires passwords for this to work, so the tool also resets their passwords. I then created an org unit that matches the unit I'm sending all of these users to, and uploaded the output file to Google. All those users then get transferred to that unit and I can now remove all of these users in bulk. We had tens of thousands of users, so this saved us a ton of time - I am hoping it can help others, too.  

2. What happens if I accidentally import the wrong file?

* The utility first checks if the file is in the correct format ('.csv'), and also checks to make sure the formatting of that file is equal to that of a user export from G-Admin. If either one of these checks fail, the program will be upset and tell you to try running it again, accompanied by an appropriate error message.

3. What if I make a mistake?

* Don't worry - all changes are done to a temporary file, and not the source file itself. Whatever file you choose as your input will be left un-altered.

4. What if I leave the destination org unit and password as blank?

* If you don't enter an org unit as your destination, it defaults it to '/The Bucket'. This is a play on the application's name, which together instantiates the phrase "ChuckIt in /The Bucket"
* If you don't enter a password, the password field will just be left blank

5. What if the utility finds a user that has never logged in, but they're not in one of the org units I asked the program to look for?

* In these cases, the user(s) will still appear in the output file, but their org units will not have changed. This is useful because it allows you to parse through all of these students, but have selective control over which one of them actually get transferred to your new org unit. 