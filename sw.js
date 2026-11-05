const CACHE="airdrop-radar-v2";
const CORE=["./","./index.html","./manifest.webmanifest","./assets/icon.svg","./data/opportunities.json","./data/discovery-candidates.json"];
self.addEventListener("install",event=>{event.waitUntil(caches.open(CACHE).then(cache=>cache.addAll(CORE)));self.skipWaiting()});
self.addEventListener("activate",event=>{event.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(key=>key!==CACHE).map(key=>caches.delete(key)))));self.clients.claim()});
self.addEventListener("fetch",event=>{
 const request=event.request,url=new URL(request.url);
 if(request.method!=="GET"||url.origin!==location.origin)return;
 if(request.mode==="navigate"){
  event.respondWith(fetch(request,{cache:"no-store"}).then(response=>{if(response.ok){const copy=response.clone();caches.open(CACHE).then(cache=>cache.put("./index.html",copy))}return response}).catch(()=>caches.match("./index.html")));
  return;
 }
 if(url.pathname.includes("/data/")){
  event.respondWith(fetch(request,{cache:"no-store"}).then(response=>{if(response.ok){const copy=response.clone();caches.open(CACHE).then(cache=>cache.put(request,copy))}return response}).catch(()=>caches.match(request)));
  return;
 }
 event.respondWith(caches.match(request).then(cached=>cached||fetch(request).then(response=>{if(response.ok){const copy=response.clone();caches.open(CACHE).then(cache=>cache.put(request,copy))}return response})));
});
