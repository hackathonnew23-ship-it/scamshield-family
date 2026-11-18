var C='scamshield-v9';
var CORE=['./','./index.html','./manifest.webmanifest','./icon.svg','./rules.json'];
self.addEventListener('install',function(e){
  self.skipWaiting();
  e.waitUntil(caches.open(C).then(function(c){return Promise.all(CORE.map(function(u){return c.add(u).catch(function(){})}))}));
});
self.addEventListener('activate',function(e){
  e.waitUntil(caches.keys().then(function(k){
    return Promise.all(k.filter(function(x){return x!==C}).map(function(x){return caches.delete(x)}));
  }).then(function(){return self.clients.claim()}));
});
self.addEventListener('fetch',function(e){
  var r=e.request;
  if(r.method!=='GET')return;
  var u=new URL(r.url);
  if(u.origin!==location.origin)return;
  var fresh=r.mode==='navigate'||/rules\.json$/.test(u.pathname);
  e.respondWith(fetch(r).then(function(res){
    if(res&&res.ok){var cp=res.clone();caches.open(C).then(function(c){c.put(r,cp)})}
    return res;
  }).catch(function(){
    return caches.match(r,{ignoreSearch:true}).then(function(hit){
      return hit||(r.mode==='navigate'?caches.match('./index.html'):Response.error());
    });
  }));
});
