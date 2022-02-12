## Run instructions
- You must run file **"\output\web_io\web_io.exe"** to run the program
- You can see the program log in the **"\output\web_io\report.log"** file

## Input
#### **NOTE: The program also works without a proxy. Therefore, the use of a proxy is not recommended.**
- If you have a list of accounts, you do not need to fill in the first two fields;
  but if you don't have, first two fields are required!
- `Accounts` file format: 
  - username1(space)password1
  - username2(space)password2
  -  ...
- `Proxies` file format: _(for example)_
  - **http**://127.0.0.1:5050
  - **https**://127.0.0.1:8080
  - ...
- Setting the `liking time` is **mandatory**
- `API delay` is optional; the suggested time for this is between 5 and 7 seconds

# Important
## Common problems and their solutions

#### 1st issue: `instagram_private_api.errors.ClientCheckpointRequiredError: checkpoint_challenge_required`
- Solution 1: Go to the application or website and click the **"This is me"** button. Further authorization is successful.
- Solution 2: Your access attempt has been flagged. Login manually to pass the required challenge.

#### 2nd issue: `urllib.error.HTTPError: HTTP Error 400: Bad Request`
- Solution: If there is another error after that, read the next error.

#### 3rd issue: `warnings.warn('Proxy support is alpha.', UserWarning)`
- Solution: Ignore errors like this!

*Note: [Do not forget to run the program with a smile :)]*
