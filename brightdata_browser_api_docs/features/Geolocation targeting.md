# Geolocation targeting

> Target specific peers in countries or geographical locations for precise geo-targeted data collection.

<Tip>
  Browser API automatically selects the optimal peer location for your sessions, reducing the need for manual configuration in **most** cases. Manual geo-targeting is useful when accessing region-restricted or location-specific data.
</Tip>

* [**Country**](/scraping-automation/scraping-browser/features/proxy-location#country) - targets peers from a specific country
* [**Geolocation radius**](/scraping-automation/scraping-browser/features/proxy-location#geolocation-radius) – targets peers using an exact latitude, longitude, and radius simulating a precise physical location for more granular geo-targeted data collection.

## Country

Add the `-country` flag, after your `USER` credentials within the Bright Data endpoint, followed by the 2-letter ISO code for that country.

For example, Browser API using Puppeteer in the USA:

<CodeGroup>
  ```sh NodeJS, Puppeteer theme={null}
  const SBR_WS_ENDPOINT = `wss://${USERNAME-country-us:PASSWORD}@brd.superproxy.io:9222`;
  ```
</CodeGroup>

**EU region**
You can target the entire European Union region in the same manner as "Country" above by adding "eu" after "country" in your request: "-country-eu".

Requests sent using -country-eu, will use IPs from one of the countries below which are included automatically within "eu":
`AL, AZ, KG, BA, UZ, BI, XK, SM, DE, AT, CH, UK, GB,IE, IM, FR, ES, NL, IT, PT, BE, AD, MT, MC, MA, LU, TN, DZ, GI, LI, SE, DK, FI, NO, AX, IS, GG, JE, EU, GL, VA, FX, FO.`

## Geolocation radius

Use the `Proxy.setLocation` function to dynamically change the location of your proxies using an exact latitude, longitude, and radius.

### Parameters

<ParamField path="lat" type="float">
  Specifies the latitude of the desired proxy location.
</ParamField>

<ParamField path="lon" type="float">
  Specifies the longitude of the desired proxy location.
</ParamField>

<ParamField path="distance" type="float">
  Defines the maximum distance from the provided coordinates within which the proxy can be located.
  <Note>Unit: Kilometers.</Note>
</ParamField>

<ParamField path="strict" type="boolean" default="true">
  Defines the desired behavior in case no peers are available in the specified distance.

  `strict: true` - our system will search for available peers only within the specific distance.

  `strict: false` - if no peers are available in the specified distance we will automatically expand the distance and look for the nearest available peers.
</ParamField>

### Usage

The `Proxy.setLocation` command should be invoked before navigating to the site for which the proxy is intended. This ensures that the proxy location is set accurately according to the specified parameters before any data requests are made.

**How to run examples**

You need to get Browser API credentials in the control panel.
Pass it in format `SBR_ZONE_FULL_USERNAME:SBR_ZONE_PASSWORD` as environment variable `AUTH`

<CodeGroup>
  ```sh Shell theme={null}
  export AUTH=brd-customer-<customer_id>-zone-<zone_name>:<zone_password>
  ```

  ```sh CMD theme={null}
  set AUTH=brd-customer-<customer_id>-zone-<zone_name>:<zone_password>
  ```

  ```powershell Powershell theme={null}
  $Env:AUTH = 'brd-customer-<customer_id>-zone-<zone_name>:<zone_password>'
  ```
</CodeGroup>

<Tip>You can also pass `TARGET_URL` environment variable to change default targeted website.</Tip>

### Code Examples

Change proxy location before scraping

<Tip>Select your pefered tech-stack</Tip>

<CodeGroup>
  ```js NodeJS - Playwright theme={null}
  #!/usr/bin/env node
  const playwright = require('playwright');
  const {
      AUTH = 'SBR_ZONE_FULL_USERNAME:SBR_ZONE_PASSWORD',
      TARGET_URL = 'https://geo.brdtest.com/mygeo.json',
      LOCATION = 'amsterdam',
  } = process.env;

  const LOCATIONS = Object.freeze({
      amsterdam: { lat: 52.377956, lon: 4.897070 },
      london: { lat: 51.509865, lon: -0.118092 },
      new_york: { lat: 40.730610, lon: -73.935242 },
      paris: { lat: 48.864716, lon: 2.349014 },
  });

  async function scrape(url = TARGET_URL, location = LOCATION) {
      if (AUTH == 'SBR_ZONE_FULL_USERNAME:SBR_ZONE_PASSWORD') {
          throw new Error(`Provide Browser API credentials in AUTH`
              + ` environment variable or update the script.`);
      }
      if (!LOCATIONS[location]) {
          throw new Error(`Unknown location`);
      }
      const { lat, lon } = LOCATIONS[location];
      console.log(`Connecting to Browser...`);
      const endpointURL = `wss://${AUTH}@brd.superproxy.io:9222`;
      const browser = await playwright.chromium.connectOverCDP(endpointURL);
      try {
          console.log(`Connected! Changing proxy location`
              + ` to ${location} (${lat}, ${lon})...`);
          const page = await browser.newPage();
          const client = await page.context().newCDPSession(page);
          await client.send('Proxy.setLocation', {
              lat, lon,
              distance: 50 /* kilometers */,
              strict: true,
          });
          console.log(`Navigating to ${url}...`);
          await page.goto(url, { timeout: 2 * 60 * 1000 });
          console.log(`Navigated! Scraping data...`);
          const data = await page.$eval('body', el => el.innerText);
          console.log(`Scraped! Data:`, JSON.parse(data));
      } finally {
          await browser.close();
      }
  }

  if (require.main == module) {
      scrape().catch(error => {
          console.error(error.stack || error.message || error);
          process.exit(1);
      });
  }
  ```

  ```js NodeJS - Puppeteer theme={null}
  #!/usr/bin/env node
  const puppeteer = require('puppeteer-core');
  const {
      AUTH = 'SBR_ZONE_FULL_USERNAME:SBR_ZONE_PASSWORD',
      TARGET_URL = 'https://geo.brdtest.com/mygeo.json',
      LOCATION = 'amsterdam',
  } = process.env;

  const LOCATIONS = Object.freeze({
      amsterdam: { lat: 52.377956, lon: 4.897070 },
      london: { lat: 51.509865, lon: -0.118092 },
      new_york: { lat: 40.730610, lon: -73.935242 },
      paris: { lat: 48.864716, lon: 2.349014 },
  });

  async function scrape(url = TARGET_URL, location = LOCATION) {
      if (AUTH == 'SBR_ZONE_FULL_USERNAME:SBR_ZONE_PASSWORD') {
          throw new Error(`Provide Browser API credentials in AUTH`
              + ` environment variable or update the script.`);
      }
      if (!LOCATIONS[location]) {
          throw new Error(`Unknown location`);
      }
      const { lat, lon } = LOCATIONS[location];
      console.log(`Connecting to Browser...`);
      const browserWSEndpoint = `wss://${AUTH}@brd.superproxy.io:9222`;
      const browser = await puppeteer.connect({ browserWSEndpoint });
      try {
          console.log(`Connected! Changing proxy location`
              + ` to ${location} (${lat}, ${lon})...`);
          const page = await browser.newPage();
          const client = await page.createCDPSession();
          await client.send('Proxy.setLocation', {
              lat, lon,
              distance: 50 /* kilometers */,
              strict: true,
          });
          console.log(`Navigating to ${url}...`);
          await page.goto(url, { timeout: 2 * 60 * 1000 });
          console.log(`Navigated! Scraping data...`);
          const data = await page.$eval('body', el => el.innerText);
          console.log(`Scraped! Data:`, JSON.parse(data));
      } finally {
          await browser.close();
      }
  }

  function getErrorDetails(error) {
      if (error.target?._req?.res) {
          const {
              statusCode,
              statusMessage,
          } = error.target._req.res;
          return `Unexpected Server Status ${statusCode}: ${statusMessage}`;
      }
  }

  if (require.main == module) {
      scrape().catch(error => {
          console.error(getErrorDetails(error)
              || error.stack
              || error.message
              || error);
          process.exit(1);
      });
  }
  ```

  ```js NodeJS - Selenium theme={null}
  #!/usr/bin/env node
  const { Builder, Browser, By } = require('selenium-webdriver');
  const {
      AUTH = 'SBR_ZONE_FULL_USERNAME:SBR_ZONE_PASSWORD',
      TARGET_URL = 'https://geo.brdtest.com/mygeo.json',
      LOCATION = 'amsterdam',
  } = process.env;

  const LOCATIONS = Object.freeze({
      amsterdam: { lat: 52.377956, lon: 4.897070 },
      london: { lat: 51.509865, lon: -0.118092 },
      new_york: { lat: 40.730610, lon: -73.935242 },
      paris: { lat: 48.864716, lon: 2.349014 },
  });

  async function scrape(url = TARGET_URL, location = LOCATION) {
      if (AUTH == 'SBR_ZONE_FULL_USERNAME:SBR_ZONE_PASSWORD') {
          throw new Error(`Provide Browser API credentials in AUTH`
              + ` environment variable or update the script.`);
      }
      if (!LOCATIONS[location]) {
          throw new Error(`Unknown location`);
      }
      const { lat, lon } = LOCATIONS[location];
      console.log(`Connecting to Browser...`);
      const server = `https://${AUTH}@brd.superproxy.io:9515`;
      const driver = await new Builder()
          .forBrowser(Browser.CHROME)
          .usingServer(server)
          .build();
      try {
          console.log(`Connected! Changing proxy location`
              + ` to ${location} (${lat}, ${lon})...`);
          await driver.sendAndGetDevToolsCommand('Proxy.setLocation', {
              lat, lon,
              distance: 50 /* kilometers */,
              strict: true,
          });
          console.log(`Navigating to ${url}...`);
          await driver.get(url);
          console.log(`Navigated! Scraping data...`);
          const body = await driver.findElement(By.css('body'));
          const data = await body.getText();
          console.log(`Scraped! Data:`, JSON.parse(data));
      } finally {
          await driver.quit();
      }
  }

  if (require.main == module) {
      scrape().catch(error => {
          console.error(error.stack || error.message || error);
          process.exit(1);
      });
  }
  ```
</CodeGroup>
