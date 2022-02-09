This module contains various data sets that can be accessed
by brute force modules.

- [ua\_strings.txt](https://github.com/tamimibrahim17/List-of-user-agents) - 4,712 user agent strings; sorted.
- [msol\_codes.py](https://docs.microsoft.com/en-us/azure/active-directory/develop/reference-aadsts-error-codes) - MSOL error codes.

# MSOL Error Code Notes

Source: https://docs.microsoft.com/en-us/azure/active-directory/develop/reference-aadsts-error-codes

## JavaScript Harvest Snippet

Used the following JavaScript Snippet to extract the codes as JSON

```javascript
table = document.getElementsByTagName("table")[3]
rows = table.getElementsByTagName("tr")
d={}
for(ind=0;ind<rows.length;ind++){
      cells=rows[ind].getElementsByTagName("td")
        d[cells[0].textContent]=cells[1].textContent
        }
console.log(JSON.stringify(d))
```

## Valid Credential Codes

 - `AADSTS50014` - user account is not fully created yet
 - `AADSTS50055` - expired password
 - `AADSTS50057` - disabled account
 - `AADSTS50072` - user needs to enroll for second factor authentication
 - `AADSTS50074` - strong authentication required
 - `AADSTS50076` - mfa required
 - `AADSTS50079` - mfa required
 - `AADSTS50129` - device is not workplace joined
 - `AADSTS50131` - POTENTIALLY VALID - conditional access error
 - `AADSTS50144` - expired password
 - `AADSTS53000` - conditional access policy requires a domain joined device and the device is not complient
 - `AADSTS53001` - ^ except the device is not domain joined
 - `AADSTS53004` - user needs to complete mfa registration
 - `AADSTS80012` - logon at invalid hours
 - `AADSTS90072` - mfa error...see documentation
 - `AADSTS90094` - AdminConsentRequired
 - `AADSTS50158` - conditional access controls present

## Valid User Codes

 - `AADSTS50126` - Error validating credentials due to invalid username/password. 
 - `AADSTS50056` - Invalid/null password configured for user; the password does not exist
                   in the store for this user.
 - `AADSTS50053` - smart lock

## Fatal Codes

 - `AADSTS20001`
 - `AADSTS20012`
 - `AADSTS20033`
 - `AADSTS40008`
 - `AADSTS40009`
 - `AADSTS40010`
 - `AADSTS40015`
 - `AADSTS700016`  - UnauthorizedClient - Application wasn't found in directory/tenant.
 - `AADSTS50000`
 - `AADSTS50005`
 - `AADSTS50008`
 - `AADSTS50020`
 - `AADSTS50128`   - invalid domain name
 - `AADSTS50180`   - WindowsIntegratedAuthMissing
 - `AADSTS51001`   - domain hint must be present with on-premises security identifier or on-premises UPN
 - `AADSTS90023`   - invalid request
 - `AADSTS9002313` - invalid request
 - `AADSTS90024`   - request budget exceeded
 - `AADSTS530032`  - blocked by conditional access policy

