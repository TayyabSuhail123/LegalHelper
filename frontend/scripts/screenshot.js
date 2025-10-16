const puppeteer = require('puppeteer');
const path = require('path');

async function takeScreenshot() {
  const browser = await puppeteer.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });
  
  const page = await browser.newPage();
  
  // Set viewport to desktop size
  await page.setViewport({ 
    width: 1920, 
    height: 1080,
    deviceScaleFactor: 2 // For high DPI
  });
  
  try {
    // Navigate to the frontend
    await page.goto('http://localhost:3001', { 
      waitUntil: 'networkidle0',
      timeout: 10000 
    });
    
    // Wait a bit for any animations to complete
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Take screenshot
    const screenshotPath = path.join(__dirname, '..', 'docs', 'frontend-screenshot.png');
    await page.screenshot({ 
      path: screenshotPath,
      fullPage: true,
      type: 'png'
    });
    
    console.log(`Screenshot saved to: ${screenshotPath}`);
    
  } catch (error) {
    console.error('Error taking screenshot:', error);
  } finally {
    await browser.close();
  }
}

takeScreenshot();
