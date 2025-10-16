# How to Configure the Browser API

> Learn how to set up and configure Bright Data's Browser API with your credentials, run sample scripts, and navigate live browser sessions. Ensure efficient web scraping with our detailed instructions.

To get started, grab your credentials - the Username and Password you will use with your web automation tool. You can find them in the Browser API zone you just created, in the "Overview" tab. We assume that you aleady have your preferred web automation tool installed. If not, please instal it.

## Browser API Quick Start Examples

Run these basic examples to check that your Browser API is working (remember to swap in your credentials and target URL):

<Tip>
  For advanced examples, such as handling [**captchas**](https://docs.brightdata.com/scraping-automation/scraping-browser/cdp-functions/custom#captcha-solver)**,** see the [Code Examples](https://docs.brightdata.com/scraping-automation/scraping-browser/code-examples) section.
</Tip>

<Tabs>
  <Tab title="NodeJS">
    <CodeGroup>
      ```js Puppeteer theme={null}
      #!/usr/bin/env node
      const puppeteer = require('puppeteer-core');
      const {
          // Replace with your Browser API zone credentials
          AUTH = 'USER:PASS',
          TARGET_URL = 'https://example.com',
      } = process.env;

      async function scrape(url = TARGET_URL) {
          if (AUTH == 'USER:PASS') {
              throw new Error(`Provide Browser API credentials in AUTH`
                  + ` environment variable or update the script.`);
          }
          console.log(`Connecting to Browser...`);
          const browserWSEndpoint = `wss://${AUTH}@brd.superproxy.io:9222`;
          const browser = await puppeteer.connect({ browserWSEndpoint });
          try {
              console.log(`Connected! Navigating to ${url}...`);
              const page = await browser.newPage();
              const client = await page.createCDPSession();
              const { frameTree: { frame } } = await client.send('Page.getFrameTree');
              const { url: inspectUrl } = await client.send('Page.inspect', {
                  frameId: frame.id,
              });
              console.log(`You can inspect this session at: ${inspectUrl}.`);
              await page.goto(url, { timeout: 2 * 60 * 1000 });
              console.log(`Navigated! Scraping page content...`);
              const data = await page.content();
              console.log(`Scraped! Data: ${data}`);
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

      ```js Playwright theme={null}
      #!/usr/bin/env node
      const playwright = require('playwright');
      const {
          // Replace with your Browser API zone credentials
          AUTH = 'USER:PASS',
          TARGET_URL = 'https://example.com',
      } = process.env;

      async function scrape(url = TARGET_URL) {
          if (AUTH == 'USER:PASS') {
              throw new Error(`Provide Browser API credentials in AUTH`
                  + ` environment variable or update the script.`);
          }
          console.log(`Connecting to Browser...`);
          const endpointURL = `wss://${AUTH}@brd.superproxy.io:9222`;
          const browser = await playwright.chromium.connectOverCDP(endpointURL);
          try {
              console.log(`Connected! Navigating to ${url}...`);
              const page = await browser.newPage();
              const client = await page.context().newCDPSession(page);
              const { frameTree: { frame } } = await client.send('Page.getFrameTree');
              const { url: inspectUrl } = await client.send('Page.inspect', {
                  frameId: frame.id,
              });
              console.log(`You can inspect this session at: ${inspectUrl}.`);
              await page.goto(url, { timeout: 2 * 60 * 1000 });
              console.log(`Navigated! Scraping page content...`);
              const data = await page.content();
              // Print HTML data
              console.log(`Scraped! Data: ${data}`);
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

      ```js Selenium theme={null}
      #!/usr/bin/env node
      const { Builder, Browser } = require('selenium-webdriver');
      const {
          // Replace with your Browser API zone credentials
          AUTH = 'USER:PASS',
          TARGET_URL = 'https://example.com',
      } = process.env;

      async function scrape(url = TARGET_URL) {
          if (AUTH == 'USER:PASS') {
              throw new Error(`Provide Browser API credentials in AUTH`
                  + ` environment variable or update the script.`);
          }
          console.log(`Connecting to Browser...`);
          const server = `https://${AUTH}@brd.superproxy.io:9515`;
          const driver = await new Builder()
              .forBrowser(Browser.CHROME)
              .usingServer(server)
              .build();
          const cdp = (name, params = {}) => driver.sendAndGetDevToolsCommand(name, params);
          try {
              console.log(`Connected! Navigating to ${url}...`);
              const { frameTree: { frame } } = await cdp('Page.getFrameTree');
              const { url: inspectUrl } = await cdp('Page.inspect', {
                  frameId: frame.id,
              });
              console.log(`You can inspect this session at: ${inspectUrl}.`);
              await driver.get(url);
              console.log(`Navigated! Scraping page content...`);
              const data = await driver.getPageSource();
              console.log(`Scraped! Data: ${data}`);
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
  </Tab>

  <Tab title="Python">
    <CodeGroup>
      ```python Playwright theme={null}
      #!/usr/bin/env python3
      import asyncio
      from os import environ
      from playwright.async_api import Playwright, async_playwright

      # Replace with your Browser API zone credentials
      AUTH = environ.get('AUTH', default='USER:PASS')
      TARGET_URL = environ.get('TARGET_URL', default='https://example.com')


      async def scrape(playwright: Playwright, url=TARGET_URL):
          if AUTH == 'USER:PASS':
              raise Exception('Provide Browser API credentials in AUTH '
                              'environment variable or update the script.')
          print('Connecting to Browser...')
          endpoint_url = f'wss://{AUTH}@brd.superproxy.io:9222'
          browser = await playwright.chromium.connect_over_cdp(endpoint_url)
          try:
              print(f'Connected! Navigating to {url}...')
              page = await browser.new_page()
              client = await page.context.new_cdp_session(page)
              frames = await client.send('Page.getFrameTree')
              frame_id = frames['frameTree']['frame']['id']
              inspect = await client.send('Page.inspect', {
                  'frameId': frame_id,
              })
              inspect_url = inspect['url']
              print(f'You can inspect this session at: {inspect_url}.')
              await page.goto(url, timeout=2*60_000)
              print('Navigated! Scraping page content...')
              data = await page.content()
              print(f'Scraped! Data: {data}')
          finally:
              await browser.close()


      async def main():
          async with async_playwright() as playwright:
              await scrape(playwright)


      if __name__ == '__main__':
          asyncio.run(main())
      ```

      ```python Selenium theme={null}
      #!/usr/bin/env python3
      from os import environ
      from selenium.webdriver import Remote, ChromeOptions as Options
      from selenium.webdriver.chromium.remote_connection import ChromiumRemoteConnection as Connection

      # Replace with your Browser API zone credentials
      AUTH = environ.get('AUTH', default='USER:PASS')
      TARGET_URL = environ.get('TARGET_URL', default='https://example.com')


      def scrape(url=TARGET_URL):
          if AUTH == 'USER:PASS':
              raise Exception('Provide Browser API credentials in AUTH '
                              'environment variable or update the script.')
          print('Connecting to Browser...')
          browserWSEndpoint = f'https://{AUTH}@brd.superproxy.io:9515'
          connection = Connection(browserWSEndpoint, 'goog', 'chrome')
          driver = Remote(connection, options=Options())

          def cdp(cmd, params={}):
              return driver.execute('executeCdpCommand', {
                  'cmd': cmd,
                  'params': params,
              })['value']

          try:
              print(f'Connected! Navigating to {url}...')
              frames = cdp('Page.getFrameTree')
              frame_id = frames['frameTree']['frame']['id']
              inspect = cdp('Page.inspect', {
                  'frameId': frame_id,
              })
              inspect_url = inspect['url']
              print(f'You can inspect this session at: {inspect_url}')
              driver.get(url)
              print('Navigated! Scraping page content...')
              data = driver.page_source
              print(f'Scraped! Data: {data}')
          finally:
              driver.quit()


      if __name__ == '__main__':
          scrape()
      ```
    </CodeGroup>
  </Tab>

  <Tab title="C#">
    <CodeGroup>
      ```cs PuppeteerSharp theme={null}
      using PuppeteerSharp;
      using System.Net.WebSockets;
      using System.Text;

      class Scraper
      {

          private string _auth;

          public Scraper(string auth)
          {
              _auth = auth;
          }

          private async Task<IBrowser> Connect()
          {
              if (_auth == "USER:PASS")
              {
                  throw new Exception("Provide Browser API credentials in AUTH"
                          + " environment variable or update the script.");
              }
              var options = new ConnectOptions()
              {
                  BrowserWSEndpoint = "wss://brd.superproxy.io:9222",
                  WebSocketFactory = async (uri, options, cToken) =>
                  {
                      var socket = new ClientWebSocket();
                      var authBytes = Encoding.UTF8.GetBytes(_auth);
                      var authHeader = "Basic " + Convert.ToBase64String(authBytes);
                      socket.Options.SetRequestHeader("Authorization", authHeader);
                      socket.Options.KeepAliveInterval = TimeSpan.Zero;
                      await socket.ConnectAsync(uri, cToken);
                      return socket;
                  },
              };
              return await Puppeteer.ConnectAsync(options);
          }

          public async Task Scrape(string url)
          {
              Console.WriteLine("Connecting to Browser...");
              var browser = await Connect();
              try {
                  Console.WriteLine($"Connected! Navigating to {url}...");
                  var page = await browser.NewPageAsync();
                  var client = await page.Target.CreateCDPSessionAsync();
                  var frames = await client.SendAsync("Page.getFrameTree");
                  var frameId = frames!.Value.GetProperty("frameTree").GetProperty("frame")
      										.GetProperty("id").GetString();
                  var parameters = new Dictionary<string, object> { { "frameId", frameId } };
                  var inspect = await client.SendAsync("Page.inspect", parameters);
                  var inspectUrl = inspect!.Value.GetProperty("url").GetString();
                  Console.WriteLine($"You can inspect this session at: {inspectUrl}");
                  await page.GoToAsync(url, /* timeout= */ 2 * 60 * 1000);
                  Console.WriteLine("Navigated! Scraping page content...");
                  var data = await page.GetContentAsync();
                  Console.WriteLine($"Scraped! Data: {data}");
              } finally {
                  await browser.CloseAsync();
              }
          }

          private static string Env(string name, string defaultValue)
          {
              return Environment.GetEnvironmentVariable(name) ?? defaultValue;
          }

          public static async Task Main()
          {
              // Replace with your Browser API zone credentials
              var auth = Env("AUTH", "USER:PASS");
              var url = Env("TARGET_URL", "https://example.com");
              var scraper = new Scraper(auth);
              await scraper.Scrape(url);
          }

      }
      ```

      ```cs Playwright theme={null}
      using Microsoft.Playwright;

      class Scraper
      {

          private IPlaywright _pw;
          private string _auth;

          public Scraper(IPlaywright pw, string auth)
          {
              _pw = pw;
              _auth = auth;
          }

          private async Task<IBrowser> Connect()
          {
              if (_auth == "USER:PASS")
              {
                  throw new Exception("Provide Browser API credentials in AUTH"
                          + " environment variable or update the script.");
              }
              var endpointURL = $"wss://{_auth}@brd.superproxy.io:9222";
              return await _pw.Chromium.ConnectOverCDPAsync(endpointURL);
          }

          public async Task Scrape(string url)
          {
              Console.WriteLine("Connecting to Browser...");
              var browser = await Connect();
              try {
                  Console.WriteLine($"Connected! Navigating to {url}...");
                  var page = await browser.NewPageAsync();
                  var client = await page.Context.NewCDPSessionAsync(page);
                  var frames = await client.SendAsync("Page.getFrameTree");
                  var frameId = frames!.Value.GetProperty("frameTree").GetProperty("frame")
      										.GetProperty("id").GetString();
                  var parameters = new Dictionary<string, object> { { "frameId", frameId } };
                  var inspect = await client.SendAsync("Page.inspect", parameters);
                  var inspectUrl = inspect!.Value.GetProperty("url").GetString();
                  Console.WriteLine($"You can inspect this session at: {inspectUrl}");
                  await page.GotoAsync(url, new (){ Timeout = 2 * 60 * 1000 });
                  Console.WriteLine("Navigated! Scraping page content...");
                  var data = await page.ContentAsync();
                  Console.WriteLine($"Scraped! Data: {data}");
              } finally {
                  await browser.CloseAsync();
              }
          }

          private static string Env(string name, string defaultValue)
          {
              return Environment.GetEnvironmentVariable(name) ?? defaultValue;
          }

          public static async Task Main()
          {
              // Replace with your Browser API zone credentials
              var auth = Env("AUTH", "USER:PASS");
              var url = Env("TARGET_URL", "https://example.com");
              var pw = await Playwright.CreateAsync();
              var scraper = new Scraper(pw, auth);
              await scraper.Scrape(url);
          }

      }
      ```

      ```cs Selenium theme={null}
      using OpenQA.Selenium;
      using OpenQA.Selenium.Chrome;
      using OpenQA.Selenium.Remote;

      class Scraper
      {

          private string _auth;

          public Scraper(string auth)
          {
              _auth = auth;
          }

          private WebDriver Connect()
          {
              if (_auth == "USER:PASS")
              {
                  throw new Exception("Provide Browser API credentials in AUTH"
                          + " environment variable or update the script.");
              }
              var uri = new Uri($"https://{_auth}@brd.superproxy.io:9515");
              var executor = new HttpCommandExecutor(uri, TimeSpan.FromSeconds(60));
              var cdpCommand = new HttpCommandInfo(HttpCommandInfo.PostCommand,
                      "/session/{sessionId}/goog/cdp/execute");
              executor.TryAddCommand("cdp", cdpCommand);
              var capabilities = new ChromeOptions().ToCapabilities();
              return new RemoteWebDriver(executor, capabilities);
          }

          public void Scrape(string url)
          {
              Console.WriteLine("Connecting to Browser...");
              var driver = Connect();
              try {
                  Console.WriteLine($"Connected! Navigating to {url}...");
                  var frames = Cdp(driver, "Page.getFrameTree");
                  var frameId = frames.Get<string>("frameTree", "frame", "id");
                  var inspect = Cdp(driver, "Page.inspect", new (){
                      {"frameId", frameId},
                  });
                  var inspectUrl = inspect.Get<string>("url");
                  Console.WriteLine($"You can inspect this session at: {inspectUrl}");
                  driver.Navigate().GoToUrl(url);
                  Console.WriteLine("Navigated! Scraping page content...");
                  var data = driver.PageSource;
                  Console.WriteLine($"Scraped! Data: {data}");
              } finally {
                  driver.Quit();
              }
          }

          private static string Env(string name, string defaultValue)
          {
              return Environment.GetEnvironmentVariable(name) ?? defaultValue;
          }

          private Dictionary<string, object> Cdp(WebDriver driver, string cmd, Dictionary<string, object>? args = null)
          {
              var result = driver.ExecuteCustomDriverCommand("cdp", new ()
              {
                  {"cmd", cmd},
                  {"params", args ?? new ()},
              });
              return (Dictionary<string, object>) result;
          }

          public static void Main()
          {
              // Replace with your Browser API zone credentials
              var auth = Env("AUTH", "USER:PASS");
              var url = Env("TARGET_URL", "https://example.com");
              var scraper = new Scraper(auth);
              scraper.Scrape(url);
          }

      }

      static class DictionaryUtility {

          static public T Get<T>(this Dictionary<string, object> dict, params string[] path)
          {
              object result = dict;
              foreach (var name in path)
              {
                  if (result is Dictionary<string, object> obj)
                      result = obj[name];
                  else
                      throw new Exception("Wrong type");
              }
              return (T) result;
          }
      }
      ```
    </CodeGroup>
  </Tab>
</Tabs>

## Single Navigation Per Session

Browser API sessions are structured to allow one initial navigation per session. This initial navigation refers to the first instance of loading the target site from which data is to be extracted. Following this, users are free to navigate the site using clicks, scrolls, and other interactive actions within the same session. However, to start a new scraping job, either on the same site or a different one, from the initial navigation stage, it is necessary to begin a new session.

## Session Time Limits

Browser API has 2 kinds of timeouts aimed to safeguard our customers from uncontrolled usage.

1. Idle Session Timeout: in case a browser session is kept open for 5 minutes and above in an idle mode, meaning no usage going through it, Browser API will automatically timeout the session.
2. Maximum Session Length Timeout: Browser API session can last up to 30 minutes. Once the maximum session time is reached the session will automatically timeout.
