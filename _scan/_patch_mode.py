# -*- coding: utf-8 -*-
"""One-shot patch: fix the jump chain in _scan/template.html.

Root cause: pageUrl() returned a relative "p/<key>/..." path whenever the page
was not opened via file://. That is only valid when the page is served by
serve.py. Opened via a plain static server / built-in preview, the link 404s ->
"open main entry" reports unreachable.

Fix: probe the server identity via GET /__console__ (served by serve.py), then
      (a) use ABSOLUTE /p/<key>/... when the probe succeeds,
      (b) fall back to file:// + copy-path when it does not.
"""
import io
import sys

TPL = r"D:/ai_person/personal-all-console/_scan/template.html"
t = io.open(TPL, encoding="utf-8", newline="").read()
n_ok = 0


def rep(name, old, new, expect=1):
    global t, n_ok
    n = t.count(old)
    if n != expect:
        print("[FAIL] %s: matched %d (expected %d)" % (name, n, expect))
        sys.exit(1)
    t = t.replace(old, new)
    n_ok += 1
    print("[ok] " + name)


# ---------- A. HTML: mode hint container ----------
rep("A modebar container",
    '  <div id="fresh"></div>\n  <div class="ports" id="ports"></div>',
    '  <div id="fresh"></div>\n  <div id="modebar"></div>\n  <div class="ports" id="ports"></div>')

# ---------- B. CSS ----------
rep("B modebar css",
    '</style>',
    '''/* ---------- mode hint bar: static-preview fallback notice ---------- */
.modebar{display:flex;align-items:flex-start;gap:11px;margin:0 0 14px;padding:11px 16px;border-radius:12px;
  border:1px solid rgba(56,189,248,.42);background:rgba(56,189,248,.09);color:#bfe6ff;font-size:12.5px;line-height:1.75}
.modebar svg{width:16px;height:16px;stroke:currentColor;fill:none;stroke-width:2;flex:none;margin-top:3px;
  stroke-linecap:round;stroke-linejoin:round}
.modebar b{color:#e8f6ff}
.modebar code{background:rgba(56,189,248,.16);padding:1px 5px;border-radius:4px}
</style>''')

# ---------- C. JS: server-identity probe ----------
rep("C serve probe",
    'const DISC = _RAW.discovered||[];',
    r'''const DISC = _RAW.discovered||[];

/* ---------- runtime mode probe ----------
   Only the real serve.py exposes /p/<key>/ repository mounts. Opened through a
   plain static server or the built-in preview there are no mounts, so emitting
   p/<key>/ links makes "open main entry" 404. Probe the server identity first:
   on failure, always degrade to file:// + copy-path. */
let SERVE_OK=false;
const SERVE_READY = (location.protocol==='file:')
  ? Promise.resolve(false)
  : fetch('/__console__',{cache:'no-store'})
      .then(r=>r.ok?r.json():null)
      .then(j=>{ SERVE_OK=!!(j&&j.console==='personal-all-console'); return SERVE_OK; })
      .catch(()=>{ SERVE_OK=false; return false; });
SERVE_READY.then(ok=>{
  if(ok||location.protocol==='file:') return;
  const el=document.getElementById('modebar'); if(!el) return;
  el.className='modebar';
  el.innerHTML='<svg viewBox="0 0 24 24"><path d="M12 3l9 16H3z"/><path d="M12 9v5M12 17h.01"/></svg>'+
    '<div>当前是<b>静态预览模式</b>：没有检测到工作台服务，浏览器又禁止网页打开本地文件，'+
    '所以点「打开主入口」只会把本地路径复制给你。<br>要能直接跳转，请运行 <code>start.bat</code>'+
    '（或 <code>python serve.py</code>）后访问 <code>http://127.0.0.1:3000/</code>。</div>';
});''')

# ---------- D. pageUrl ----------
rep("D pageUrl",
    r'''function pageUrl(root,rel){
  if(location.protocol!=='file:'){
    const n=s=>String(s).replace(/\\/g,'/').replace(/\/+$/,'').toLowerCase();
    const d=ALL.find(x=>n(x.root)===n(root));
    if(d) return 'p/'+d.key+'/'+(rel||'');
  }
  return fileUrl(root,rel);
}''',
    r'''function pageUrl(root,rel){
  if(SERVE_OK){
    const n=s=>String(s).replace(/\\/g,'/').replace(/\/+$/,'').toLowerCase();
    const d=ALL.find(x=>n(x.root)===n(root));
    // absolute path: serve.py mounts at site root; a relative one breaks when
    // the console page itself lives under a sub-path
    if(d) return '/p/'+d.key+'/'+String(rel||'').replace(/^\/+/,'');
  }
  return fileUrl(root,rel);
}''')

# ---------- E. openIt ----------
rep("E openIt",
    r'''function openIt(p,rel){
  const relpath = String(rel||'').replace(/^dir:\/\//,'');   // 目录型条目同样落到 /p/<key>/ 或本地目录
  const url = /^https?:\/\//i.test(p) ? p : pageUrl(p,relpath);
  if(/^file:/i.test(url) && location.protocol!=='file:'){
    // http(s) 页面里浏览器安全策略禁止打开 file:// 链接：转为本地路径复制兜底
    let nat=url.slice(7); if(nat.startsWith('/')) nat=nat.slice(1);
    try{ nat=decodeURIComponent(nat); }catch(e){}
    cp(nat.replace(/\//g,'\\'),'浏览器禁止 http 页面打开本地文件，路径已复制；建议双击 index.html（file://）打开本工作台');
  } else window.open(url,'_blank');
  const it = REC.find(x=>x.k===p+relpath);
  if(it){ it.t=Date.now(); } else { REC.unshift({k:p+relpath,n:arguments[2]||'',t:Date.now()}); REC=REC.slice(0,40); }
  jset(LS_REC,REC);
}''',
    r'''async function openIt(p,rel){
  const relpath = String(rel||'').replace(/^dir:\/\//,'');   // 目录型条目同样落到 /p/<key>/ 或本地目录
  await SERVE_READY;                 // 等探测结束：渲染可能早于探测，否则会误判成服务挂载
  const url = /^https?:\/\//i.test(p) ? p : pageUrl(p,relpath);
  let opened=false;
  if(/^file:/i.test(url) && location.protocol!=='file:'){
    // http(s) 页面里浏览器安全策略禁止打开 file:// 链接：转为本地路径复制兜底
    let nat=url.slice(7); if(nat.startsWith('/')) nat=nat.slice(1);
    try{ nat=decodeURIComponent(nat); }catch(e){}
    cp(nat.replace(/\//g,'\\'),'浏览器禁止网页打开本地文件：路径已复制，粘到资源管理器即可；或用 start.bat 以服务模式打开本工作台');
  } else {
    opened=!!window.open(url,'_blank');
    if(!opened) cp(url,'新窗口被浏览器拦截，链接已复制');
  }
  const it = REC.find(x=>x.k===p+relpath);
  if(it){ it.t=Date.now(); } else { REC.unshift({k:p+relpath,n:arguments[2]||'',t:Date.now()}); REC=REC.slice(0,40); }
  jset(LS_REC,REC);
  return opened;
}''')

# ---------- F. go ----------
rep("F go",
    r'''function go(key){
  const d=ALL.find(x=>x.key===key); if(!d) return;
  openIt(d.root, d.main);
  toast('已打开：'+d.label);
}''',
    r'''async function go(key){
  const d=ALL.find(x=>x.key===key); if(!d) return;
  const ok = await openIt(d.root, d.main);
  if(ok) toast('已打开：'+d.label);
}''')

# ---------- G. drawer items: defer URL resolution to click time ----------
rep("G drawer CUR_ITEMS",
    r'''      const u=isCmd?cmd:(e.href||pageUrl(d.root,real));
      const i=CUR_ITEMS.push({u:u,n:e.name,f:full,cmd:cmd})-1;''',
    r'''      // do NOT freeze the URL here: the probe result may land after render,
      // so resolve it on click instead (openIt re-computes via pageUrl)
      const i=CUR_ITEMS.push({root:d.root,rel:real,href:e.href||'',n:e.name,f:full,cmd:cmd})-1;''')

# ---------- H. drawer delegate: route open through openIt ----------
rep("H drawer delegate",
    "  if(act==='open') visit(it.u,it.n);",
    '''  if(act==='open'){
    if(it.href) window.open(it.href,'_blank');   // 外部 http 链接直接开
    else openIt(it.root,it.rel);
  }''')

# ---------- I. README link in drawer meta: same deferral ----------
rep("I drawer readme link",
    '''    (d.mainDoc?'<a class="btn icon" target="_blank" href="'+pageUrl(d.root,d.mainDoc)+'" title="README">'+svg('file')+'</a>':'');''',
    '''    (d.mainDoc?'<a class="btn icon" data-doc="'+esc(d.mainDoc)+'" data-doc-root="'+esc(d.root)+'" title="README">'+svg('file')+'</a>':'');''')

rep("J drawer readme delegate",
    "document.getElementById('dClose').onclick=closeDrawer;",
    """document.getElementById('dMeta').addEventListener('click',ev=>{
  const a=ev.target.closest('[data-doc]'); if(!a) return;
  ev.preventDefault();
  openIt(a.getAttribute('data-doc-root'), a.getAttribute('data-doc'));
});
document.getElementById('dClose').onclick=closeDrawer;""")

# ---------- write + self-check ----------
io.open(TPL, "w", encoding="utf-8", newline="").write(t)
chk = io.open(TPL, encoding="utf-8", newline="").read()
assert "let SERVE_OK=false;" in chk, "probe missing"
assert '<div id="modebar"></div>' in chk, "modebar container missing"
assert chk.count("await SERVE_READY;") == 1, "openIt probe await missing"
assert "visit(it.u" not in chk, "old drawer delegate still present"
assert "pageUrl(d.root,d.mainDoc)" not in chk, "old readme link still present"
assert chk.count("<script>") == chk.count("</script>") == 1, "script tag imbalance"

print("--- patched %d spots, %d bytes ---" % (n_ok, len(chk)))
