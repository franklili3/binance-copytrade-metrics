# Disable Captcha Solver

> By default, as part of our full proxy unblocking solution, Browser API also solves CAPTCHAs that are encountered while returning your proxy request.

When disabling CAPTCHA solver, our unlocker algorithm still takes care of the entire ever-changing flow of finding the best proxy network, customizing headers, fingerprinting, and more, but intentionally does not solve CAPTCHAs automatically, giving your team a lightweight, streamlined solution, that broadens the scope of your potential scraping opportunities.

Best for:

* Scraping data from websites without getting blocked
* Emulating real-user web behavior
* Teams that don’t have an unblocking infrastructure in-house and don’t want their scraper to solve CAPTCHAs automatically

<Accordion title="How can I get started?">
  To disable CAPTCHA solving just open the relevant zone, go to the ‘configuration’ tab and open the advanced settings where you will find the ‘Automatic Captcha Solving’ controller. To disable CAPTCHA solving just switch off the toggle.

  <Frame>
        <img src="https://mintcdn.com/brightdata/YUhP5HZ1PAScLcu8/images/scraping-automation/scraping-browser/features/captcha-solver/automatic-captcha-solving.png?fit=max&auto=format&n=YUhP5HZ1PAScLcu8&q=85&s=5f946726dfd34a6fe036e3de412eb8ab" alt="automatic-captcha-solving.png" data-og-width="641" width="641" data-og-height="325" height="325" data-path="images/scraping-automation/scraping-browser/features/captcha-solver/automatic-captcha-solving.png" data-optimize="true" data-opv="3" srcset="https://mintcdn.com/brightdata/YUhP5HZ1PAScLcu8/images/scraping-automation/scraping-browser/features/captcha-solver/automatic-captcha-solving.png?w=280&fit=max&auto=format&n=YUhP5HZ1PAScLcu8&q=85&s=35c08e7203a042386759c1d86c778135 280w, https://mintcdn.com/brightdata/YUhP5HZ1PAScLcu8/images/scraping-automation/scraping-browser/features/captcha-solver/automatic-captcha-solving.png?w=560&fit=max&auto=format&n=YUhP5HZ1PAScLcu8&q=85&s=51858cb2eed4e9492d8142415325d991 560w, https://mintcdn.com/brightdata/YUhP5HZ1PAScLcu8/images/scraping-automation/scraping-browser/features/captcha-solver/automatic-captcha-solving.png?w=840&fit=max&auto=format&n=YUhP5HZ1PAScLcu8&q=85&s=18c4f3ca4d0c69d1f1ed2e0970359730 840w, https://mintcdn.com/brightdata/YUhP5HZ1PAScLcu8/images/scraping-automation/scraping-browser/features/captcha-solver/automatic-captcha-solving.png?w=1100&fit=max&auto=format&n=YUhP5HZ1PAScLcu8&q=85&s=bd03f23351c0210d5b4f9059515b9ae2 1100w, https://mintcdn.com/brightdata/YUhP5HZ1PAScLcu8/images/scraping-automation/scraping-browser/features/captcha-solver/automatic-captcha-solving.png?w=1650&fit=max&auto=format&n=YUhP5HZ1PAScLcu8&q=85&s=73d4b973c76890a3b472bac024f0a3f2 1650w, https://mintcdn.com/brightdata/YUhP5HZ1PAScLcu8/images/scraping-automation/scraping-browser/features/captcha-solver/automatic-captcha-solving.png?w=2500&fit=max&auto=format&n=YUhP5HZ1PAScLcu8&q=85&s=7c74386e1bd3aff1cd8501b7d6561d03 2500w" />
  </Frame>
</Accordion>

<Note>
  If you would like to manually configure our default CAPTCHA solver through CDP commands on your own, see [custom CDP functions](/scraping-automation/scraping-browser/cdp-functions/custom)
</Note>
