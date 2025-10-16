# Browser API Troubleshooting

> Get troubleshooting tips for Browser API. Learn how to use the debugger, analyze error codes, and optimize your web scraping with Chrome Dev Tools.

## Browser API Debugger

Web scraping projects often require intricate interactions with target websites and debugging is vital for identifying and resolving issues found during the development process. The Browser API Debugger serves as a valuable resource, enabling you to inspect, analyze, and fine-tune your code alongside Chrome Dev Tools, resulting in better control, visibility, and efficiency.

### Where to find it

Our Browser API Debugger can be launched via two methods:

1. Manually via Control Panel
2. Remotely via your script

Choose your preferred method below to see more:

<Tabs>
  <Tab title="Manually via Control Panel">
    The Browser API Debugger can be easily accessed within your Bright Data Control Panel. Follow these steps:

    1. Within the control panel, go to [My Zones](https://brightdata.com/cp/zones)
    2. Click on your specific Browser API zone
    3. Click on the **Overview** tab
    4. On the right side, Click on the "Chrome Dev Tools Debugger" button seen below:

       <img src="https://mintcdn.com/brightdata/a-wmt8sZJyXzLgP2/devtool_buttonm_mk1_browser_api.png?fit=max&auto=format&n=a-wmt8sZJyXzLgP2&q=85&s=32ff48619447c4b0ca9398aaed7b4ab9" alt="" data-og-width="1316" width="1316" data-og-height="513" height="513" data-path="devtool_buttonm_mk1_browser_api.png" data-optimize="true" data-opv="3" srcset="https://mintcdn.com/brightdata/a-wmt8sZJyXzLgP2/devtool_buttonm_mk1_browser_api.png?w=280&fit=max&auto=format&n=a-wmt8sZJyXzLgP2&q=85&s=3f5c1087ee8fe0b52c622a29ebb15f93 280w, https://mintcdn.com/brightdata/a-wmt8sZJyXzLgP2/devtool_buttonm_mk1_browser_api.png?w=560&fit=max&auto=format&n=a-wmt8sZJyXzLgP2&q=85&s=8814c84ca2f6fff36a675f5ece715d13 560w, https://mintcdn.com/brightdata/a-wmt8sZJyXzLgP2/devtool_buttonm_mk1_browser_api.png?w=840&fit=max&auto=format&n=a-wmt8sZJyXzLgP2&q=85&s=804b4986bcedbefd4a27f98dbd7f6adb 840w, https://mintcdn.com/brightdata/a-wmt8sZJyXzLgP2/devtool_buttonm_mk1_browser_api.png?w=1100&fit=max&auto=format&n=a-wmt8sZJyXzLgP2&q=85&s=6c891e6a7ce08f1827a54f67d6945a32 1100w, https://mintcdn.com/brightdata/a-wmt8sZJyXzLgP2/devtool_buttonm_mk1_browser_api.png?w=1650&fit=max&auto=format&n=a-wmt8sZJyXzLgP2&q=85&s=cdec206ee5019b21ce88b6a3fd60c67f 1650w, https://mintcdn.com/brightdata/a-wmt8sZJyXzLgP2/devtool_buttonm_mk1_browser_api.png?w=2500&fit=max&auto=format&n=a-wmt8sZJyXzLgP2&q=85&s=9d85a8c3f4d216965f7af05bced476c5 2500w" />

    ### Getting Started with the Debugger & Chrome Dev Tools

    <Steps>
      <Step title="Open a Browser API Session">
        * Ensure you have an active Browser API session
        * If you don't yet know how to launch a Browser API session, see our Quick Start guide.
      </Step>

      <Step title="Launch the Debugger">
        * Once your session is up and running you can now launch the Debugger.
        * Click on the Debugger button within your 'Access parameters' tab to launch the Browser API Debugger interface (see the screenshot above )
      </Step>

      <Step title="Connect with your live browser sessions">
        * Within the Debugger interface, you will find a list of your live Browser API sessions.
        * Select the preferred session that you wish to debug
        * Click on the session link or copy/paste it into your browser of choice, and this will establish a connection between the Debugger and your selected session.

        <Frame>
                    <img src="https://mintcdn.com/brightdata/YUhP5HZ1PAScLcu8/images/scraping-automation/scraping-browser/features/debugger/all-set.png?fit=max&auto=format&n=YUhP5HZ1PAScLcu8&q=85&s=74048beefe970dbc4f5ee5e170a97637" alt="" data-og-width="825" width="825" data-og-height="496" height="496" data-path="images/scraping-automation/scraping-browser/features/debugger/all-set.png" data-optimize="true" data-opv="3" srcset="https://mintcdn.com/brightdata/YUhP5HZ1PAScLcu8/images/scraping-automation/scraping-browser/features/debugger/all-set.png?w=280&fit=max&auto=format&n=YUhP5HZ1PAScLcu8&q=85&s=8c53c528212e9d953cd3892cf9058d7c 280w, https://mintcdn.com/brightdata/YUhP5HZ1PAScLcu8/images/scraping-automation/scraping-browser/features/debugger/all-set.png?w=560&fit=max&auto=format&n=YUhP5HZ1PAScLcu8&q=85&s=e708a4ae91461281156853e813a75463 560w, https://mintcdn.com/brightdata/YUhP5HZ1PAScLcu8/images/scraping-automation/scraping-browser/features/debugger/all-set.png?w=840&fit=max&auto=format&n=YUhP5HZ1PAScLcu8&q=85&s=df4d0f44aa8d66b2200611d863398036 840w, https://mintcdn.com/brightdata/YUhP5HZ1PAScLcu8/images/scraping-automation/scraping-browser/features/debugger/all-set.png?w=1100&fit=max&auto=format&n=YUhP5HZ1PAScLcu8&q=85&s=83fa0e23f80b02236847dc5d61e10897 1100w, https://mintcdn.com/brightdata/YUhP5HZ1PAScLcu8/images/scraping-automation/scraping-browser/features/debugger/all-set.png?w=1650&fit=max&auto=format&n=YUhP5HZ1PAScLcu8&q=85&s=156b16d50d47f71eb26bbff6a6ea22f2 1650w, https://mintcdn.com/brightdata/YUhP5HZ1PAScLcu8/images/scraping-automation/scraping-browser/features/debugger/all-set.png?w=2500&fit=max&auto=format&n=YUhP5HZ1PAScLcu8&q=85&s=5b0ead586ed7027ddcf73a6a51117154 2500w" />
        </Frame>
      </Step>
    </Steps>
  </Tab>

  <Tab title="Remotely via your script">
    To access and launch the debugger session directly from your script, you'll need to send the CDP command:
    `Page.inspect`.

    See the following examples:

    <CodeGroup>
      ```js NodeJS theme={null}
      // Puppeteer - Inspect page using devtools
      const page = await browser.newPage();
      const client = await page.target().createCDPSession();
      const {frameTree: {frame}} = await client.send('Page.getFrameTree', {});
      const {url: inspectUrl} = await client.send('Page.inspect', {
          frameId: frame.id,
      });
      console.log(`Inspect session at ${inspectUrl}`);

      // Playwright - Inspect page using devtools
      const page = await browser.newPage();
      const client = await page.context().newCDPSession(page);
      const {frameTree: {frame}} = await client.send('Page.getFrameTree', {});
      const {url: inspectUrl} = await client.send('Page.inspect', {
          frameId: frame.id,
      });
      console.log(`Inspect session at ${inspectUrl}`);
      ```

      ```python Python theme={null}
      # Playwright - Inspect page using devtools
      page = await browser.new_page()
      client = await page.context.new_cdp_session(page)
      frame_tree = await client.send('Page.getFrameTree', {})
      frame_id = frame_tree['frameTree']['frame']['id']
      inspect = await client.send('Page.inspect', {'frameId': frame_id})
      inspect_url = inspect['url']
      print('Inspect session at', inspect_url)
      ```

      ```cs C# theme={null}
      // PuppeteerSharp - Inspect page using devtools
      var page = await browser.NewPageAsync();
      var client = await page.Target.CreateCDPSessionAsync();
      var frameTree = await client.SendAsync("Page.getFrameTree");
      var frameId = frameTree!["frameTree"]!["frame"]!["id"]!;
      var inspect = await client.SendAsync("Page.inspect", new { frameId = frameId });
      var inspectUrl = inspect["url"]!;
      Console.WriteLine($"Inspect session at {inspectUrl}");

      // Playwright - Inspect page using devtools
      var page = await browser.NewPageAsync();
      var client = await page.Context.NewCDPSessionAsync(page);
      var frameTree = await client.SendAsync("Page.getFrameTree");
      var frameId = frameTree.Value
          .GetProperty("frameTree")
          .GetProperty("frame")
          .GetProperty("id")
          .GetString()!;
      var inspect = await client.SendAsync("Page.inspect", new ()
      {
          { "frameId", frameId },
      });
      var inspectUrl = inspect.Value
          .GetProperty("url")
          .GetString()!;
      Console.WriteLine($"Inspect session at {inspectUrl}");
      ```
    </CodeGroup>
  </Tab>
</Tabs>

### Leveraging Chrome Dev Tools

* With the Browser API Debugger now connected to your live session, you gain access to the powerful features of Chrome Dev Tools.
* Utilize the Dev Tools interface to inspect HTML elements, analyze network requests, debug JavaScript code, and monitor performance. Leverage breakpoints, console logging, and other debugging techniques to identify and resolve issues within your code.

<Frame>
    <img src="https://mintcdn.com/brightdata/YUhP5HZ1PAScLcu8/images/scraping-automation/scraping-browser/features/debugger/test-sites.png?fit=max&auto=format&n=YUhP5HZ1PAScLcu8&q=85&s=01c1fe30fc52736f8e6db0143f99c0ec" alt="test-sites.png" data-og-width="955" width="955" data-og-height="411" height="411" data-path="images/scraping-automation/scraping-browser/features/debugger/test-sites.png" data-optimize="true" data-opv="3" srcset="https://mintcdn.com/brightdata/YUhP5HZ1PAScLcu8/images/scraping-automation/scraping-browser/features/debugger/test-sites.png?w=280&fit=max&auto=format&n=YUhP5HZ1PAScLcu8&q=85&s=5a91b07c094dbd3b3330312923d4ec72 280w, https://mintcdn.com/brightdata/YUhP5HZ1PAScLcu8/images/scraping-automation/scraping-browser/features/debugger/test-sites.png?w=560&fit=max&auto=format&n=YUhP5HZ1PAScLcu8&q=85&s=2875af1c1aab2e3817376c7c4d7175b8 560w, https://mintcdn.com/brightdata/YUhP5HZ1PAScLcu8/images/scraping-automation/scraping-browser/features/debugger/test-sites.png?w=840&fit=max&auto=format&n=YUhP5HZ1PAScLcu8&q=85&s=11d29f0a654d2a75820ca1f8ec87af77 840w, https://mintcdn.com/brightdata/YUhP5HZ1PAScLcu8/images/scraping-automation/scraping-browser/features/debugger/test-sites.png?w=1100&fit=max&auto=format&n=YUhP5HZ1PAScLcu8&q=85&s=7b65a390c1d06badc243b4fdc2507740 1100w, https://mintcdn.com/brightdata/YUhP5HZ1PAScLcu8/images/scraping-automation/scraping-browser/features/debugger/test-sites.png?w=1650&fit=max&auto=format&n=YUhP5HZ1PAScLcu8&q=85&s=ddf826a023ff8838781fae4b2fc15969 1650w, https://mintcdn.com/brightdata/YUhP5HZ1PAScLcu8/images/scraping-automation/scraping-browser/features/debugger/test-sites.png?w=2500&fit=max&auto=format&n=YUhP5HZ1PAScLcu8&q=85&s=cf246e10e2f7486a6aea70fd5b048e8e 2500w" />
</Frame>

### Automatically opening devtools locally to view your live browser session

If you would like to automatically launch devtools on every session to view your live browser session, you can integrate the following code snippet:

```js NodeJS - Puppeteer theme={null}
// Launch devtools locally

const { exec } = require('child_process');
const chromeExecutable = 'google-chrome';

const delay = ms => new Promise(resolve => setTimeout(resolve, ms));
const openDevtools = async (page, client) => {
    // get current frameId
    const frameId = page.mainFrame()._id;
    // get URL for devtools from Browser API
    const { url: inspectUrl } = await client.send('Page.inspect', { frameId });
    // open devtools URL in local chrome
    exec(`"${chromeExecutable}" "${inspectUrl}"`, error => {
        if (error)
            throw new Error('Unable to open devtools: ' + error);
    });
    // wait for devtools ui to load
    await delay(5000);
};

const page = await browser.newPage();
const client = await page.target().createCDPSession();
await openDevtools(page, client);
await page.goto('http://example.com');
```

### Debugger Walkthrough

Check out the Browser API Debugger in action below

<Frame>
  <iframe width="660" height="350" src="https://www.youtube.com/embed/68Kom7tS-QY" title="Debugger Walkthrough" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen />
</Frame>

## Error codes

Analyze some of the popular error codes you might be receiving below:

| Error Code | Meaning                                 | What can you do about it?                                                                                                                                          |
| ---------- | --------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `407`      | An issue with the remote browser's port | Please check your remote browser's port. The correct port for Browser API is either the default port:9222 OR if you are using Selenium specifically, use port:9515 |
| `403`      | Authentication Error                    | Check authentication credentials (username, password) and check that you are using the correct "Browser API" zone from Bright Data control panel                   |
| `503`      | Service Unavailable                     | We are likely scaling browsers right now to meet demand. Try to reconnect in 1 minute.                                                                             |

## FAQs

Check out our [frequently asked questions](/scraping-automation/scraping-browser/faqs) regarding Browser API

## How To

Find out more about the [common library navigational functions](/scraping-automation/scraping-browser/code-examples) and examples for browser automation and specifically for Browser API
