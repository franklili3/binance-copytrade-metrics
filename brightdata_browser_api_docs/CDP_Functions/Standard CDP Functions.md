# Standard CDP Functions

> Explore essential CDP functions for Browser API, from setting cookies to country targeting. Learn to optimize web scraping with these common Puppeteer and Playwright commands.

Browser API supports CDP so all puppeteer functions/features work within our browsers. You can find all puppeteer API documentation and usage examples on the [official puppeteer documentation page](https://pptr.dev/). We have also added a few Bright Data-specific [custom CDP events](/scraping-automation/scraping-browser/cdp-functions/custom) which can be useful as well.

The following are a few common browser navigation functions to get you started.

<AccordionGroup>
  <Accordion title="Get Page HTML">
    ```js NodeJS - Puppeteer theme={null}
    const page = await browser.newPage();  
    await page.goto('https://example.com');  
    const html = await page.content();
    ```

    For more info: [https://pptr.dev/api/puppeteer.page.content](https://pptr.dev/api/puppeteer.page.content)
  </Accordion>

  <Accordion title="Click on element">
    ```js NodeJS - Puppeteer theme={null}
    // node.js puppeteer   
    const page = await page.newPage();  
    await page.goto('https://example.com');  
    await page.click('a[href]');
    ```

    For more info: [https://pptr.dev/api/puppeteer.page.click](https://pptr.dev/api/puppeteer.page.click)
  </Accordion>

  <Accordion title="Scroll to page bottom">
    You might need to scroll the viewport to the bottom at times, such as when activating 'infinite scroll'. Here's how:

    ```js NodeJS - Puppeteer theme={null}
    // node.js puppeteer   
    const page = await page.newPage();  
    await page.goto('https://example.com');  
    await page.evaluate(()=>window.scrollBy(0, window.innerHeight));
    ```
  </Accordion>

  <Accordion title="Take Screenshot">
    <CodeGroup>
      ```js NodeJS - Puppeteer theme={null}
      // More info at https://pptr.dev/api/puppeteer.page.screenshot  
      await page.screenshot({ path: 'screenshot.png', fullPage: true });
      ```

      ```python Python - Playwright theme={null}
      # More info at <https://playwright.dev/python/docs/screenshots>  
      await page.screenshot(path='screenshot.png', full_page=True)
      ```

      ```cs C# - PuppeteerSharp theme={null}
      await page.ScreenshotAsync("screenshot.png", new ()  
      {  
          FullPage = true,  
      });
      ```
    </CodeGroup>

    <Note>
      When running the example scripts above the screenshot above will be saved as “screenshot.png” within your files.
    </Note>
  </Accordion>

  <Accordion title="Set Cookies">
    Please note that this is supported onl for customers who completed the KYC verification process.

    ```js NodeJS Puppeteer theme={null}
    const page = await browser.newPage();  
    await page.setCookie({name: 'LANG', value: 'en-US', domain: 'example.com'});  
    await page.goto('https://example.com');
    ```

    For more info: [https://pptr.dev/api/puppeteer.page.setcookie](https://pptr.dev/api/puppeteer.page.setcookie)
  </Accordion>

  <Accordion title="Blocking Endpoints">
    It is possible to block endpoints that are not required to save bandwidth. See an example of this below:

    ```js NodeJS - Puppeteer theme={null}
    // connect to a remote browser...
    const blockedUrls = ['*doubleclick.net*'];
    const page = await browser.newPage();
    const client = await page.target().createCDPSession();
    await client.send('Network.enable');
    await client.send('Network.setBlockedURLs', {urls: blockedUrls});
    await page.goto('https://washingtonpost.com');
    ```
  </Accordion>

  <Accordion title="Country Targeting">
    When using the Browser API, the same **country-targeting** parameter is available to use as in our other proxy products.

    When setting up your script, add the `-country` flag, **after** your "USER" credentials within the Bright Data endpoint, followed by the 2-letter [ISO code](https://www.nationsonline.org/oneworld/country_code_list.htm) for that country.

    ```js  theme={null}
    const SBR_WS_ENDPOINT = `wss://${USER-country-us:PASS}@brd.superproxy.io:9222`;
    ```

    In the example above, we added `-country-us` to the Bright Data endpoint within our script, so our request will originate from the United States ("us").

    #### EU region

    You can target the entire European Union region in the same manner as "Country" above by adding "eu" after "country" in your request: `-country-eu`
    Requests sent using `-country-eu`, will use IPs from **one** of the countries below which are included automatically within "eu":

    ```sh Countries theme={null}
    AL, AZ, KG, BA, UZ, BI, XK, SM, DE, AT, CH, UK, GB, IE, IM, FR, ES, NL, IT, PT, BE, AD, MT, MC, MA, LU, TN, DZ, GI, LI, SE, DK, FI, NO, AX, IS, GG, JE, EU, GL, VA, FX, FO
    ```

    <Note>
      The allocation of a country within the EU is random.
    </Note>
  </Accordion>
</AccordionGroup>
