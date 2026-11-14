#!/usr/bin/env python3
"""デザイン案の生成スクリプト。
本番の index.html から中身（文章・診断の仕組み）をそのまま借り、
<style> だけを案ごとに差し替えて teian/<記号>-<slug>.html を書き出す。
使い方:  python3 teian/gen.py
"""
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = (HERE.parent / "index.html").read_text(encoding="utf-8")

# ---------------------------------------------------------------- 共通の骨組み
BASE = r"""
  :root{--fs-h2:1.5rem;}
  @media(min-width:900px){:root{--fs-h2:2rem;}}
  *{margin:0;padding:0;box-sizing:border-box;}
  html{scroll-behavior:smooth;-webkit-text-size-adjust:100%;}
  body{font-family:var(--body-font);color:var(--body);background:var(--bg);line-height:1.8;font-size:16px;-webkit-font-smoothing:antialiased;}
  b{color:var(--ink);font-weight:700;}
  a{color:inherit;}

  header{background:var(--header-bg);backdrop-filter:blur(10px);-webkit-backdrop-filter:blur(10px);border-bottom:1px solid var(--line);position:sticky;top:0;z-index:50;}
  .header-inner{max-width:1120px;margin:0 auto;padding:12px 24px;display:flex;align-items:center;gap:16px;flex-wrap:wrap;}
  .site-title{font-family:var(--head-font);font-weight:var(--head-weight);font-size:1rem;letter-spacing:var(--head-ls);color:var(--ink);line-height:1.4;}
  .site-title .sub{display:block;font-size:.75rem;color:var(--muted);letter-spacing:.14em;font-family:var(--mono-font);font-weight:500;}
  nav.mode{margin-left:auto;display:flex;gap:4px;background:var(--seg-bg);padding:4px;border-radius:var(--r-btn);}
  .mode button{font-family:var(--body-font);font-size:.875rem;font-weight:700;min-height:44px;padding:6px 20px;border:none;background:transparent;color:var(--muted-strong);cursor:pointer;border-radius:var(--r-btn);transition:background .2s,color .2s;}
  .mode button:hover{color:var(--ink);}
  .mode button.active{background:var(--seg-on-bg);color:var(--seg-on-fg);box-shadow:var(--seg-shadow);}
  @media(max-width:720px){.site-title .sub{display:none;}.header-inner{padding:10px 16px;}.mode button{padding:6px 14px;}}

  .hero{max-width:1120px;margin:0 auto;padding:88px 24px 56px;display:grid;grid-template-columns:1fr;gap:20px;}
  .hero h1{font-family:var(--head-font);font-size:clamp(2rem,5.2vw,3.6rem);line-height:1.4;font-weight:var(--head-weight);letter-spacing:var(--head-ls);color:var(--ink);text-wrap:balance;}
  .hero h1 .kami{color:var(--kami-text);}
  .hero h1 .tab{color:var(--tab-text);}
  .hero h1 .kami,.hero h1 .tab,.verdict h3 .kami,.verdict h3 .tab{white-space:nowrap;}
  .hero p.lead{margin-top:20px;color:var(--muted-strong);max-width:42em;font-size:1rem;}
  .hero-seal{order:-1;justify-self:start;font-family:var(--mono-font);font-size:.75rem;font-weight:700;letter-spacing:.12em;color:var(--seal-fg);background:var(--seal-bg);padding:4px 16px;border-radius:9999px;}
  @media(max-width:720px){.hero{padding:48px 16px 32px;}}

  .wrap{max-width:1120px;margin:0 auto;padding:0 24px 96px;}
  @media(max-width:720px){.wrap{padding:0 16px 64px;}}
  .book-grid{display:grid;grid-template-columns:232px minmax(0,1fr);gap:56px;align-items:start;}
  @media(max-width:900px){.book-grid{grid-template-columns:minmax(0,1fr);gap:32px;}}

  .toc{position:sticky;top:88px;font-size:.875rem;}
  .toc .toc-label{font-family:var(--mono-font);letter-spacing:.16em;font-size:.75rem;font-weight:700;color:var(--muted);margin-bottom:12px;}
  .toc a{display:flex;align-items:center;min-height:44px;color:var(--muted-strong);text-decoration:none;padding:8px 12px;line-height:1.5;border-radius:var(--r-sm);transition:background .2s,color .2s;}
  .toc a:hover{color:var(--ink);background:var(--surface2);}
  .toc a.now{color:var(--ink);font-weight:700;background:var(--surface2);}
  @media(max-width:900px){.toc{position:static;display:flex;flex-wrap:wrap;gap:8px;padding-bottom:24px;border-bottom:1px solid var(--line);}.toc .toc-label{flex-basis:100%;margin-bottom:4px;}.toc a{background:var(--surface2);padding:8px 12px;font-size:.75rem;}}

  section.chapter{margin-bottom:96px;scroll-margin-top:96px;}
  .ch-head{display:flex;align-items:baseline;gap:16px;flex-wrap:wrap;padding-bottom:16px;margin-bottom:28px;border-bottom:1px solid var(--line);}
  .ch-num{font-family:var(--head-font);font-size:1.5rem;color:var(--accent);font-weight:var(--head-weight);line-height:1;}
  .ch-head h2{font-family:var(--head-font);font-size:var(--fs-h2);letter-spacing:var(--head-ls);font-weight:var(--head-weight);color:var(--ink);line-height:1.4;}
  .ch-head .en{margin-left:auto;font-family:var(--mono-font);font-size:.75rem;letter-spacing:.16em;color:var(--muted);text-transform:uppercase;}
  section.chapter h3{font-family:var(--head-font);font-weight:var(--head-weight);font-size:1.25rem;margin:44px 0 12px;letter-spacing:var(--head-ls);color:var(--ink);line-height:1.5;}
  section.chapter p{margin-bottom:16px;max-width:44em;}
  section.chapter ul{margin:0 0 16px 1.4em;max-width:42em;}
  section.chapter li{margin-bottom:8px;}

  .ref{font-size:.75rem;vertical-align:super;color:var(--link);text-decoration:none;font-weight:700;margin-left:1px;line-height:0;}
  .ref:hover{text-decoration:underline;}

  .duo{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin:24px 0 8px;}
  @media(max-width:720px){.duo{grid-template-columns:1fr;}}
  .card{border-radius:var(--r-card);background:var(--surface);border:var(--card-border);padding:24px;box-shadow:var(--card-shadow);}
  .card.kami{background:var(--card-kami-bg);}
  .card.tab{background:var(--card-tab-bg);}
  .card .badge{display:inline-block;font-size:.75rem;font-weight:700;letter-spacing:.08em;padding:4px 16px;border-radius:9999px;margin-bottom:12px;}
  .card.kami .badge{background:var(--kami);color:var(--on-kami);}
  .card.tab .badge{background:var(--tab);color:var(--on-tab);}
  .card h4{font-family:var(--head-font);font-weight:var(--head-weight);font-size:1.25rem;margin-bottom:8px;color:var(--ink);letter-spacing:var(--head-ls);}
  .card ul{margin-left:1.3em;font-size:.875rem;}
  .card li{margin-bottom:8px;}
  .card .minus li{color:var(--muted-strong);}
  .plusminus{font-family:var(--mono-font);font-size:.75rem;font-weight:700;letter-spacing:.1em;color:var(--muted-strong);margin:16px 0 6px;}

  .evidence{background:var(--ev-bg);border-radius:var(--r-card);padding:20px 24px;margin:20px 0;font-size:1rem;max-width:46em;border:var(--ev-border);}
  .evidence .ev-label{font-family:var(--mono-font);font-size:.75rem;letter-spacing:.16em;color:var(--ev-label);font-weight:700;margin-bottom:6px;}
  .evidence.guide{background:var(--guide-bg);}
  .evidence.guide .ev-label{color:var(--guide-label);}
  .evidence a{color:var(--link);}

  .principles{counter-reset:pr;list-style:none;margin:24px 0!important;max-width:46em;}
  .principles li{counter-increment:pr;position:relative;padding:16px 24px 16px 72px;margin-bottom:12px;background:var(--surface);border:var(--card-border);border-radius:var(--r-card);box-shadow:var(--card-shadow);}
  .principles li::before{content:counter(pr,decimal-leading-zero);position:absolute;left:24px;top:16px;font-family:var(--mono-font);font-size:1.25rem;color:var(--accent);font-weight:700;}

  .matrix-wrap{overflow-x:auto;}
  table.matrix{width:100%;border-collapse:separate;border-spacing:0;font-size:.875rem;margin:16px 0;border:1px solid var(--line);border-radius:var(--r-card);overflow:hidden;}
  .matrix th,.matrix td{border-bottom:1px solid var(--line);padding:12px 16px;text-align:left;vertical-align:top;}
  .matrix tbody tr:last-child td{border-bottom:none;}
  .matrix thead th{background:var(--th-bg);color:var(--th-fg);font-weight:700;font-size:.75rem;letter-spacing:.04em;}
  .pick{font-weight:700;white-space:nowrap;}
  .pick.kami{color:var(--kami-text);}
  .pick.tab{color:var(--tab-text);}
  .pick.both{color:var(--accent);}

  ol.bib{margin-left:1.6em;font-size:.875rem;color:var(--muted-strong);}
  ol.bib li{margin-bottom:12px;scroll-margin-top:100px;}
  ol.bib li:target{background:var(--ev-bg);border-radius:var(--r-sm);padding:6px 10px;}
  .pop{display:block;font-size:.75rem;color:var(--tab-text);}

  #view-shindan{display:none;padding-top:56px;}
  .sh-intro{max-width:46em;margin-bottom:40px;}
  .sh-intro h2{font-family:var(--head-font);font-weight:var(--head-weight);font-size:var(--fs-h2);margin-bottom:12px;letter-spacing:var(--head-ls);color:var(--ink);line-height:1.4;text-wrap:balance;}
  .sh-intro p{color:var(--muted-strong);}

  .q-block{background:var(--q-bg);border:var(--q-border);border-radius:var(--r-card);padding:32px;margin-bottom:16px;box-shadow:var(--card-shadow);}
  @media(max-width:560px){.q-block{padding:20px 16px;}}
  .q-head{display:flex;gap:12px;align-items:baseline;margin-bottom:6px;}
  .q-no{font-family:var(--mono-font);color:var(--accent);font-weight:700;font-size:.875rem;white-space:nowrap;}
  .q-title{font-family:var(--head-font);font-size:1.25rem;font-weight:var(--head-weight);color:var(--ink);letter-spacing:var(--head-ls);}
  .q-desc{font-size:.875rem;color:var(--muted-strong);margin-bottom:16px;}
  .opts{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:8px;margin-top:12px;}
  .opt{border:1.5px solid var(--opt-line);border-radius:var(--r-opt);padding:12px 16px;min-height:48px;cursor:pointer;background:var(--opt-bg);transition:border-color .15s,background .15s,color .15s;font-size:1rem;line-height:1.6;user-select:none;font-family:inherit;color:var(--ink);text-align:left;width:100%;display:block;}
  .opt:focus-visible,.mode button:focus-visible,.btn-main:focus-visible,.btn-sub:focus-visible{outline:3px solid var(--focus);outline-offset:2px;}
  .opt:hover{border-color:var(--ink);}
  .opt.sel{border-color:var(--sel-bg);background:var(--sel-bg);color:var(--sel-fg);}
  .opt .o-note{display:block;font-size:.75rem;color:var(--muted-strong);margin-top:4px;}
  .opt.sel .o-note{color:var(--sel-fg);opacity:.8;}

  .sh-actions{display:flex;gap:12px;align-items:center;margin:32px 0 64px;flex-wrap:wrap;}
  .btn-main{font-family:var(--body-font);font-size:1rem;font-weight:700;letter-spacing:.06em;background:var(--btn-bg);color:var(--btn-fg);border:none;min-height:52px;padding:12px 44px;border-radius:var(--r-btn);cursor:pointer;transition:background .2s,transform .2s;}
  .btn-main:hover{background:var(--btn-hover);}
  .btn-main:active{transform:scale(.98);}
  .btn-sub{font-family:var(--body-font);background:transparent;border:1.5px solid var(--opt-line);color:var(--ink);min-height:48px;padding:10px 24px;border-radius:var(--r-btn);cursor:pointer;font-size:.875rem;font-weight:700;transition:border-color .2s;}
  .btn-sub:hover{border-color:var(--ink);}
  .sh-warn{color:var(--warn);font-size:.875rem;font-weight:700;display:none;}

  #result{display:none;scroll-margin-top:96px;}
  .verdict{border-radius:var(--r-verdict);background:var(--v-bg);color:var(--v-fg);padding:40px;margin-bottom:32px;position:relative;overflow:hidden;}
  @media(max-width:560px){.verdict{padding:28px 20px;}}
  .verdict .v-label{font-family:var(--mono-font);font-size:.75rem;letter-spacing:.14em;color:var(--v-muted);margin-bottom:8px;font-weight:700;}
  .verdict h3{font-family:var(--head-font);font-weight:var(--head-weight);font-size:var(--fs-h2);line-height:1.4;margin-bottom:12px;color:var(--v-ink);letter-spacing:var(--head-ls);}
  .verdict h3 .kami{color:var(--v-kami);}
  .verdict h3 .tab{color:var(--v-tab);}
  .verdict p{max-width:44em;}
  .verdict b{color:var(--v-ink);}
  .meter{display:flex;height:20px;border-radius:9999px;overflow:hidden;margin:24px 0 8px;max-width:560px;background:var(--meter-track);gap:2px;}
  .meter .m-p{background:var(--v-kami-fill);transition:width .8s cubic-bezier(.2,.8,.2,1);}
  .meter .m-t{background:var(--v-tab-fill);transition:width .8s cubic-bezier(.2,.8,.2,1);}
  .meter-legend{display:flex;justify-content:space-between;max-width:560px;font-size:.75rem;color:var(--v-muted);}
  .meter-title{font-size:.875rem;font-weight:700;margin-top:24px;color:var(--v-ink);}
  .meter-title + .meter{margin-top:8px;}
  .meter-note{font-size:.875rem;color:var(--v-muted);margin-top:12px;}
  .verdict details{font-size:.875rem;color:var(--v-muted);margin-top:8px;max-width:44em;}
  .verdict summary{cursor:pointer;text-decoration:underline;text-underline-offset:3px;}

  .r-section{margin:40px 0;}
  .r-section h4{font-family:var(--head-font);font-weight:var(--head-weight);font-size:1.25rem;margin-bottom:16px;color:var(--ink);letter-spacing:var(--head-ls);}
  .reason-grid{display:grid;grid-template-columns:1fr 1fr;gap:12px;}
  @media(max-width:720px){.reason-grid{grid-template-columns:1fr;}}
  .reason{border:var(--card-border);border-radius:var(--r-card);padding:20px;background:var(--surface);font-size:.875rem;box-shadow:var(--card-shadow);}
  .reason.r-kami{background:var(--card-kami-bg);}
  .reason.r-tab{background:var(--card-tab-bg);}
  .reason .r-side,.tag-kami,.tag-tab,.tag-both{font-size:.75rem;font-weight:700;letter-spacing:.06em;padding:4px 12px;border-radius:9999px;white-space:nowrap;display:inline-block;}
  .reason .r-side{margin-bottom:8px;}
  .reason.r-kami .r-side,.tag-kami{background:var(--kami);color:var(--on-kami);}
  .reason.r-tab .r-side,.tag-tab{background:var(--tab);color:var(--on-tab);}
  .reason.r-both .r-side,.tag-both{background:var(--both-bg);color:var(--both-fg);}
  .caution{background:var(--caution-bg);border-radius:var(--r-card);padding:16px 20px;margin-bottom:8px;font-size:.875rem;border:var(--ev-border);}
  .recipe{background:var(--surface2);border-radius:var(--r-card);padding:24px;font-size:1rem;}
  .recipe-lead{font-size:.875rem;color:var(--muted-strong);margin-bottom:16px;}
  .recipe .step{display:flex;gap:12px;padding:10px 0;align-items:baseline;border-top:1px solid var(--line);}
  .recipe .step b{white-space:nowrap;min-width:5.5em;}
  @media(max-width:560px){.recipe .step{flex-wrap:wrap;gap:4px 10px;}.recipe .step span:last-child{flex-basis:100%;}.recipe .step b{min-width:0;}}
  .recipe-notes{margin:16px 0 0 1.2em;font-size:.875rem;color:var(--muted-strong);}
  .recipe-notes li{margin-bottom:4px;}

  footer{border-top:1px solid var(--line);padding:32px 24px 56px;text-align:center;font-size:.75rem;color:var(--muted);letter-spacing:.04em;background:var(--footer-bg);}

  @media (prefers-reduced-motion:reduce){html{scroll-behavior:auto;}*{transition:none!important;}}
  @media print{
    header,.mode,.sh-actions,.toc{display:none!important;}
    body{background:#fff;}
    .book-grid{grid-template-columns:1fr;}
  }
"""

# ---------------------------------------------------------------- 案ごとの型
VARIANTS = [
    dict(
        key="a", slug="claude", name="案A — あたたかい紙色（Claude型）",
        fonts="family=Zen+Old+Mincho:wght@500;700&family=Noto+Sans+JP:wght@400;500;700&family=IBM+Plex+Mono:wght@500;600",
        css=r"""
  /* 型: awesome-design-md / claude。クリーム色の紙面・明朝の見出し・テラコッタの差し色・濃い色の結果カード */
  :root{
    --bg:#faf9f5;            /* canvas */
    --surface:#efe9de;       /* surface-card */
    --surface2:#f5f0e8;      /* surface-soft */
    --ink:#141413; --body:#3d3d3a; --muted-strong:#5e5c56; --muted:#6c6a64;
    --line:#e6dfd8;          /* hairline */
    --kami:#a9583e;          /* primary-active（文字が読める濃さ） */
    --kami-text:#a9583e; --on-kami:#ffffff;
    --tab:#2f7f70;           /* accent-teal #5db8a6 を文字用に濃くしたもの */
    --tab-text:#2f7f70; --on-tab:#ffffff;
    --accent:#cc785c;        /* primary */
    --link:#a9583e;
    --card-kami-bg:#efe9de; --card-tab-bg:#efe9de;
    --card-border:none; --card-shadow:none;
    --ev-bg:#f5f0e8; --ev-border:1px solid #e6dfd8; --ev-label:#a9583e;
    --guide-bg:#f5f0e8; --guide-label:#2f7f70;
    --th-bg:#181715; --th-fg:#faf9f5;
    --q-bg:#ffffff; --q-border:1px solid #e6dfd8;
    --opt-bg:#faf9f5; --opt-line:#d9d1c6; --sel-bg:#141413; --sel-fg:#faf9f5;
    --btn-bg:#a9583e; --btn-hover:#8f4a34; --btn-fg:#ffffff;
    --seg-bg:#efe9de; --seg-on-bg:#141413; --seg-on-fg:#faf9f5; --seg-shadow:none;
    --seal-bg:#efe9de; --seal-fg:#a9583e;
    --v-bg:#181715; --v-fg:#d6d2c9; --v-ink:#faf9f5; --v-muted:#a09d96;
    --v-kami:#e09a80; --v-tab:#5db8a6; --v-kami-fill:#cc785c; --v-tab-fill:#5db8a6; --meter-track:#252320;
    --both-bg:#e8e0d2; --both-fg:#5e4a1c;
    --caution-bg:#f8e9e2; --warn:#c64545; --focus:#cc785c;
    --header-bg:rgba(250,249,245,.9); --footer-bg:transparent;
    --r-sm:6px; --r-card:12px; --r-opt:8px; --r-btn:8px; --r-verdict:16px;
    --head-font:"Zen Old Mincho","Hiragino Mincho ProN","Yu Mincho",serif;
    --body-font:"Noto Sans JP","Hiragino Kaku Gothic ProN","Yu Gothic",sans-serif;
    --mono-font:"IBM Plex Mono","Noto Sans JP",monospace;
    --head-weight:500; --head-ls:-.01em;
  }
  .hero h1{font-weight:500;}
  .card.kami{box-shadow:inset 0 3px 0 #cc785c;}
  .card.tab{box-shadow:inset 0 3px 0 #5db8a6;}
"""),
    dict(
        key="b", slug="notion", name="案B — やさしい色カード（Notion型）",
        fonts="family=Noto+Sans+JP:wght@400;500;700;900&family=IBM+Plex+Mono:wght@500;600",
        css=r"""
  /* 型: awesome-design-md / notion。白い紙面・太いゴシック見出し・淡い色つきカード・紫のボタン */
  :root{
    --bg:#ffffff;            /* canvas */
    --surface:#f6f5f4;       /* surface */
    --surface2:#f6f5f4;
    --ink:#1a1a1a; --body:#37352f; --muted-strong:#5d5b54; --muted:#787671;
    --line:#e5e3df;          /* hairline */
    --kami:#dd5b00;          /* brand-orange */
    --kami-text:#b34a00; --on-kami:#ffffff;
    --tab:#2a9d99;           /* brand-teal */
    --tab-text:#1d7774; --on-tab:#ffffff;
    --accent:#5645d4;        /* primary */
    --link:#0075de;          /* link-blue */
    --card-kami-bg:#ffe8d4;  /* card-tint-peach */
    --card-tab-bg:#d9f3e1;   /* card-tint-mint */
    --card-border:none; --card-shadow:none;
    --ev-bg:#fef7d6;         /* card-tint-yellow */
    --ev-border:none; --ev-label:#793400;
    --guide-bg:#e6e0f5;      /* card-tint-lavender */
    --guide-label:#3a2a99;
    --th-bg:#f6f5f4; --th-fg:#1a1a1a;
    --q-bg:#ffffff; --q-border:1px solid #e5e3df;
    --opt-bg:#ffffff; --opt-line:#c8c4be; --sel-bg:#5645d4; --sel-fg:#ffffff;
    --btn-bg:#5645d4; --btn-hover:#4534b3; --btn-fg:#ffffff;
    --seg-bg:#f6f5f4; --seg-on-bg:#ffffff; --seg-on-fg:#1a1a1a; --seg-shadow:0 1px 3px rgba(0,0,0,.12);
    --seal-bg:#e6e0f5; --seal-fg:#3a2a99;
    --v-bg:#dcecfa;          /* card-tint-sky */
    --v-fg:#37352f; --v-ink:#0a1530; --v-muted:#5d5b54;
    --v-kami:#b34a00; --v-tab:#1d7774; --v-kami-fill:#dd5b00; --v-tab-fill:#2a9d99; --meter-track:#ffffff;
    --both-bg:#f9e79f; --both-fg:#523410;
    --caution-bg:#fde0ec;    /* card-tint-rose */
    --warn:#e03131; --focus:#5645d4;
    --header-bg:rgba(255,255,255,.9); --footer-bg:#fafaf9;
    --r-sm:6px; --r-card:12px; --r-opt:8px; --r-btn:8px; --r-verdict:20px;
    --head-font:"Noto Sans JP","Hiragino Kaku Gothic ProN","Yu Gothic",sans-serif;
    --body-font:"Noto Sans JP","Hiragino Kaku Gothic ProN","Yu Gothic",sans-serif;
    --mono-font:"IBM Plex Mono","Noto Sans JP",monospace;
    --head-weight:700; --head-ls:-.02em;
  }
  .hero h1{font-weight:900;}
  .ch-head{border-bottom:none;padding-bottom:0;}
  .ch-num{display:inline-grid;place-items:center;width:44px;height:44px;border-radius:12px;background:#e6e0f5;color:#3a2a99;font-size:1.25rem;align-self:center;}
  .q-no{background:#e6e0f5;color:#3a2a99;padding:2px 10px;border-radius:6px;font-size:.75rem;}
"""),
    dict(
        key="c", slug="apple", name="案C — 白と余白（Apple型）",
        fonts="family=Noto+Sans+JP:wght@400;500;700&family=Outfit:wght@500;600",
        css=r"""
  /* 型: awesome-design-md / apple。白と薄灰の面・黒い看板・青い丸ボタン1色・影も枠もないカード */
  :root{
    --bg:#ffffff;            /* canvas */
    --surface:#f5f5f7;       /* canvas-parchment */
    --surface2:#f5f5f7;
    --ink:#1d1d1f; --body:#1d1d1f; --muted-strong:#515154; --muted:#6e6e73;
    --line:#e0e0e0;          /* hairline */
    --kami:#1d1d1f;          /* 紙 = 墨（ink） */
    --kami-text:#1d1d1f; --on-kami:#ffffff;
    --tab:#0066cc;           /* タブレット = primary の青 */
    --tab-text:#0066cc; --on-tab:#ffffff;
    --accent:#6e6e73;
    --link:#0066cc;
    --card-kami-bg:#f5f5f7; --card-tab-bg:#f5f5f7;
    --card-border:none; --card-shadow:none;
    --ev-bg:#f5f5f7; --ev-border:none; --ev-label:#6e6e73;
    --guide-bg:#f5f5f7; --guide-label:#0066cc;
    --th-bg:#f5f5f7; --th-fg:#1d1d1f;
    --q-bg:#f5f5f7; --q-border:none;
    --opt-bg:#ffffff; --opt-line:#d2d2d7; --sel-bg:#0071e3; --sel-fg:#ffffff;
    --btn-bg:#0071e3; --btn-hover:#0066cc; --btn-fg:#ffffff;
    --seg-bg:#f5f5f7; --seg-on-bg:#1d1d1f; --seg-on-fg:#ffffff; --seg-shadow:none;
    --seal-bg:#272729; --seal-fg:#f5f5f7;
    --v-bg:#000000; --v-fg:#d2d2d7; --v-ink:#ffffff; --v-muted:#a1a1a6;
    --v-kami:#ffffff; --v-tab:#2997ff; --v-kami-fill:#f5f5f7; --v-tab-fill:#2997ff; --meter-track:#272729;
    --both-bg:#e8e8ed; --both-fg:#1d1d1f;
    --caution-bg:#f5f5f7; --warn:#b3261e; --focus:#0071e3;
    --header-bg:rgba(255,255,255,.8); --footer-bg:#f5f5f7;
    --r-sm:8px; --r-card:18px; --r-opt:11px; --r-btn:9999px; --r-verdict:18px;
    --head-font:"Outfit","Noto Sans JP","Hiragino Kaku Gothic ProN",sans-serif;
    --body-font:"Noto Sans JP","Hiragino Kaku Gothic ProN","Yu Gothic",sans-serif;
    --mono-font:"Outfit","Noto Sans JP",sans-serif;
    --head-weight:700; --head-ls:-.02em;
  }
  /* 看板は画面幅いっぱいの黒い面 */
  .hero{max-width:none;background:#000;padding:120px 24px 104px;justify-items:center;text-align:center;margin-bottom:80px;}
  .hero > div:first-child{max-width:900px;}
  .hero h1{color:#fff;}
  .hero h1 .kami{color:#fff;}
  .hero h1 .tab{color:#2997ff;}
  .hero p.lead{color:#a1a1a6;margin-left:auto;margin-right:auto;}
  .hero-seal{justify-self:center;}
  @media(max-width:720px){.hero{padding:72px 16px 64px;margin-bottom:48px;}}
  .ch-head{border-bottom:none;padding-bottom:0;}
  .ch-head h2{font-size:clamp(1.7rem,3.6vw,2.5rem);}
  section.chapter{margin-bottom:120px;}
  .card{padding:32px;}
  .sh-intro{text-align:center;margin-left:auto;margin-right:auto;}
"""),
    dict(
        key="d", slug="figma", name="案D — 白黒＋色ブロック（Figma型）",
        fonts="family=Zen+Kaku+Gothic+New:wght@400;500;700;900&family=IBM+Plex+Mono:wght@500;600",
        css=r"""
  /* 型: awesome-design-md / figma。白黒の骨組み・黒い丸ボタン・等幅の小見出し・大きな色ブロック */
  :root{
    --bg:#ffffff;            /* canvas */
    --surface:#f7f7f5;       /* surface-soft */
    --surface2:#f7f7f5;
    --ink:#000000; --body:#1c1c1c; --muted-strong:#4a4a4a; --muted:#6b6b6b;
    --line:#e6e6e6;          /* hairline */
    --kami:#f3c9b6;          /* block-coral */
    --kami-text:#000000; --on-kami:#000000;
    --tab:#c8e6cd;           /* block-mint */
    --tab-text:#000000; --on-tab:#000000;
    --accent:#000000;
    --link:#000000;
    --card-kami-bg:#f3c9b6; --card-tab-bg:#c8e6cd;
    --card-border:none; --card-shadow:none;
    --ev-bg:#f4ecd6;         /* block-cream */
    --ev-border:none; --ev-label:#000000;
    --guide-bg:#c5b0f4;      /* block-lilac */
    --guide-label:#000000;
    --th-bg:#000000; --th-fg:#ffffff;
    --q-bg:#ffffff; --q-border:1px solid #e6e6e6;
    --opt-bg:#ffffff; --opt-line:#c9c9c9; --sel-bg:#000000; --sel-fg:#ffffff;
    --btn-bg:#000000; --btn-hover:#2b2b2b; --btn-fg:#ffffff;
    --seg-bg:#f1f1f1; --seg-on-bg:#000000; --seg-on-fg:#ffffff; --seg-shadow:none;
    --seal-bg:#000000; --seal-fg:#ffffff;
    --v-bg:#1f1d3d;          /* block-navy */
    --v-fg:#dcdbe8; --v-ink:#ffffff; --v-muted:#b4b2cc;
    --v-kami:#000000; --v-tab:#000000; --v-kami-fill:#f3c9b6; --v-tab-fill:#c8e6cd; --meter-track:#35325e;
    --both-bg:#dceeb1; --both-fg:#000000;
    --caution-bg:#efd4d4;    /* block-pink */
    --warn:#c2185b; --focus:#ff3d8b;
    --header-bg:rgba(255,255,255,.92); --footer-bg:transparent;
    --r-sm:6px; --r-card:24px; --r-opt:8px; --r-btn:50px; --r-verdict:32px;
    --head-font:"Zen Kaku Gothic New","Hiragino Kaku Gothic ProN","Yu Gothic",sans-serif;
    --body-font:"Zen Kaku Gothic New","Hiragino Kaku Gothic ProN","Yu Gothic",sans-serif;
    --mono-font:"IBM Plex Mono","Zen Kaku Gothic New",monospace;
    --head-weight:700; --head-ls:-.02em;
  }
  body{font-weight:500;}
  /* 看板はライム色の大きなブロック */
  .hero{max-width:1072px;background:#dceeb1;border-radius:32px;padding:72px 56px 64px;margin:24px auto 72px;}
  @media(max-width:1120px){.hero{margin-left:16px;margin-right:16px;}}
  @media(max-width:720px){.hero{padding:40px 24px;border-radius:24px;margin-bottom:40px;}}
  .hero p.lead{color:#1c1c1c;}
  /* 「紙」「タブレット」は色の札にする（文字色は黒のまま） */
  .hero h1 .kami,.hero h1 .tab,.verdict h3 .kami,.verdict h3 .tab{padding:0 .18em;border-radius:.2em;white-space:nowrap;}
  .hero h1 .kami{background:#f3c9b6;}
  .hero h1 .tab{background:#ffffff;}
  .verdict h3 .kami{background:#f3c9b6;}
  .verdict h3 .tab{background:#c8e6cd;}
  .pick.kami,.pick.tab,.pick.both{padding:1px 10px;border-radius:9999px;}
  .pick.kami{background:#f3c9b6;}
  .pick.tab{background:#c8e6cd;}
  .pick.both{background:#dceeb1;}
  .ch-head{border-bottom:2px solid #000;}
  .ch-num{font-family:var(--mono-font);font-size:.875rem;border:1.5px solid #000;border-radius:9999px;padding:4px 12px;align-self:center;}
  .card .badge,.reason .r-side{background:#000!important;color:#fff!important;}
  .ref{text-decoration:underline;text-underline-offset:2px;}
  .pop{color:#4a4a4a;}
"""),
    dict(
        key="e", slug="wired", name="案E — 新聞・雑誌（WIRED型）",
        fonts="family=Zen+Old+Mincho:wght@700;900&family=Noto+Serif+JP:wght@400;700&family=Noto+Sans+JP:wght@500;700",
        css=r"""
  /* 型: awesome-design-md / wired。白黒の紙面・太い明朝の見出し・角のないボタン・罫線で区切る・色はリンクの青だけ */
  :root{
    --bg:#ffffff;            /* canvas */
    --surface:#ffffff;
    --surface2:#f5f5f5;      /* canvas-soft */
    --ink:#000000; --body:#1a1a1a; --muted-strong:#4d4d4d; --muted:#6b6b6b;
    --line:#e0e0e0;          /* hairline */
    --kami:#000000; --kami-text:#000000; --on-kami:#ffffff;
    --tab:#057dbc;           /* link */
    --tab-text:#04679b; --on-tab:#ffffff;
    --accent:#000000;
    --link:#04679b;
    --card-kami-bg:#ffffff; --card-tab-bg:#ffffff;
    --card-border:none; --card-shadow:none;
    --ev-bg:#f5f5f5; --ev-border:none; --ev-label:#000000;
    --guide-bg:#f5f5f5; --guide-label:#04679b;
    --th-bg:#000000; --th-fg:#ffffff;
    --q-bg:#ffffff; --q-border:none;
    --opt-bg:#ffffff; --opt-line:#000000; --sel-bg:#000000; --sel-fg:#ffffff;
    --btn-bg:#000000; --btn-hover:#333333; --btn-fg:#ffffff;
    --seg-bg:transparent; --seg-on-bg:#ffffff; --seg-on-fg:#000000; --seg-shadow:none;
    --seal-bg:transparent; --seal-fg:#000000;
    --v-bg:#000000; --v-fg:#d6d6d6; --v-ink:#ffffff; --v-muted:#a8a8a8;
    --v-kami:#ffffff; --v-tab:#4fb3e8; --v-kami-fill:#ffffff; --v-tab-fill:#057dbc; --meter-track:#333333;
    --both-bg:#e0e0e0; --both-fg:#000000;
    --caution-bg:#f5f5f5; --warn:#b00020; --focus:#057dbc;
    --header-bg:#000000; --footer-bg:#000000;
    --r-sm:0px; --r-card:0px; --r-opt:0px; --r-btn:0px; --r-verdict:0px;
    --head-font:"Zen Old Mincho","Hiragino Mincho ProN","Yu Mincho",serif;
    --body-font:"Noto Serif JP","Hiragino Mincho ProN","Yu Mincho",serif;
    --mono-font:"Noto Sans JP","Hiragino Kaku Gothic ProN",sans-serif;
    --head-weight:900; --head-ls:0;
  }
  /* 黒い帯の題字（マストヘッド） */
  header{border-bottom:none;}
  .site-title{color:#fff;}
  .site-title .sub{color:#a8a8a8;}
  nav.mode{background:transparent;padding:0;}
  .mode button{color:#bdbdbd;font-family:var(--mono-font);}
  .mode button:hover{color:#fff;}
  .mode button.active{background:#fff;color:#000;}
  .mode button:focus-visible{outline-color:#fff;}
  /* 看板は太い罫線ではさむ */
  .hero{border-top:6px solid #000;border-bottom:1px solid #000;margin-top:32px;padding:48px 24px 40px;max-width:1072px;}
  @media(max-width:1120px){.hero{margin-left:16px;margin-right:16px;padding-left:0;padding-right:0;}}
  .hero h1{font-size:clamp(2.1rem,5.6vw,4rem);line-height:1.3;}
  .hero h1 .kami{color:#000;}
  .hero-seal{padding:0;border-bottom:2px solid #000;border-radius:0;font-family:var(--mono-font);letter-spacing:.2em;}
  .hero p.lead{font-size:1rem;}
  .ch-head{border-bottom:none;border-top:3px solid #000;padding-top:14px;}
  .ch-num{font-size:2.6rem;}
  .ch-head .en{font-family:var(--mono-font);}
  .toc a{border-radius:0;}
  .toc a.now{background:transparent;border-left:3px solid #000;}
  .card{border-top:4px solid #000;border-bottom:1px solid #e0e0e0;padding:16px 4px 20px;}
  .card.tab{border-top-color:#057dbc;}
  .card .badge,.reason .r-side,.tag-kami,.tag-tab,.tag-both{border-radius:0;font-family:var(--mono-font);}
  .principles li{border-top:1px solid #000;padding-left:72px;}
  .principles li::before{font-family:var(--head-font);font-size:1.6rem;top:10px;}
  .q-block{border-top:3px solid #000;padding:24px 0;}
  .q-no{font-family:var(--head-font);font-size:1.4rem;}
  .reason{border-top:3px solid #000;}
  .reason.r-tab{border-top-color:#057dbc;}
  .reason.r-kami,.reason.r-tab{background:#fff;}
  .caution{border-left:4px solid #b00020;}
  .btn-main,.btn-sub,.mode button,.opt{font-family:var(--mono-font);}
  .verdict h3 .kami{text-decoration:underline;text-decoration-thickness:3px;text-underline-offset:6px;}
  footer{color:#a8a8a8;border-top:none;}
  .meter{border:1px solid #666;}
"""),
    dict(
        key="f", slug="miro", name="案F — 黄色い付箋の掲示板（Miro型）",
        fonts="family=M+PLUS+Rounded+1c:wght@400;500;700;800&family=Outfit:wght@600",
        css=r"""
  /* 型: awesome-design-md / miro。白い画面に黄色の看板・付箋のような淡い色カード・青いボタン。書体は親しみの丸ゴシックに置き換え */
  :root{
    --bg:#ffffff;            /* canvas */
    --surface:#f7f8fa;       /* surface */
    --surface2:#f7f8fa;
    --ink:#1c1c1e; --body:#1c1c1e; --muted-strong:#555a6a; --muted:#555a6a;
    --line:#e0e2e8;          /* hairline */
    --kami:#ff9999;          /* brand-coral */
    --kami-text:#600000; --on-kami:#600000;
    --tab:#0fbcb0;           /* brand-teal */
    --tab-text:#187574; --on-tab:#05302e;
    --accent:#2a41b6;        /* blue-pressed（文字に使う青はこれ1色） */
    --link:#2a41b6;          /* blue-pressed（文字が読める濃さ） */
    --card-kami-bg:#ffc6c6;  /* coral-light */
    --card-tab-bg:#c3faf5;   /* teal-light */
    --card-border:none; --card-shadow:0 2px 0 rgba(5,0,56,.08),0 8px 18px rgba(5,0,56,.06);
    --ev-bg:#fff4c4;         /* yellow-light */
    --ev-border:none; --ev-label:#1c1c1e;
    --guide-bg:#f7f8fa; --guide-label:#2a41b6;
    --th-bg:#050038; --th-fg:#ffffff;
    --q-bg:#ffffff; --q-border:1px solid #e0e2e8;
    --opt-bg:#ffffff; --opt-line:#c7cad5; --sel-bg:#4262ff; --sel-fg:#ffffff;
    --btn-bg:#4262ff; --btn-hover:#2a41b6; --btn-fg:#ffffff;
    --seg-bg:#f7f8fa; --seg-on-bg:#1c1c1e; --seg-on-fg:#ffffff; --seg-shadow:none;
    --seal-bg:#1c1c1e; --seal-fg:#ffd02f;
    --v-bg:#050038;          /* ink-deep */
    --v-fg:#ffffff; --v-ink:#ffffff; --v-muted:#a5a8b5;
    --v-kami:#ff9999; --v-tab:#0fbcb0; --v-kami-fill:#ff9999; --v-tab-fill:#0fbcb0; --meter-track:#24205a;
    --both-bg:#ffd02f; --both-fg:#1c1c1e;
    --caution-bg:#fde0f0;    /* rose-light */
    --warn:#c21f1f; --focus:#4262ff;
    --header-bg:rgba(255,255,255,.92); --footer-bg:#1c1c1e;
    --r-sm:8px; --r-card:16px; --r-opt:12px; --r-btn:9999px; --r-verdict:28px;
    --head-font:"M PLUS Rounded 1c","Hiragino Maru Gothic ProN",sans-serif;
    --body-font:"M PLUS Rounded 1c","Hiragino Maru Gothic ProN",sans-serif;
    --mono-font:"Outfit","M PLUS Rounded 1c",sans-serif;
    --head-weight:800; --head-ls:-.01em;
  }
  body{font-weight:500;}
  /* 看板は黄色い大きな面。うしろに点線の方眼（ホワイトボードの空気） */
  .hero{max-width:1072px;background:#ffd02f radial-gradient(rgba(28,28,30,.12) 1.2px,transparent 1.2px) 0 0/22px 22px;border-radius:32px;padding:72px 56px 64px;margin:24px auto 72px;}
  @media(max-width:1120px){.hero{margin-left:16px;margin-right:16px;}}
  @media(max-width:720px){.hero{padding:40px 24px;border-radius:24px;margin-bottom:40px;}}
  .hero h1 .kami{color:#600000;}
  .hero h1 .tab{color:#187574;}
  .hero h1 .kami,.hero h1 .tab{background:#fff;padding:0 8px;border-radius:8px;white-space:nowrap;}
  .hero p.lead{color:#1c1c1e;}
  /* 付箋らしく、少しだけ傾ける */
  .duo .card.kami{transform:rotate(-.6deg);}
  .duo .card.tab{transform:rotate(.6deg);}
  .reason-grid .reason:nth-child(odd){transform:rotate(-.4deg);}
  .reason-grid .reason:nth-child(even){transform:rotate(.4deg);}
  .card.kami .badge,.reason.r-kami .r-side,.tag-kami{background:#600000;color:#fff;}
  .card.tab .badge,.reason.r-tab .r-side,.tag-tab{background:#187574;color:#fff;}
  .ch-head{border-bottom:none;}
  .ch-num{display:inline-grid;place-items:center;width:48px;height:48px;border-radius:50%;background:#ffd02f;color:#1c1c1e;font-size:1.25rem;align-self:center;}
  .q-no{background:#ffd02f;color:#1c1c1e;padding:4px 12px;border-radius:9999px;font-size:.875rem;}
  .principles li::before{color:#2a41b6;}
  .verdict h3 .kami,.verdict h3 .tab{color:#050038;padding:0 8px;border-radius:8px;white-space:nowrap;}
  .verdict h3 .kami{background:#ff9999;}
  .verdict h3 .tab{background:#0fbcb0;}
  footer{color:#a5a8b5;border-top:none;}
  @media (prefers-reduced-motion:reduce){.duo .card,.reason{transform:none!important;}}
  /* 印刷：背景色が落ちても読めるよう、結果カードは白地に濃い文字へ */
  @media print{
    :root{--v-bg:#fff;--v-fg:#2c2c34;--v-ink:#050038;--v-muted:#555a6a;--meter-track:#eee;}
    .verdict{border:2px solid #050038;}
    .hero{background:#fff;border:2px solid #1c1c1e;}
    .duo .card,.reason{transform:none!important;}
    *{-webkit-print-color-adjust:exact;print-color-adjust:exact;}
  }
"""),
    dict(
        key="g", slug="spotify", name="案G — 夜のダークモード（Spotify型）",
        fonts="family=Noto+Sans+JP:wght@400;500;700;900",
        css=r"""
  /* 型: awesome-design-md / spotify。ほぼ黒の画面・明るさの段差で面を分ける・緑の丸いボタン・太いゴシック */
  :root{
    color-scheme:dark;
    --bg:#121212;            /* near black */
    --surface:#181818;       /* dark surface */
    --surface2:#1f1f1f;      /* mid dark */
    --ink:#ffffff; --body:#cbcbcb; --muted-strong:#b3b3b3; --muted:#a0a0a0;
    --line:#2a2a2a;
    --kami:#ffa42b;          /* warning orange（紙 = だいだい） */
    --kami-text:#ffa42b; --on-kami:#121212;
    --tab:#539df5;           /* announcement blue（タブレット = 青） */
    --tab-text:#7db5f7; --on-tab:#121212;
    --accent:#1ed760;        /* Spotify Green */
    --link:#1ed760;
    --card-kami-bg:#181818; --card-tab-bg:#181818;
    --card-border:none; --card-shadow:none;
    --ev-bg:#1f1f1f; --ev-border:none; --ev-label:#1ed760;
    --guide-bg:#1f1f1f; --guide-label:#7db5f7;
    --th-bg:#252525; --th-fg:#ffffff;
    --q-bg:#181818; --q-border:none;
    --opt-bg:#1f1f1f; --opt-line:#4d4d4d; --sel-bg:#1ed760; --sel-fg:#000000;
    --btn-bg:#1ed760; --btn-hover:#3be477; --btn-fg:#000000;
    --seg-bg:#1f1f1f; --seg-on-bg:#ffffff; --seg-on-fg:#000000; --seg-shadow:none;
    --seal-bg:#1ed760; --seal-fg:#000000;
    --v-bg:linear-gradient(180deg,#3d3d3d 0%,#181818 70%); --v-fg:#cbcbcb; --v-ink:#ffffff; --v-muted:#b3b3b3;
    --v-kami:#ffa42b; --v-tab:#7db5f7; --v-kami-fill:#ffa42b; --v-tab-fill:#539df5; --meter-track:#4d4d4d;
    --both-bg:#1ed760; --both-fg:#000000;
    --caution-bg:#2a1c1e; --warn:#f3727f; --focus:#ffffff;
    --header-bg:rgba(18,18,18,.92); --footer-bg:#000000;
    --r-sm:6px; --r-card:8px; --r-opt:8px; --r-btn:9999px; --r-verdict:8px;
    --head-font:"Noto Sans JP","Hiragino Kaku Gothic ProN",sans-serif;
    --body-font:"Noto Sans JP","Hiragino Kaku Gothic ProN",sans-serif;
    --mono-font:"Noto Sans JP","Hiragino Kaku Gothic ProN",sans-serif;
    --head-weight:900; --head-ls:-.02em;
  }
  .verdict{background:var(--v-bg);}
  /* 看板はアルバムの色のように、上から色がにじむ */
  .hero{max-width:none;background:linear-gradient(180deg,#1e4d7a 0%,#121212 100%);padding:112px max(24px,calc((100% - 1072px)/2)) 64px;margin-bottom:48px;}
  @media(max-width:720px){.hero{padding:64px 16px 40px;}}
  .hero p.lead{color:#cbcbcb;}
  .ch-head{border-bottom:none;}
  .ch-num{color:#1ed760;}
  .toc a.now{background:#1f1f1f;color:#fff;}
  .card,.reason{transition:background .2s;}
  .card:hover,.reason:hover{background:#252525;}
  .opt:hover{border-color:#ffffff;}
  .principles li{background:#181818;}
  .principles li::before{color:#1ed760;}
  .recipe{background:#181818;}
  .caution{border-left:4px solid #f3727f;}
  ol.bib li:target{background:#1f1f1f;}
  .matrix tbody tr:nth-child(even) td{background:#161616;}
  footer{border-top:none;color:#a0a0a0;}
  @media print{
    :root{--bg:#fff;--surface:#fff;--surface2:#f4f4f4;--ink:#000;--body:#222;--muted-strong:#444;--muted:#555;--line:#ccc;
      --kami-text:#a35a00;--tab-text:#1d5fa8;--th-bg:#eee;--th-fg:#000;--q-bg:#fff;--opt-bg:#fff;
      --v-bg:#fff;--v-fg:#222;--v-ink:#000;--v-muted:#444;--ev-bg:#f4f4f4;--caution-bg:#fbeaec;--card-kami-bg:#fff;--card-tab-bg:#fff;}
    .hero{background:#fff;}
    .verdict{border:2px solid #000;}
  }
"""),
]

# ---------------------------------------------------------------- 書き出し
STYLE_RE = re.compile(r'(?:<link rel="preconnect"[^>]*>\n)*(?:<link href="https://fonts\.googleapis\.com[^>]*>\n)?<style>.*?</style>', re.S)


def build(v, out=None):
    head = (
        '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
        f'<link href="https://fonts.googleapis.com/css2?{v["fonts"]}&display=swap" rel="stylesheet">\n'
        f"<style>{BASE}\n  /* ===== ここから下が案ごとの型 ===== */{v['css']}</style>"
    )
    html, n = STYLE_RE.subn(lambda m: head, SRC, count=1)
    assert n == 1, "styleブロックが見つからない"
    out = out or HERE / f'{v["key"]}-{v["slug"]}.html'
    out.write_text(html, encoding="utf-8")
    return out


INDEX_CARDS = [
    ("../index.html", "いまの見た目", "和紙色の地に明朝体の見出し、朱色と青緑。", "落ち着いた「読みもの」の空気。", "比べるための基準。"),
    ("e-wired.html", "案E — 新聞・雑誌 【新】", "元にした型：WIRED。白黒だけの紙面に太い明朝体、太い罫線で区切る。角はすべて四角。", "色はタブレットの青ひとつ。上の題字は黒い帯。", "向き：研究にもとづく「読みもの」として格調高く見せたい。"),
    ("f-miro.html", "案F — 黄色い付箋の掲示板 【新】", "元にした型：Miro。黄色い看板に点の方眼、付箋のように少し傾いた色カード。", "書体は丸ゴシック。ボタンは青。", "向き：校内研修や職員室の掲示物のように、明るく親しみやすくしたい。"),
    ("g-spotify.html", "案G — 夜のダークモード 【新】", "元にした型：Spotify。ほぼ黒の画面で、紙＝だいだい、タブレット＝青、ボタンは緑。", "印刷するときだけ白い紙面に切り替わる。", "向き：いちばん「アプリっぽい」。夜にスマホで読む人に。"),
    ("a-claude.html", "案A — あたたかい紙色", "元にした型：Claude。クリーム色の紙面に明朝の見出し、テラコッタの差し色。", "診断結果だけ濃い色のカードで目立たせる。", "向き：いまの雰囲気を残して、すっきり整えたい。"),
    ("b-notion.html", "案B — やさしい色カード", "元にした型：Notion。白地に太いゴシック、紙＝もも色、タブレット＝ミント色のカード。", "親しみやすく、研修資料として配りやすい。", "向き：先生どうしで気軽に回したい。"),
    ("c-apple.html", "案C — 白と余白", "元にした型：Apple。黒い看板と白い本文、色は青ひとつだけ。", "枠も影もなく、余白で区切る。", "向き：いちばん「きちんとした公式資料」に見せたい。"),
    ("d-figma.html", "案D — 白黒＋色ブロック", "元にした型：Figma。白黒の骨組みに、ライム・コーラル・ミントの大きな色面。", "紙とタブレットを「色の札」で見分ける。", "向き：いちばん印象に残したい。SNSで映える。"),
]


def build_index():
    cards = "".join(
        f'''<a class="c" href="{h}"><div class="f"><iframe src="{h}" loading="lazy" tabindex="-1" aria-hidden="true"></iframe></div>
<h2>{t}</h2><p>{a}<br>{b}<br><b>{c}</b></p><span>ひらく →</span></a>'''
        for h, t, a, b, c in INDEX_CARDS
    )
    html = f'''<!DOCTYPE html><html lang="ja"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>デザイン案の見比べ</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:"Hiragino Kaku Gothic ProN","Yu Gothic",sans-serif;background:#f4f4f2;color:#222;line-height:1.7;padding:32px 16px 64px}}
h1{{font-size:1.5rem;max-width:1200px;margin:0 auto 4px}}
.lead{{max-width:1200px;margin:0 auto 24px;color:#555;font-size:.875rem}}
.g{{max-width:1200px;margin:0 auto;display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:20px}}
.c{{background:#fff;border-radius:16px;padding:16px;text-decoration:none;color:inherit;border:1px solid #e2e2de;display:block;transition:border-color .2s}}
.c:hover{{border-color:#222}}
.f{{height:300px;overflow:hidden;border-radius:10px;border:1px solid #e2e2de;margin-bottom:14px;position:relative}}
.f iframe{{width:1200px;height:1000px;border:0;transform:scale(.3);transform-origin:0 0;pointer-events:none;position:absolute;left:0;top:0}}
@media(min-width:0){{.f{{container-type:inline-size}}.f iframe{{transform:scale(calc(100cqw / 1200px * 1));}}}}
h2{{font-size:1rem;margin-bottom:6px}}
p{{font-size:.875rem;color:#555}}
p b{{color:#222}}
span{{display:inline-block;margin-top:10px;font-size:.875rem;font-weight:700}}
</style></head><body>
<h1>デザイン案の見比べ</h1>
<p class="lead">文章と診断の仕組みはどれも同じ。変えているのは見た目だけです。気になった案をひらいて、「診断テスト」も押してみてください。</p>
<div class="g">{cards}</div>
</body></html>'''
    (HERE / "index.html").write_text(html, encoding="utf-8")


# 本番に採用した型（index.html にはこの型を当てる）
SAIYOU = "miro"

if __name__ == "__main__":
    import sys
    if "--apply" in sys.argv:
        v = next(x for x in VARIANTS if x["slug"] == SAIYOU)
        print("✓ 本体 index.html に適用 —", build(v, HERE.parent / "index.html").name, v["name"])
        sys.exit()
    if "--copy" in sys.argv:
        # 継目の修理用：本体には触らず、写し（tsugime-out/copy/index.html）にだけ書き出す
        v = next(x for x in VARIANTS if x["slug"] == SAIYOU)
        dst = HERE.parent / "tsugime-out" / "copy" / "index.html"
        dst.parent.mkdir(parents=True, exist_ok=True)
        print("✓ 写しに書き出し —", build(v, dst))
        sys.exit()
    for v in VARIANTS:
        print("✓", build(v).name, "—", v["name"])
    build_index()
    print("✓ index.html — 見比べ用の一覧")
