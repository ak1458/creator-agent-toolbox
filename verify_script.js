const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  await page.goto('http://localhost:5175');

  // Wait for the app to load
  await page.waitForSelector('text=Creator Agent Toolbox', { timeout: 10000 });

  // Create a new workflow
  await page.fill('input[placeholder="e.g. iPhone Battery Tips"]', 'Test Topic 123');
  await page.click('button:has-text("Create Workflow")');

  try {
    // Wait to see if a workflow appears
    await page.waitForSelector('text=Test Topic 123', { timeout: 15000 });
    console.log("SUCCESS: Workflow created and listed!");
  } catch (err) {
    console.error("FAILED: Could not find created workflow.");
    await page.screenshot({ path: 'verify_error.png' });
  }

  await browser.close();
})();