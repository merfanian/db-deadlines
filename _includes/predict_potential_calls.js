// Function to guess the target year's conference link
function guessConferenceLink(baseLink, targetYear) {
  if (!baseLink || baseLink === '#') {
    return null;
  }
  
  // Try common patterns to replace year in URL
  var patterns = [
    // Pattern: /2024/ -> /2025/
    { regex: /\/(\d{4})\//g, replace: '/' + targetYear + '/' },
    // Pattern: /2024 -> /2025
    { regex: /\/(\d{4})(?:\/|$)/g, replace: '/' + targetYear + '/' },
    // Pattern: -2024 -> -2025
    { regex: /-(\d{4})(?:\/|$)/g, replace: '-' + targetYear + '/' },
    // Pattern: 2024 -> 2025 (at end of domain or path)
    { regex: /(\d{4})(?:\/|$)/g, replace: targetYear + '/' },
  ];
  
  var guessedLink = baseLink;
  for (var i = 0; i < patterns.length; i++) {
    var pattern = patterns[i];
    if (pattern.regex.test(baseLink)) {
      guessedLink = baseLink.replace(pattern.regex, function(match, year) {
        return match.replace(year, targetYear);
      });
      // If we successfully replaced a year, return it
      if (guessedLink !== baseLink && guessedLink.indexOf(targetYear) !== -1) {
        return guessedLink;
      }
    }
  }
  
  // If no pattern matched, try appending year to common paths
  var commonPaths = ['/' + targetYear, '/' + targetYear + '/', '/conferences/' + targetYear];
  for (var j = 0; j < commonPaths.length; j++) {
    var testLink = baseLink.replace(/\/$/, '') + commonPaths[j];
    if (testLink !== baseLink) {
      return testLink;
    }
  }
  
  return null;
}

// Function to fetch and extract deadline from a conference website
function fetchConferenceDeadline(url, targetYear) {
  // This will be called asynchronously, so we return a promise
  return new Promise(function(resolve, reject) {
    // Use a CORS proxy if needed, or try direct fetch
    var fetchUrl = url;
    
    // Try to use a CORS proxy if direct fetch fails
    // For now, we'll try direct fetch first
    fetch(fetchUrl, {
      method: 'GET',
      mode: 'cors',
      headers: {
        'Accept': 'text/html'
      }
    })
    .then(function(response) {
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      return response.text();
    })
    .then(function(html) {
      // Parse HTML to extract deadline
      var parser = new DOMParser();
      var doc = parser.parseFromString(html, 'text/html');
      var text = doc.body ? doc.body.innerText : html;
      var textLower = text.toLowerCase();
      
      var deadline = null;
      var abstractDeadline = null;
      
      // Look for "Important Dates" section
      var importantSection = null;
      var headings = doc.querySelectorAll('h1, h2, h3, h4, h5, h6, strong, b');
      for (var i = 0; i < headings.length; i++) {
        var headingText = headings[i].textContent.toLowerCase();
        if (headingText.indexOf('important') !== -1 && headingText.indexOf('date') !== -1) {
          // Get content after heading
          var section = headings[i].nextElementSibling;
          if (section) {
            importantSection = section.textContent;
          } else {
            // Try parent's next sibling
            var parent = headings[i].parentElement;
            if (parent && parent.nextElementSibling) {
              importantSection = parent.nextElementSibling.textContent;
            }
          }
          break;
        }
      }
      
      var searchText = importantSection ? importantSection.toLowerCase() : textLower;
      
      // Extract deadline patterns (written and numeric dates)
      var monthNames = {
        'january': '01', 'february': '02', 'march': '03', 'april': '04',
        'may': '05', 'june': '06', 'july': '07', 'august': '08',
        'september': '09', 'october': '10', 'november': '11', 'december': '12',
        'jan': '01', 'feb': '02', 'mar': '03', 'apr': '04',
        'may': '05', 'jun': '06', 'jul': '07', 'aug': '08',
        'sep': '09', 'oct': '10', 'nov': '11', 'dec': '12'
      };
      
      var deadlinePatterns = [
        // Written: "deadline: January 12th, 2025"
        /(?:paper\s+)?(?:submission\s+)?deadline[:\s]+(\w+)\s+(\d{1,2})(?:st|nd|rd|th)?,?\s+(\d{4})/i,
        // Numeric: "deadline: 01/12/2025"
        /(?:paper\s+)?(?:submission\s+)?deadline[:\s]+(\d{1,2})[\/-](\d{1,2})[\/-](\d{2,4})/i,
      ];
      
      for (var j = 0; j < deadlinePatterns.length; j++) {
        var match = searchText.match(deadlinePatterns[j]);
        if (match) {
          var month, day, year;
          if (match[1].match(/^\d+$/)) {
            // Numeric format
            month = match[1];
            day = match[2];
            year = match[3];
          } else {
            // Written format
            month = monthNames[match[1].toLowerCase()] || match[1];
            day = match[2];
            year = match[3];
          }
          
          if (year.length === 2) {
            year = '20' + year;
          }
          
          // Only accept dates in the future and for the target year or next
          var deadlineDate = new Date(parseInt(year), parseInt(month) - 1, parseInt(day));
          var now = new Date();
          if (deadlineDate > now && (parseInt(year) === targetYear || parseInt(year) === targetYear + 1)) {
            deadline = year + '-' + ('0' + month).slice(-2) + '-' + ('0' + day).slice(-2) + ' 23:59:59';
            break;
          }
        }
      }
      
      resolve({
        deadline: deadline,
        abstractDeadline: abstractDeadline,
        link: url
      });
    })
    .catch(function(error) {
      // If fetch fails, return null (prediction will use historical pattern)
      resolve({
        deadline: null,
        abstractDeadline: null,
        link: url,
        error: error.message
      });
    });
  });
}

// Function to predict potential call for papers based on historical data
function predictPotentialCalls(allConferences) {
  var predictions = [];
  var conferenceGroups = {};
  var currentYear = new Date().getFullYear();
  var currentDate = new Date();
  
  // Group conferences by title
  for (var i = 0; i < allConferences.length; i++) {
    var conf = allConferences[i];
    var title = conf.title;
    
    // Skip entries that are clearly not the main conference (e.g., tracks)
    if (title.indexOf('[') !== -1 && title.indexOf('Track') !== -1) {
      continue;
    }
    
    if (!conferenceGroups[title]) {
      conferenceGroups[title] = [];
    }
    conferenceGroups[title].push(conf);
  }
  
  // For each conference group, find the latest entry and predict next deadline
  for (var title in conferenceGroups) {
    var entries = conferenceGroups[title];
    
    // Sort by year descending
    entries.sort(function(a, b) {
      return (b.year || 0) - (a.year || 0);
    });
    
    var latestEntry = entries[0];
    var latestYear = latestEntry.year || 0;
    
    // Only predict if the latest entry is from a past year or current year
    // and we don't already have an entry for next year
    var hasNextYearEntry = false;
    for (var j = 0; j < entries.length; j++) {
      if (entries[j].year > latestYear) {
        hasNextYearEntry = true;
        break;
      }
    }
    
    // Skip if we already have a future entry
    if (hasNextYearEntry) {
      continue;
    }
    
    // Skip if latest entry is too far in the future (more than 2 years)
    if (latestYear > currentYear + 1) {
      continue;
    }
    
    // Analyze historical deadlines to find pattern
    var deadlinePatterns = [];
    for (var k = 0; k < Math.min(entries.length, 5); k++) {
      var entry = entries[k];
      if (entry.deadline && entry.deadline !== 'TBA') {
        try {
          // Parse date with timezone if available
          var timezone = entry.timezone || 'America/New_York';
          var deadlineDate = moment.tz(entry.deadline, timezone);
          if (deadlineDate.isValid()) {
            deadlinePatterns.push({
              year: entry.year,
              month: deadlineDate.month(), // 0-11
              day: deadlineDate.date(),
              date: deadlineDate.toDate()
            });
          }
        } catch (e) {
          // Skip invalid dates
        }
      }
    }
    
    if (deadlinePatterns.length < 2) {
      continue; // Need at least 2 historical deadlines to make a prediction
    }
    
    // Predict next deadline based on most recent pattern
    // Use the most recent deadline and add 1 year, adjusting for typical patterns
    var mostRecentPattern = deadlinePatterns[0];
    var predictedYear = latestYear + 1;
    
    // Calculate average day of month if we have multiple years
    var avgDay = 0;
    var avgMonth = 0;
    for (var m = 0; m < deadlinePatterns.length; m++) {
      avgDay += deadlinePatterns[m].day;
      avgMonth += deadlinePatterns[m].month;
    }
    avgDay = Math.round(avgDay / deadlinePatterns.length);
    avgMonth = Math.round(avgMonth / deadlinePatterns.length);
    
    // Use most recent month, but average day for more stability
    var predictedMonth = mostRecentPattern.month;
    var predictedDay = avgDay;
    
    // Create predicted deadline date using moment with timezone
    var timezone = latestEntry.timezone || 'America/New_York';
    // Format: YYYY-MM-DD HH:mm:ss, moment month is 0-indexed so add 1 for display
    var monthStr = ('0' + (predictedMonth + 1)).slice(-2);
    var dayStr = ('0' + predictedDay).slice(-2);
    var dateString = predictedYear + '-' + monthStr + '-' + dayStr + ' 23:59:59';
    var predictedDeadline = moment.tz(dateString, timezone);
    
    // Only show predictions that are in the future (at least 30 days ahead)
    var daysUntilPrediction = predictedDeadline.diff(moment(), 'days');
    if (daysUntilPrediction < 30) {
      // If prediction is too soon, try next year
      predictedYear = latestYear + 2;
      var monthStr2 = ('0' + (predictedMonth + 1)).slice(-2);
      var dayStr2 = ('0' + predictedDay).slice(-2);
      var dateString2 = predictedYear + '-' + monthStr2 + '-' + dayStr2 + ' 23:59:59';
      predictedDeadline = moment.tz(dateString2, timezone);
      daysUntilPrediction = predictedDeadline.diff(moment(), 'days');
    }
    
    // Only show predictions that are within the next 2 years
    if (daysUntilPrediction > 0 && daysUntilPrediction < 730) {
      // Try to guess the target year's link
      var targetLink = latestEntry.link || '#';
      var guessedLink = guessConferenceLink(latestEntry.link, predictedYear);
      
      // If we guessed a different link, use it
      if (guessedLink && guessedLink !== latestEntry.link) {
        targetLink = guessedLink;
      }
      
      predictions.push({
        title: title,
        full_name: latestEntry.full_name || title,
        predictedYear: predictedYear,
        predictedDeadline: predictedDeadline,
        predictedDeadlineString: predictedDeadline.format('YYYY-MM-DD HH:mm:ss'),
        daysUntil: daysUntilPrediction,
        latestEntry: latestEntry,
        sub: latestEntry.sub || ['ML'],
        link: targetLink,
        guessedLink: guessedLink,
        timezone: timezone,
        hindex: latestEntry.hindex || 0,
        needsVerification: true  // Flag to verify deadline from website
      });
    }
  }
  
  // Sort by predicted deadline (soonest first)
  predictions.sort(function(a, b) {
    return a.predictedDeadline.diff(b.predictedDeadline);
  });
  
  return predictions;
}

// Function to render potential calls section
function renderPotentialCalls(predictions) {
  if (predictions.length === 0) {
    return;
  }
  
  var html = '<div id="potential_calls">';
  html += '<h1 id="potential-calls-title">Potential Call for Papers</h1>';
  html += '<div class="meta col-12" style="margin-bottom: 15px;">';
  html += 'These are predicted deadlines based on historical patterns. Actual deadlines may vary.';
  html += '</div>';
  
  for (var i = 0; i < predictions.length; i++) {
    var pred = predictions[i];
    var confId = 'potential-' + pred.title.toLowerCase().replace(/[^a-z0-9]/g, '') + '-' + pred.predictedYear;
    var subs = Array.isArray(pred.sub) ? pred.sub : [pred.sub];
    
    html += '<div id="' + confId + '" class="ConfItem potential-call';
    for (var j = 0; j < subs.length; j++) {
      html += ' ' + subs[j] + '-conf';
    }
    html += '">';
    
    html += '<div class="row conf-row">';
    html += '<div class="col-6">';
    html += '<span class="conf-title">';
    html += '<a title="' + (pred.full_name || 'Predicted Deadline') + ' Details" href="' + pred.link + '" target="_blank">';
    var label = pred.verified ? '(Verified)' : '(Predicted)';
    var labelColor = pred.verified ? '#4CAF50' : '#888';
    html += pred.title + ' ' + pred.predictedYear + ' <span style="font-size: 0.7em; color: ' + labelColor + ';">' + label + '</span>';
    html += '</a>';
    html += '</span>';
    html += '<span class="conf-title-small">';
    html += '<a title="' + (pred.full_name || 'Predicted Deadline') + ' Details" href="' + pred.link + '" target="_blank">';
    var labelSmall = pred.verified ? '(Ver)' : '(Pred)';
    var labelColorSmall = pred.verified ? '#4CAF50' : '#888';
    html += pred.title + " '" + String(pred.predictedYear).slice(-2) + ' <span style="font-size: 0.7em; color: ' + labelColorSmall + ';">' + labelSmall + '</span>';
    html += '</a>';
    html += '</span>';
    html += '<span class="conf-title-icon">';
    html += '<a title="Conference Website" href="' + pred.link + '" target="_blank">';
    html += '<img src="{{site.baseurl}}/static/img/203-earth.svg" class="badge-link" alt="Link to Conference Website" />';
    html += '</a>';
    html += '</span>';
    html += '</div>';
    html += '<div class="col-6">';
    html += '<span class="timer"></span>';
    html += '<span class="timer-small"></span>';
    html += '</div>';
    html += '</div>';
    
    html += '<div class="row">';
    html += '<div class="col-12 col-sm-6">';
    html += '<div class="meta">';
    html += '<span class="conf-place">Predicted based on historical patterns.</span>';
    html += '</div>';
    html += '</div>';
    html += '<div class="col-12 col-sm-6">';
    html += '<div class="deadline">';
    html += '<div>Predicted Deadline: <span class="deadline-time"></span></div>';
    html += '</div>';
    html += '<div class="calendar"></div>';
    html += '</div>';
    html += '</div>';
    
    html += '<div class="row">';
    html += '<div class="col-12">';
    for (var k = 0; k < subs.length; k++) {
      html += '<span title="Click to only show ' + subs[k] + ' conferences" data-sub="' + subs[k] + '" class="conf-sub ' + subs[k] + '-tag"></span>';
    }
    html += '</div>';
    html += '</div>';
    html += '<hr>';
    html += '</div>';
  }
  
  html += '</div>';
  
  // Insert before past_confs
  $('#coming_confs').after(html);
  
  // Initialize countdown timers and other features for potential calls
  for (var i = 0; i < predictions.length; i++) {
    var pred = predictions[i];
    var confId = 'potential-' + pred.title.toLowerCase().replace(/[^a-z0-9]/g, '') + '-' + pred.predictedYear;
    var subs = Array.isArray(pred.sub) ? pred.sub : [pred.sub];
    
    // Set subject tags
    for (var j = 0; j < subs.length; j++) {
      $('#' + confId + ' .' + subs[j] + '-tag').html(sub2name[subs[j]].toLocaleLowerCase());
    }
    
    // Set up countdown timer
    var timezone = pred.timezone || 'America/New_York';
    var confDate = pred.predictedDeadline; // Already a moment object
    
    // Render countdown timer
    $('#' + confId + ' .timer').countdown(confDate.toDate(), function (event) {
      $(this).html(event.strftime('%D days %Hh %Mm %Ss'));
    });
    
    // Render countdown timer small
    $('#' + confId + ' .timer-small').countdown(confDate.toDate(), function (event) {
      $(this).html(event.strftime('%Dd %H:%M:%S'));
    });
    
    // Convert deadline to local timezone
    try {
      var local_timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
      var localConfDate = moment.tz(confDate, local_timezone);
      $('#' + confId + ' .deadline-time').html(localConfDate.format('MMMM D, YYYY [at] h:mm A z'));
    } catch(err) {
      $('#' + confId + ' .deadline-time').html(confDate.format('MMMM D, YYYY [at] h:mm A z'));
    }
    
    // Add calendar button
    var myCalendar = createCalendarFromObject({
      id: confId,
      title: pred.title + ' ' + pred.predictedYear + ' predicted deadline',
      date: confDate.toDate(),
      duration: 60,
    });
    document.querySelector('#' + confId + ' .calendar').appendChild(myCalendar);
    
    // Set diff attribute for sorting
    var today = moment();
    var diff = today.diff(confDate, 'days');
    $('#' + confId).attr("diff", diff);
  }
}

