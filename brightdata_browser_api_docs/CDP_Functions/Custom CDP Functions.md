# Custom CDP Functions

> In addition to the [standard CDP Functions](/scraping-automation/scraping-browser/cdp-functions/standard), Browser API also provides some powerful custom CDP Functions.

## Captcha Solver

When navigating a page with Browser API, our integrated CAPTCHA solver **automatically solves all CAPTCHAs** by default. You can monitor this auto-solving process in your code with the following custom CDP functions.

<Note>
  If you would like to disable CAPTCHA solver entirely through the Control Panel see our feature for [Disable Captcha Solver](/scraping-automation/scraping-browser/features/captcha-solver)
</Note>

<Note>
  Once a CAPTCHA is solved, if there is a form to submit, it will be submitted by default.
</Note>

## CAPTCHA Solver - Automatic Solve

<AccordionGroup>
  <Accordion title="Captcha.solve">
    Use this command to return the status after the captcha was solved, failed, or not detected.

    <CodeGroup>
      ```js Captcha.solve theme={null}
      Captcha.solve({
          detectTimeout?: number // Detect timeout in millisecond for solver to detect captcha  
          options?: CaptchaOptions[] // Configuration options for captcha solving  
      }) : SolveResult
      ```

      ```js SolveResult theme={null}
      SolveResult : {  
        status: SolveStatus // Detect and solve status  
        type?: string // Detected captcha type  
        error?: string // Error if captcha was not solved  
      }
      ```

      ```js SolveStatus theme={null}
      SolveStatus : string enum {  
        "not_detected" // Captcha was not detected  
        "solve_finished" // Captcha successfully solved  
        "solve_failed" // Captcha detected, but was not solved  
        "invalid" // Something goes wrong  
      }
      ```
    </CodeGroup>

    **Examples**

    <CodeGroup>
      ```js NodeJS - Puppeteer theme={null}
      const page = await browser.newPage();
      const client = await page.target().createCDPSession();
      await page.goto('[https://site-with-captcha.com](https://site-with-captcha.com/)');  

      // Note 1: If no captcha was found it will return not_detected status after detectTimeout   
      // Note 2: Once a CAPTCHA is solved, if there is a form to submit, it will be submitted by default   

      const client = await page.target().createCDPSession();  
      const {status} = await client.send('Captcha.solve', {detectTimeout: 30*1000});   
      console.log(`Captcha solve status: ${status}`)
      ```

      ```python Python - Playwright theme={null}
      page = await browser.new_page()   
      client = await page.context.new_cdp_session(page)   
      await page.goto('[https://site-with-captcha.com](https://site-with-captcha.com/)')  
      # Note 1: If no captcha was found it will return not_detected status after detectTimeout   
      # Note 2: Once a CAPTCHA is solved, if there is a form to submit, it will be submitted by default  
      client = await page.context.new_cdp_session(page)  
      solve_result = await client.send('Captcha.solve', { 'detectTimeout': 30*1000 })   
      status = solve_result['status']   
      print(f'Captcha solve status: {status}') 
      ```
    </CodeGroup>

    <Note>
      If CAPTCHA-solving fails, please attempt a retry. If the issue persists, submit a support reques detailing the specific problem you encountered.
    </Note>
  </Accordion>

  <Accordion title="Custom CDP commands for CAPTCHA status">
    Use the commands below to pinpoint a more specific stage in the CAPTCHA solving flow:

    |                         |                                                                 |
    | ----------------------- | --------------------------------------------------------------- |
    | `Captcha.detected`      | Browser API has encountered a CAPTCHA and has begun to solve it |
    | `Captcha.solveFinished` | Browser API successfully solved the CAPTCHA                     |
    | `Captcha.solveFailed`   | Browser API failed in solving the CAPTCHA                       |
    | `Captcha.waitForSolve`  | Browser API waits for CAPTCHA solver to finish                  |

    **Examples**

    <Tabs>
      <Tab title="Asynchronous">
        The following code sets up a CDP session, listens for CAPTCHA events, and handles timeouts:

        <CodeGroup>
          ```js NodeJS - Puppeteer theme={null}
          // Node.js - Puppeteer - waiting for CAPTCHA solving events  
          const client = await page.target().createCDPSession();   
          await new Promise((resolve, reject)=>{   
            client.on('Captcha.solveFinished', resolve);   
            client.on('Captcha.solveFailed', ()=>reject(new Error('Captcha failed')));   
            setTimeout(reject, 5 * 60 * 1000, new Error('Captcha solve timeout'));  
          });
          ```

          ```python Python - Playwright theme={null}
          # Python - Playwright - waiting for CAPTCHA solving events  
          client = await page.context.new_cdp_session(page)  
          client.on('Captcha.detected', lambda c: print('Captcha detected', c))   
          client.on('Captcha.solveFinished', lambda _: print('Captcha solved!'))   
          client.on('Captcha.solveFailed', lambda _: print('Captcha failed!'))
          ```
        </CodeGroup>
      </Tab>

      <Tab title="Synchronous">
        <Warning>
          Selenium doesn't support asynchronous server-driven events like Puppeteer and Playwright.
        </Warning>

        The `Captcha.waitForSolve` command waits for Browser API's CAPTCHA solver to finish.

        ```python Python - Selenium theme={null}
        # Python Selenium - Waiting for Captcha to auto-solve after navigate  
        driver.execute('executeCdpCommand', {  
            'cmd': 'Captcha.waitForSolve',  
            'params': {},  
        })
        ```
      </Tab>
    </Tabs>
  </Accordion>
</AccordionGroup>

## CAPTCHA Solver - Manual Control

If you would like to either manually configure or fully disable our default CAPTCHA solver and instead call the solver manually or solve on your own, see the following CDP commands and functionality.

<AccordionGroup>
  <Accordion title="Captcha.setAutoSolve">
    This command is used to control the auto-solving of a CAPTCHA. You can disable auto-solve or configure algorithms for different CAPTCHA types and manually trigger this:

    <CodeGroup>
      ```js Captcha.setAutoSolve theme={null}
      Captcha.setAutoSolve({  
        autoSolve: boolean // Whether to automatically solve captcha after navigate  
        options?: CaptchaOptions[] // Configuration options for captcha auto-solving  
      }) : void
      ```

      ```js CaptchaOptions theme={null}
      CaptchaOptions : {  
        type: string // Captcha type  
        disabled?: boolean // Disable detect and solve for specified captcha  
        ... // additinal options related to captcha type  
      }
      ```
    </CodeGroup>

    Examples of CDP commands to disable auto-solver **completely** within the session:

    <CodeGroup>
      ```js NodeJS - Puppeteer theme={null}
      // Node.js Puppeteer - Disable Captcha auto-solver completely  
      const page = await browser.newPage();  
      const client = await page.target().createCDPSession();  
      await client.send('Captcha.setAutoSolve', { autoSolve: false })
      ```

      ```python Python - Playwright theme={null}
      # Python Playwright - Disable Captcha auto-solver completely  
      page = await browser.new_page()  
      client = await page.context.new_cdp_session(page)  
      await client.send('Captcha.setAutoSolve', {'autoSolve': False}):
      ```

      ```python - Selenium theme={null}
      # Python Selenium - Disable Captcha auto-solver completely  
      driver.execute('executeCdpCommand', {  
          'cmd': 'Captcha.setAutoSolve',  
          'params': {'autoSolve': False},  
      })
      ```
    </CodeGroup>
  </Accordion>

  <Accordion title="Disable auto-solver for a specific CAPTCHA type only - Examples">
    <CodeGroup>
      ```js NodeJS - Puppeteer theme={null}
      // Node.js Puppeteer - Disable Captcha auto-solver for ReCaptcha only  
      const page = await browser.newPage();  
      const client = await page.target().createCDPSession();  
      await client.send('Captcha.setAutoSolve', {  
          autoSolve: true,  
          options: [{  
              type: 'usercaptcha',  
              disabled: true,  
          }],  
      });
      ```

      ```python Python - Playwright theme={null}
      # Python Playwright - Disable Captcha auto-solver for ReCaptcha only  
      page = await browser.new_page()  
      client = await page.context.new_cdp_session(page)  
      await client.send('Captcha.setAutoSolve', {  
          'autoSolve': True,  
          'options': [{  
              'type': 'usercaptcha',  
              'disabled': True,  
          }],  
      })
      ```
    </CodeGroup>
  </Accordion>

  <Accordion title="Manually solving CAPTCHAs - Examples">
    <CodeGroup>
      ```js NodeJS - Puppeteer theme={null}
      // Node.js Puppeteer - manually solving CAPTCHA after navigation  
      const page = await browser.newPage();  
      const client = await page.target().createCDPSession();  
      await client.send('Captcha.setAutoSolve', { autoSolve: false });  
      await page.goto('https://site-with-captcha.com', { timeout: 2*60*1000 });  
      const {status} = await client.send('Captcha.solve', { detectTimeout: 30*1000 });  
      console.log('Captcha solve status:', status);
      ```

      ```python Python - Playwright theme={null}
      # Python Playwright- manually solving CAPTCHA after navigation  
      page = await browser.new_page()  
      client = await page.context.new_cdp_session(page)  
      await client.send('Captcha.setAutoSolve', {'autoSolve': False})  
      await page.goto('https://site-with-captcha.com', timeout=2*60_000)  
      solve_result = await client.send('Captcha.solve', {'detectTimeout': 30_000})  
      print('Captcha solve status:', solve_result['status'])
      ```

      ```python Python - Selenium theme={null}
      # Python Selenium - manually solving CAPTCHA after navigation  
      driver.execute('executeCdpCommand', {  
          'cmd': 'Captcha.setAutoSolve',  
          'params': {'autoSolve': False},  
      })  
      driver.get('https://site-with-captcha.com')  
      solve_result = driver.execute('executeCdpCommand', {  
          'cmd': 'Captcha.solve',  
          'params': {'detectTimeout': 30_000},  
      })  
      print('Captcha solve status:', solve_result['value']['status'])
      ```
    </CodeGroup>
  </Accordion>

  <Accordion title="CaptchaOptions for other Captcha types">
    For the following three CAPTCHA types we support the following additional options to control and configure our auto-solving algorithm.

    <Tabs>
      <Tab title="CF Challenge">
        ```js CF Challenge theme={null}
        timeout: 40000  
        selector: '#challenge-body-text, .challenge-form'  
        check_timeout: 300  
        error_selector: '#challenge-error-title'  
        success_selector: '#challenge-success[style*=inline]'  
        check_success_timeout: 300  
        btn_selector: '#challenge-stage input[type=button]'  
        cloudflare_checkbox_frame_selector: '#turnstile-wrapper iframe'  
        checkbox_area_selector: '.ctp-checkbox-label .mark'  
        wait_timeout_after_solve: 500  
        wait_networkidle: {timeout: 500}
        ```
      </Tab>

      <Tab title="HCaptcha">
        ```js HCaptcha theme={null}
        detect_selector:  
          '#cf-hcaptcha-container, #challenge-hcaptcha-wrapper .hcaptcha-box, .h-captcha'  
        pass_proxy: true  
        submit_form: true  
        submit_selector: '#challenge-form body > form[action*="internalcaptcha/captchasubmit"]  
        value_selector: '.h-captcha textarea[id^="h-captcha-response"]'  
          
        ```
      </Tab>

      <Tab title="usercaptcha (reCAPTCHA)">
        ```js UserCaptcha (reCAPTCHA) theme={null}
        { // configuration keys and default values for reCAPTCHA (type=usercaptcha)  
          type: 'usercaptcha',  
          // selector to retrieve sitekey and/or action  
          selector: '.g-recaptcha, .recaptcha',  
          // attributes to search for sitekey  
          sitekey_attributes: ['data-sitekey', 'data-key'],  
          // attributes to search for action  
          action_attributes: ['data-action'],  
          // detect selectors  
          detect_selector: `  
            .g-recaptcha[data-sitekey] > *,  
            .recaptcha > *,  
            iframe[src*="[www.google.com/recaptcha/api2](http://www.google.com/recaptcha/api2)"],  
            iframe[src*="[www.recaptcha.net/recaptcha/api2](http://www.recaptcha.net/recaptcha/api2)"],  
            iframe[src*="[www.google.com/recaptcha/enterprise](http://www.google.com/recaptcha/enterprise)"]`,  
          // element to type response code into  
          reponse_selector: '#g-recaptcha-response, .g-recaptcha-response',  
          // should solver submit form automatically after captcha solved  
          submit_form: true,  
          // selector for submit button  
          submit_selector: '[type=submit]',  
        }
        ```
      </Tab>
    </Tabs>
  </Accordion>
</AccordionGroup>

## Emulation Functions

<AccordionGroup>
  <Accordion title="Emulation.getSupportedDevices">
    Use this command to get a list of all possible devices that can be emulated. This method returns an array of device options that can be used with the setDevice command.

    ```js Example theme={null}
    const devices = await client.send("Emulation.getSupportedDevices");
    console.log(devices);
    ```
  </Accordion>

  <Accordion title="Emulation.setDevice">
    Once you've received the list above of supported devices, you can emulate a specific device using the Emulation.setDevice command. This command changes the screen width, height, userAgent, and devicePixelRatio to match the specified device.

    <CodeGroup>
      ```js Usage theme={null}
      await client.send("Emulation.setDevice", { device: "[device_name]" });
      ```

      ```js Example theme={null}
      await client.send("Emulation.setDevice", { device: "Vivo X200 Pro" });
      ```
    </CodeGroup>

    ## Landscape mode

    If you wish to change the orientation to landscape (for devices that support it), add the string `landscape` after the `device_name`.

    ```js Example theme={null}
    await client.send("Emulation.setDevice", { device: "Vivo X200 Pro landscape" });
    ```
  </Accordion>
</AccordionGroup>

## Ad Blocker

Enabling our `AdBlock` feature can help **reduce bandwidth** usage and **improve performance** on ad-heavy websites.

### CDP Commands

* `Unblocker.enableAdBlock` – Enables ad blocker (default: off)
* `Unblocker.disableAdBlock` – Disables ad blocker

<Tip>
  We recommend enabling ad blocking before navigating to the target page.
</Tip>

```js Example theme={null}
// Enable ad blocking before navigating
const client = await page.createCDPSession();

try {
    await client.send('Unblocker.enableAdBlock', {
        list: [null],
    });
} catch (e) {
    console.error(e.stack || e);
}

await page.goto('https://www.w3schools.com/html/html_forms.asp');
```

See the full [ad blocker example script](https://github.com/luminati-io/sbr-examples/blob/main/nodejs/puppeteer-ad-block/scrape.js).

## Session Persistence

Use this command to reuse the same proxy peer across multiple browsing sessions. This is useful for scenarios where maintaining a consistent session is required, such as preserving browser states or IP-based continuity.

### CDP Commands

* `Proxy.useSession` – Associates a session with a specific session ID.
* `sessionId` – A unique string that identifies your session.

<Note>
  Use the CDP command before navigation to the target page.
</Note>

```js Example theme={null}
const client = await page.createCDPSession();
await client.send('Proxy.useSession', { sessionId });
await page.goto('https://geo.brdtest.com/mygeo.json');
```

<Tip>
  See the full [session persistence example script](https://github.com/luminati-io/sbr-examples/blob/main/nodejs/puppeteer-proxy-session/scrape.js).
</Tip>

## File Download

You can automate file downloads in your Browser API flows using the custom Download CDP domain. This is useful for workflows that require downloading files (e.g., CSV, PDF) directly during browser automation.

### CDP Commands

* `Download.enable` – Enables file downloads for specified content types.
* `Download.downloadRequest` – Fires when request results in download.
* `Download.getLastCompleted` – Retrieves information about the last completed download.
* `Download.getDownloadedBody` – Gets the actual downloaded file content.

```js Example theme={null}
const client = await page.createCDPSession();

// Enable downloads for binary files like CSV
await client.send('Download.enable', { allowedContentTypes: ['application/octet-stream'] });

// initiate download file
await Promise.all([
  new Promise(resolve => client.once('Download.downloadRequest', resolve)),
  page.click(selector),
]);

// After download completes:
const { id } = await client.send('Download.getLastCompleted');
const { body, base64Encoded } = await client.send('Download.getDownloadedBody', { id });
const fs = require('fs');
fs.writeFileSync('./downloaded_file.csv', base64Encoded ? Buffer.from(body, 'base64') : body);
```

<Tip>
  See the full [file download example script](https://github.com/luminati-io/sbr-examples/blob/main/nodejs/puppeteer-file-download/scrape.js).
</Tip>

## Faster Text Input

For scenarios that need rapid or bulk text input, use the custom Input.type CDP command. This approach is much faster than standard CDP text input methods, making it well suited for automation tasks requiring high-speed typing or handling large volumes of text.

### CDP Commands

* `Input.type` - Sends keystrokes or simulates typing the specified text into the currently focused element.

```js Example theme={null}
const client = await page.createCDPSession();

// Focus the input element
await page.focus('input');

// Type a message
await client.send('Input.type', {
  text: 'what is the best place to try pizza and pasta?'
});
```

## Custom Client SSL/TLS Certificates

Use this command to install custom client SSL/TLS certificates where required for specific domain authentication. These certificates are applied for the duration of a **single** Browser API session and are automatically removed once the session ends.

<AccordionGroup>
  <Accordion title="Browser.addCertificate">
    ```javascript  theme={null}
    Browser.addCertificate(params: {
      cert: string // base64 encoded certificate file
      pass: string // password for the certificate
    }) : void
    ```
  </Accordion>

  <Accordion title="Code examples">
    * Replace placeholder values `SBR_ZONE_FULL_USERNAME:SBR_ZONE_PASSWORD` with your valid Browser API credentials.
    * Replace `client.pfx` with the actual path to your certificate file. This file should be a valid SSL/TLS client certificate in .pfx format.
    * Replace `secret` with the actual password for the certificate.

      <CodeGroup>
        ```js NodeJS - Puppeteer theme={null}
        const puppeteer = require('puppeteer-core');
        const fs = require('fs/promises');
        const {
          AUTH = 'SBR_ZONE_FULL_USERNAME:SBR_ZONE_PASSWORD',
          TARGET_URL = 'https://example.com',
          CERT_FILE = 'client.pfx',
          CERT_PASS = 'secret',
        } = process.env;

        async function scrape(url = TARGET_URL, file = CERT_FILE, pass = CERT_PASS) {
          if (AUTH == 'SBR_ZONE_FULL_USERNAME:SBR_ZONE_PASSWORD') {
            throw new Error(`Provide Browser API credentials in AUTH`
                + ` environment variable or update the script.`);
          }
          console.log(`Connecting to Browser...`);
          const browserWSEndpoint = `wss://${AUTH}@brd.superproxy.io:9222`;
          const browser = await puppeteer.connect({ browserWSEndpoint });
          try {
            console.log(`Connected! Installing ${file} certificate...`);
            const page = await browser.newPage();
            const client = await page.createCDPSession();
            const cert = (await fs.readFile(CERT_FILE)).toString('base64');
            await client.send('Browser.addCertificate', { cert, pass });
            console.log(`Installed! Navigating to ${url}...`);
            await page.goto(url, { timeout: 2 * 60 * 1000 });
            console.log(`Navigated! Scraping page content...`);
            const data = await page.content();
            console.log(`Scraped! Data: ${data}`);
          } finally {
            await browser.close();
          }
        }

        scrape();
        ```

        ```python Python - Selenium theme={null}
        from os import environ
        from base64 import standard_b64encode
        from selenium.webdriver import Remote, ChromeOptions as Options
        from selenium.webdriver.chromium.remote_connection import ChromiumRemoteConnection as Connection

        AUTH = environ.get('AUTH', default='SBR_ZONE_FULL_USERNAME:SBR_ZONE_PASSWORD')
        TARGET_URL = environ.get('TARGET_URL', default='https://example.com')
        CERT_FILE = environ.get('CERT_FILE', default='client.pfx')
        CERT_PASS = environ.get('CERT_PASS', default='secret')

        def scrape(url=TARGET_URL, file=CERT_FILE, pswd=CERT_PASS):
            if AUTH == 'SBR_ZONE_FULL_USERNAME:SBR_ZONE_PASSWORD':
            raise Exception('Provide Browser API credentials in AUTH '
                            'environment variable or update the script.')
            print('Connecting to Browser...')
            server_addr = f'https://{AUTH}@brd.superproxy.io:9515'
            connection = Connection(server_addr, 'goog', 'chrome')
            driver = Remote(connection, options=Options())
            try:
                print(f'Connected! Installing {file} certificate...')
                with open(file, 'rb') as f:
                    cert = standard_b64encode(f.read()).decode()
                driver.execute('executeCdpCommand', {
                    'cmd': 'Browser.addCertificate',
                    'params': {'cert': cert, 'pass': pswd},
                })
                print(f'Installed! Navigating to {url}...')
                driver.get(url)
                print('Navigated! Scraping page content...')
                data = driver.page_source
                print(f'Scraped! Data: {data}')
            finally:
                driver.quit()

        scrape()
        ```
      </CodeGroup>
  </Accordion>
</AccordionGroup>
