var MINIMUM_ANDROID_VERSION = new Date(2019, 10, 5);
var ANDROID_LAST_UPDATE = new Date(2019, 10, 4);

var MINIMUM_IOS_VERSION = splitOSVersion("13.2");
var IOS_LAST_UPDATE = new Date(2019, 9, 29);

var MINIMUM_CHROMEOS_VERSION = splitOSVersion("78.0.3904.92");
var CHROMEOS_LAST_UPDATE = new Date(2019, 10, 6);

var ANDROID_OUTDATED_MESSAGE = "\
Hello,\n\
\n\
It appears that you have an out of date Android on your device.\n\
\n\
To update, follow the instructions here: https://support.google.com/android/answer/7680439\n\
\n\
Remember that keeping your devices up to date is important for our security.\n\
\n\
Thanks!";
var IOS_OUTDATED_MESSAGE = "\
Hello,\n\
\n\
It appears that you have an out of date iOS on your device.\n\
\n\
To update, follow the instructions here: https://support.apple.com/en-us/HT204204\n\
\n\
Remember that keeping your devices up to date is important for our security.\n\
\n\
Thanks!";
var CHROMEOS_OUTDATED_MESSAGE = "\
Hello,\n\
\n\
It appears that you have an out of date ChromeOS on your device.\n\
\n\
To update, follow the instructions here: https://support.google.com/chromebook/answer/177889\n\
\n\
Remember that keeping your devices up to date is important for our security.\n\
\n\
Thanks!";


function checkOutdatedMobileDevice(device) {
  if (device.type == "ANDROID") {
    if (device.securityPatchLevel == "0") {
      return;
    }
    var version = new Date(parseFloat(device.securityPatchLevel));
    if (version < MINIMUM_ANDROID_VERSION) {
      return {name: device.email[0], version: version, type: "Android"};
    }
  } else if (device.type == "IOS_SYNC") {
    if (device.os == "") {
      return;
    }
    var version = /iOS ([\d\.]+)/.exec(device.os);
    if (compareOSVersions(splitOSVersion(version[1]), MINIMUM_IOS_VERSION) < 0) {
      return {name: device.email[0], version: version[1], type: "iOS"};
    }
  } else {
    return {error: "Unexpected type: " + device.type};
  }
}

function getAllOutdatedMobileDevices(customerId) {
  var pageToken;
  var results = [];
  var totalDevices = 0;
  do {
    var page = AdminDirectory.Mobiledevices.list(customerId, {
      maxResults: 100,
      pageToken: pageToken
    });
    for (var i = 0; i < page.mobiledevices.length; i++) {
      totalDevices++;
      var result = checkOutdatedMobileDevice(page.mobiledevices[i]);
      if (result) {
        results.push(result);
      }
    }
    pageToken = page.nextPageToken;
  } while (pageToken)
  return {totalDevices: totalDevices, results: results};
}

function splitOSVersion(v) {
  return v.split(".").map(function(c) { return parseInt(c); });
}

function compareOSVersions(v1, v2) {
  for (var i = 0; i < Math.min(v1.length, v2.length); i++) {
    if (v1[i] < v2[i]) {
      return -1;
    } else if (v1[i] > v2[i]) {
      return 1;
    }
  }

  if (v1.length < v2.length) {
    return -1;
  } else if (v1.length > v2.length) {
    return 1;
  }

  return 0;
}

function checkOutdatedChromeOSDevice(device) {
  var version = splitOSVersion(device.osVersion);
  if (compareOSVersions(version, MINIMUM_CHROMEOS_VERSION) < 0) {
    return {name: device.annotatedUser, version: device.osVersion, type: "ChromeOS"};
  }
}

function getAllOutdatedChromeOSDevices(customerId) {
  var pageToken;
  var results = [];
  var totalDevices = 0;
  do {
    var page = AdminDirectory.Chromeosdevices.list(customerId, {
      maxResults: 200,
      pageToken: pageToken,
      query: "status:ACTIVE",
    });
    if (page.chromeosdevices === undefined) {
      // ChromeOS devices are not enabled on this account.
      break;
    }
    for (var i = 0; i < page.chromeosdevices.length; i++) {
      totalDevices++;
      var result = checkOutdatedChromeOSDevice(page.chromeosdevices[i]);
      if (result) {
        results.push(result);
      }
    }
    pageToken = page.nextPageToken;
  } while (pageToken)
  return {totalDevices: totalDevices, results: results};
}

function getCustomerId(exampleUser) {
  var userKey = AdminDirectory.Users.get(exampleUser);
  return userKey.customerId;
}

function daysSinceUpdated(description, lastUpdated) {
  var days = Math.floor((new Date() - lastUpdated) / (1000 * 60 * 60 * 24));
  return "It has been " + days + " days since " + description + " was updated.\n";
}

function buildBodyForDevices(devices, description) {
  var error = "";
  var message = "Found " + devices.totalDevices + " " + description + " devices.\n";
  if (devices.results.length > 0) {
    message += devices.results.length + " outdated " + description + " devices owned by:\n";
    for (var i = 0; i < devices.results.length; i++) {
      if (devices.results[i].error) {
        error += "- " + devices.results[i].error + "\n";
      } else {
        message += "- " + devices.results[i].name + " (" + devices.results[i].version + ")\n";
      }
    }
  } else {
    message += "No outdated " + description + " devices\n";
  }
  return {message: message, error: error};
}

function emailOutdatedUsers(devices) {
  for (var i = 0; i < devices.results.length; i++) {
    if (devices.results[i].error) {
      continue;
    }

    var message;
    switch (devices.results[i].type) {
      case "iOS":
        message = IOS_OUTDATED_MESSAGE;
        break;
      case "Android":
        message = ANDROID_OUTDATED_MESSAGE;
        break;
      case "ChromeOS":
        message = CHROMEOS_OUTDATED_MESSAGE;
        break;
    }

    MailApp.sendEmail({
      to: devices.results[i].name,
      subject: "Outdated " + devices.results[i].type,
      body: message
    });
  }
}

function main() {
  var scriptProperties = PropertiesService.getScriptProperties()

  var customerId = getCustomerId(scriptProperties.getProperty("EXAMPLE_USER"));
  var outdatedMobileDevices = getAllOutdatedMobileDevices(customerId);
  var outdatedChromeOSDevices = getAllOutdatedChromeOSDevices(customerId);
  var messageBody = "";
  var errorBody = "";

  messageBody += daysSinceUpdated("iOS", IOS_LAST_UPDATE);
  messageBody += daysSinceUpdated("Android", ANDROID_LAST_UPDATE);
  var mobileBody = buildBodyForDevices(outdatedMobileDevices, "mobile");
  messageBody += mobileBody.message;
  errorBody += mobileBody.error;
  messageBody += "\n";

  messageBody += daysSinceUpdated("ChromeOS", CHROMEOS_LAST_UPDATE);
  var chromeOSBody = buildBodyForDevices(outdatedChromeOSDevices, "ChromeOS")
  messageBody += chromeOSBody.message;
  errorBody += chromeOSBody.error;

  var recipients = JSON.parse(scriptProperties.getProperty("REPORT_RECIPIENTS"));
  MailApp.sendEmail({
    to: recipients[0],
    cc: recipients.slice(1).join(","),
    subject: "Device OS report",
    body: messageBody + errorBody
  });

  var notifyUsers = JSON.parse(scriptProperties.getProperty("NOTIFY_USERS"));
  if (notifyUsers) {
    emailOutdatedUsers(outdatedMobileDevices);
    emailOutdatedUsers(outdatedChromeOSDevices);
  }
}
