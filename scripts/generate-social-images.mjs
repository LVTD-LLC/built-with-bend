// Run with Playwright installed: node scripts/generate-social-images.mjs
// PNGs are committed; ordinary asset builds do not need a browser.
import { chromium } from 'playwright';
import { mkdir } from 'node:fs/promises';

const cards = {
  'bend-2-projects': ['What can you<br>build with <em>Bend 2?</em>', 'From games to editors and databases.<br>Five projects worth exploring.', 'Explore the projects', 'From the blog'],
  directory: ['The things we<br>build with <em>Bend.</em>', 'Apps, games, tools, and experiments.<br>Real projects. Original sources.', 'Explore the directory', 'Discover'],
  blog: ['Ideas. Builds.<br><em>A closer look.</em>', 'Explore the projects and people<br>building with Bend 2.', 'Read the blog', 'Stories'],
  guides: ['Find your way.<br><em>Start building.</em>', 'Your guide to exploring the directory<br>and sharing what you make.', 'Explore the guides', 'Guides'],
  submit: ['Made with Bend?<br><em>Share your build.</em>', 'Put your project in good company.<br>Every submission is human-reviewed.', 'Submit a build', 'Community'],
};
const browser = await chromium.launch();
try {
  const page = await browser.newPage({ viewport: { width: 1200, height: 630 }, deviceScaleFactor: 1 });
  await mkdir('frontend/src/social', { recursive: true });
  for (const [name, [headline, description, action, label]] of Object.entries(cards)) {
    await page.setContent(`<!doctype html><html lang="en"><head><meta charset="utf-8"><style>
      *{box-sizing:border-box;margin:0}html,body{width:1200px;height:630px;overflow:hidden}
      body{background:#fbf8f4;color:#3d3935;font-family:Arial,sans-serif;padding:46px 52px}
      header{display:flex;align-items:center;justify-content:space-between;font-size:25px;font-weight:700}
      .brand{display:flex;align-items:center;gap:13px}.mark{background:#ba442b;color:#fffdf9;width:49px;height:49px;border-radius:6px;font:italic bold 37px Georgia;text-align:center;line-height:47px}
      .label{font-size:20px;font-weight:400;color:#706860}
      main{margin-top:51px;position:relative}h1{font-size:79px;line-height:1.06;letter-spacing:-3px;font-weight:700;position:relative;z-index:1}
      em{font-family:Georgia,serif;font-weight:400;color:#ba442b}p{font-size:27px;line-height:1.42;margin-top:25px;color:#706860}
      .symbol{position:absolute;right:8px;top:-21px;color:#ba442b;font:italic 285px Georgia;line-height:1.1}
      footer{position:absolute;bottom:43px;left:52px;right:52px;border-top:1px solid #e5ddd4;padding-top:24px;display:flex;justify-content:space-between;font-size:21px}
      .action{color:#ba442b} .domain{color:#706860}
    </style></head><body><header><div class="brand"><span class="mark">b.</span>builtwithbend</div><span class="label">${label}</span></header><main><h1>${headline}</h1><p>${description}</p><span class="symbol">↗</span></main><footer><span class="action">${action} ↗</span><span class="domain">builtwithbend.com</span></footer></body></html>`);
    await page.evaluate(() => document.fonts.ready);
    await page.screenshot({ path: `frontend/src/social/${name}.png` });
  }
} finally {
  await browser.close();
}
