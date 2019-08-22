# GSuite Device Update Notifier

This is a [Google Script](https://script.google.com) for a GSuite organization
which notifies you about the update state of mobile phones (iOS and Android)
and ChromeOS devices in your oganization.

This helps ensure users are patching devices!

One limitation: this is not able to report on "Company Owned Mobile Devices",
because the GSuite APIs do not provide any information on them. Once GSuite
adds support for them in their APIs, we intend to take advantage!

Note that the script contains iOS, Android, and ChromeOS versions in it, so we
will be updating it whenever these projects have new security releases, you'll
need to check back to get these updates, or update the script yourself.

## Setup

- Browse to https://script.google.com and create a project.
- Copy `main.js` into the text area.
- Open the File menu, select Project properties. Click on the
  Script properties tab. Press Add row and create one named `EXAMPLE_USER`
  with a value of any user in your organization's email address (e.g.
  `you@your-organization.com`). Press Add row again and create one named
  `REPORT_RECIPIENTS` with a value containing a JSON list of email address for
  people who should receive the report (e.g.
  `["you@your-organization.com", "someone-else@your-organization.com"]`). And
  press Save.
- Open the Resources menu, select Advanced Google Services, and enable the
  Admin Directory Service.
- Optionally, configure the script to be run on a regular schedule (e.g. daily)
