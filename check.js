// Node.js v18+ は fetch が標準搭載

const candidates = [
  "https://park.paa.jp/park2/waiting/clinics/1401.json",
  "https://park.paa.jp/park2/clinics/1401/waiting_status.json",
  "https://park.paa.jp/park2/clinics/1401/businesses/01/waiting_status.json",
];

for (const url of candidates) {
  try {
    const res = await fetch(url);

    if (res.ok) {
      const json = await res.json();
      console.log("FOUND API:", url);
      console.log(json);
    } else {
      console.log("NG:", url, res.status);
    }
  } catch (e) {
    console.log("ERROR:", url, e.message);
  }
}

