const fs = require("fs");

const URL = "https://park.paa.jp/park2/clinics/1401/businesses/01";

async function saveHtml() {
  const res = await fetch(URL);
  const html = await res.text();
  fs.writeFileSync("debug.html", html, "utf-8");
  console.log("saved debug.html");
}

saveHtml();

