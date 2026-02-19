import { chromium } from 'playwright';

const consoleMessages = [];
const pageErrors = [];
const result = {
  pass: false,
  topic: `UI Validation Topic ${Date.now()}`,
  workflowUrl: null,
  steps: {
    create: false,
    review: false,
    approve: false,
    refresh: false
  },
  error: null
};

const browser = await chromium.launch({ headless: true });
const context = await browser.newContext();
const page = await context.newPage();

page.on('console', (msg) => {
  if (msg.type() === 'warning' || msg.type() === 'error') {
    consoleMessages.push(`[${msg.type()}] ${msg.text()}`);
  }
});

page.on('pageerror', (err) => {
  pageErrors.push(err.message);
});

try {
  await page.goto('http://localhost:5173', { waitUntil: 'domcontentloaded', timeout: 120000 });
  await page.waitForSelector('input[type="text"]', { timeout: 120000 });

  await page.fill('input[type="text"]', result.topic);
  await page.click('button:has-text("Create Workflow")');

  await page.waitForURL(/\/workflows\//, { timeout: 120000 });
  result.workflowUrl = page.url();
  result.steps.create = true;

  await page.waitForSelector('.script-card', { timeout: 120000 });
  result.steps.review = true;

  await page.click('button:has-text("Approve Selected")');
  await page.waitForFunction(() => {
    return document.body.innerText.toLowerCase().includes('status: completed');
  }, { timeout: 120000 });
  result.steps.approve = true;

  await page.reload({ waitUntil: 'domcontentloaded' });
  await page.waitForFunction(() => {
    return document.body.innerText.toLowerCase().includes('status: completed');
  }, { timeout: 120000 });
  result.steps.refresh = true;

  result.pass = true;
} catch (error) {
  result.error = error instanceof Error ? error.stack : String(error);
}

await browser.close();

const output = {
  result,
  consoleMessages,
  pageErrors
};

console.log(JSON.stringify(output, null, 2));
