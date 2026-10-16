#!/usr/bin/env python3
"""Build the job pages from jobs/jobs.json.

    python3 tools/build_jobs.py

- Writes jobs/<slug>.html for every job (and removes pages for jobs no longer listed).
- Updates the "Open roles" list on job-seekers.html to match.
"""
import html, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = 'https://kli-recruitment.co.za'
SECTOR = {'fin': ('FINANCE', 'Finance'), 'sec': ('SECRETARIAL & RECEPTION', 'Secretarial & Reception')}
e = html.escape

ICON_PIN = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#0C918A" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 21s-7-6.2-7-11.5a7 7 0 0 1 14 0C19 14.8 12 21 12 21z"/><circle cx="12" cy="9.5" r="2.5"/></svg>'
ICON_BAG = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#0C918A" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="7" width="18" height="13" rx="2"/><path d="M9 7V5a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2v2"/></svg>'
ICON_ZAR = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#0C918A" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><rect x="2.5" y="6" width="19" height="12" rx="2"/><circle cx="12" cy="12" r="2.6"/></svg>'
FACEBOOK = 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCI+PHJlY3Qgd2lkdGg9IjI0IiBoZWlnaHQ9IjI0IiByeD0iNCIgZmlsbD0iIzE4NzdGMiIvPjxwYXRoIGZpbGw9IiNmZmYiIGQ9Ik0xNi42IDI0di05LjNoMy4xbC41LTMuNmgtMy42VjguOGMwLTEgLjMtMS44IDEuOC0xLjhoMS45VjMuOGMtLjMgMC0xLjUtLjEtMi44LS4xLTIuOCAwLTQuNyAxLjctNC43IDQuOHYyLjZIOS42djMuNmgzLjJWMjR6Ii8+PC9zdmc+'
LINKEDIN = 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCI+PHJlY3Qgd2lkdGg9IjI0IiBoZWlnaHQ9IjI0IiByeD0iNCIgZmlsbD0iIzBBNjZDMiIvPjxwYXRoIGZpbGw9IiNmZmYiIGQ9Ik03LjEgOS41aC0yLjZWMTloMi42VjkuNXpNNS44IDVhMS41IDEuNSAwIDEgMCAwIDMgMS41IDEuNSAwIDAgMCAwLTN6TTE5LjUgMTMuNmMwLTIuNi0uNi00LjMtMy41LTQuMy0xLjQgMC0yLjMuNy0yLjcgMS40VjkuNWgtMi41VjE5aDIuNnYtNC43YzAtMS4yLjItMi40IDEuOC0yLjQgMS41IDAgMS42IDEuNCAxLjYgMi41VjE5aDIuN3YtNS40eiIvPjwvc3ZnPg=='


def salary_range(s):
    nums = [int(n.replace(',', '')) for n in re.findall(r'\d[\d,]*', s)]
    return (nums[0], nums[1]) if len(nums) >= 2 else (nums[0], nums[0]) if nums else (None, None)


def card_meta(j):
    """'Cape Town · Permanent', plus the salary when the job asks for it (e.g. two similar roles)."""
    m = j['location'] + ' · ' + j['typeShort']
    return m + ' · ' + j['salary'] if j.get('showSalaryOnCard') else m


def apply_as(j):
    """The role name an application is sent under (defaults to the title)."""
    return j.get('applyAs') or j['title']


def section(title, body, cls=''):
    return f'<section class="job-section {cls}"><h2>{e(title)}</h2>{body}</section>'


def bullets(items):
    return '<ul>' + ''.join(f'<li>{e(i)}</li>' for i in items) + '</ul>'


def page(job, jobs):
    tag, sector_name = SECTOR[job['sector']]
    url = f"{SITE}/jobs/{job['slug']}.html"
    desc = f"{job['title']} · {job['location']} · {job['type']} · {job['salary']}. {job['summary']}"
    lo, hi = salary_range(job['salary'])
    salary_note = f"<small>{e(job['salaryNote'])}</small>" if job.get('salaryNote') else ''
    body_html = (
        section('About the company', f"<p>{e(job['about'])}</p>")
        + section(job.get('roleHeading', 'The role'), f"<p>{e(job['role'])}</p>")
        + section('Key responsibilities', bullets(job['responsibilities']))
        + section('Requirements', bullets(job['requirements']))
        + (section("What's on offer", bullets(job['offer']), 'offer') if job.get('offer') else '')
    )
    ld = {
        '@context': 'https://schema.org', '@type': 'JobPosting',
        'title': job['title'], 'description': body_html, 'datePosted': job['posted'],
        'employmentType': 'FULL_TIME', 'directApply': True, 'url': url,
        'hiringOrganization': {'@type': 'Organization', 'name': 'KLI Recruitment', 'sameAs': SITE, 'logo': f'{SITE}/assets/logo.png'},
        'jobLocation': {'@type': 'Place', 'address': {'@type': 'PostalAddress', 'addressLocality': job['location'], 'addressRegion': 'Western Cape', 'addressCountry': 'ZA'}},
    }
    if lo:
        ld['baseSalary'] = {'@type': 'MonetaryAmount', 'currency': 'ZAR', 'value': {'@type': 'QuantitativeValue', 'minValue': lo, 'maxValue': hi, 'unitText': 'MONTH'}}
    ld_json = json.dumps(ld, ensure_ascii=False).replace('</', '<\\/')
    others = [j for j in jobs if j['slug'] != job['slug']]
    more = ''.join(
        f'<a class="more-card" href="{j["slug"]}.html"><span class="s" style="color:{"#0C918A" if j["sector"] == "fin" else "#B07A06"}">{e(SECTOR[j["sector"]][0])}</span>'
        f'<span class="t">{e(j["title"])}</span><span class="m">{e(card_meta(j))}</span></a>' for j in others)

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(job['title'])} | KLI Recruitment</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="KLI Recruitment">
<meta property="og:title" content="{e(job['title'])}: {e(job['location'])}, {e(job['salary'])}">
<meta property="og:description" content="{e(job['summary'])} Apply now with KLI Recruitment.">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE}/assets/og-jobs.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="../assets/logo.png">
<link rel="stylesheet" href="../assets/site.css">
<script type="application/ld+json">{ld_json}</script>
</head>
<body>

<header class="kli-header">
  <div class="kli-hdr">
    <a class="kli-logo" href="../index.html"><img src="../assets/logo.png" alt="KLI Recruitment"></a>
    <nav class="kli-nav">
      <a href="../index.html">Home</a>
      <a href="../about.html">About</a>
      <a href="../employers.html">Employers</a>
      <a class="on" href="../job-seekers.html">Job Seekers</a>
      <a href="../contact.html">Contact</a>
      <a class="kli-navcta" href="../contact.html">Let's Talk →</a>
    </nav>
    <a class="kli-cta" href="../contact.html">Let's Talk <span>→</span></a>
    <button type="button" class="kli-burger" aria-label="Open menu" aria-expanded="false"><span></span><span></span><span></span></button>
  </div>
</header>

<main>
  <section class="job-hero">
    <div class="wrap">
      <div class="crumbs"><a href="../job-seekers.html">Job Seekers</a><span>›</span><a href="../job-seekers.html">Open roles</a><span>›</span><span>{e(job['title'])}</span></div>
      <div class="job-sector {job['sector']}">{e(tag)}</div>
      <h1>{e(job['title'])}<span class="dot">.</span></h1>
      <div class="facts">
        <span class="fact">{ICON_PIN}{e(job['location'])}</span>
        <span class="fact">{ICON_BAG}{e(job['type'])}</span>
        <span class="fact">{ICON_ZAR}{e(job['salary'])}</span>
      </div>
      <div class="hero-actions">
        <a class="btn btn-teal" href="#apply">Apply for this role <span>→</span></a>
        <a class="btn btn-line" href="../job-seekers.html">← All open roles</a>
      </div>
    </div>
  </section>

  <section class="job-body">
    <div class="wrap">
      <article>
        {body_html}
      </article>
      <aside class="summary">
        <h3>JOB SUMMARY</h3>
        <dl>
          <dt>Role</dt><dd>{e(job['title'])}</dd>
          <dt>Location</dt><dd>{e(job['location'])}</dd>
          <dt>Salary</dt><dd>{e(job['salary'])}{salary_note}</dd>
          <dt>Type</dt><dd>{e(job['type'])}</dd>
          <dt>Sector</dt><dd>{e(sector_name)}</dd>
        </dl>
        <a class="btn btn-teal" href="#apply">Apply now <span>→</span></a>
        <div class="help">Questions about this role? Call or WhatsApp Russell on <a href="tel:+27818785864">+27 81 878 5864</a>.</div>
      </aside>
    </div>
  </section>

  <section class="apply" id="apply">
    <div class="wrap">
      <div class="apply-intro">
        <div class="eyebrow">APPLY FOR THIS ROLE</div>
        <h2>Interested? Send us your CV<span class="dot">.</span></h2>
        <p>Tailor your CV to this role before you send it: lead with your most relevant experience and use the same words as the job description. You'll speak to Russell directly.</p>
      </div>
      <div class="apply-card">
        <form class="apply-form" data-role="{e(apply_as(job))}" enctype="multipart/form-data">
          <input type="hidden" name="role" value="{e(apply_as(job))}">
          <input type="hidden" name="sector" value="{e(sector_name)}">
          <div class="full role-lock">{e(job['title'])}<span>Applying for</span></div>
          <label>Full name<input name="name" type="text" required autocomplete="name"></label>
          <label>Email<input name="email" type="email" required autocomplete="email"></label>
          <label class="full">Phone<input name="phone" type="tel" autocomplete="tel"></label>
          <label class="full file">
            <span class="fl"><b>Upload your CV</b><small>PDF or Word, up to 5MB</small></span>
            <span class="choose">Choose file</span>
            <input name="attachment" type="file" accept=".pdf,.doc,.docx" required>
          </label>
          <label class="full">Anything we should know? <span class="optional">(optional)</span><textarea name="message" rows="4"></textarea></label>
          <button type="submit" class="btn btn-teal full">Send my application <span>→</span></button>
          <div class="form-error full" role="alert" hidden></div>
        </form>
        <div class="sent" hidden>
          <div class="ck">✓</div>
          <b>Thanks, we've got your CV<span class="dot">.</span></b>
          <p>Russell will be in touch soon. If it's urgent, call +27 81 878 5864.</p>
        </div>
      </div>
    </div>
  </section>

  <section class="more">
    <div class="wrap">
      <div class="eyebrow">CURRENT VACANCIES</div>
      <h2>Other open roles<span class="dot">.</span></h2>
      <div class="more-list">{more}</div>
    </div>
  </section>
</main>

<footer class="site-footer">
  <div class="top">
    <div class="brand"><img src="../assets/logo.png" alt="KLI Recruitment"><p>Specialist finance and secretarial recruitment, based in Cape Town.</p></div>
    <div class="col"><h4>EXPLORE</h4><a href="../about.html">About</a><a href="../employers.html">Employers</a><a href="../job-seekers.html">Job Seekers</a></div>
    <div class="col"><h4>CONTACT</h4><a href="mailto:russell@kli-recruitment.co.za">russell@kli-recruitment.co.za</a><a href="tel:+27818785864">+27 81 878 5864</a><div>Cape Town, South Africa</div>
      <a class="li" href="https://www.linkedin.com/company/kli-recruitment/?originalSubdomain=za" target="_blank" rel="noopener" aria-label="KLI Recruitment on LinkedIn"><img src="{LINKEDIN}" alt="" width="28" height="28">LinkedIn</a>
      <a class="fb" href="https://www.facebook.com/klirecruitment" target="_blank" rel="noopener" aria-label="KLI Recruitment on Facebook"><img src="{FACEBOOK}" alt="" width="28" height="28">Facebook</a></div>
  </div>
  <div class="bottom"><div>© 2026 KLI Recruitment. All rights reserved.</div><div>People. Places. Possibilities.</div></div>
</footer>

<script src="../assets/job.js"></script>
</body>
</html>
'''


# ---------- job-seekers.html (bundled page: its content is a JSON string inside a script tag) ----------
def esc(s):
    """Encode text the way it appears inside the page's JSON-encoded template."""
    return json.dumps(s, ensure_ascii=False)[1:-1].replace('</', '<\\u002F')


CARD_OLD = esc('''              <div style="font-size:20px;font-weight:700;letter-spacing:-0.01em">{{ job.title }}</div>
              <div style="font-size:15px;color:#44586A">{{ job.meta }}</div>
            </div>
            <button sc-camel-on-click="{{ job.onApply }}" style="cursor:pointer;display:inline-flex;align-items:center;gap:10px;font-size:15px;font-weight:600;padding:13px 24px;border-radius:999px;border:1.5px solid rgba(20,41,58,0.18);background:#ffffff;color:#14293A" style-hover="background:#0FB5AC;border-color:#0FB5AC;color:#ffffff">Apply <span>→</span></button>''')
CARD_NEW = esc('''              <a href="{{ job.url }}" style="font-size:20px;font-weight:700;letter-spacing:-0.01em;color:#14293A" style-hover="color:#0C918A">{{ job.title }}</a>
              <div style="font-size:15px;color:#44586A">{{ job.meta }}</div>
              <div style="font-size:15px;line-height:1.55;color:#44586A;max-width:62ch;margin-top:2px">{{ job.summary }}</div>
            </div>
            <div style="display:flex;flex-wrap:wrap;gap:10px">
              <a href="{{ job.url }}" style="display:inline-flex;align-items:center;gap:10px;font-size:15px;font-weight:600;padding:13px 24px;border-radius:999px;background:#0FB5AC;color:#ffffff;white-space:nowrap" style-hover="background:#0C918A;color:#ffffff">View details <span>→</span></a>
              <button sc-camel-on-click="{{ job.onApply }}" style="cursor:pointer;display:inline-flex;align-items:center;gap:10px;font-size:15px;font-weight:600;padding:13px 24px;border-radius:999px;border:1.5px solid rgba(20,41,58,0.18);background:#ffffff;color:#14293A;white-space:nowrap" style-hover="background:#0FB5AC;border-color:#0FB5AC;color:#ffffff">Apply <span>→</span></button>
            </div>''')
MAP_OLD = esc("      meta: j.where + '  ·  ' + j.type,\n")
MAP_NEW = esc("      meta: j.where + '  ·  ' + j.type,\n      summary: j.summary,\n      url: 'jobs/' + j.slug + '.html',\n")


def update_job_seekers(jobs):
    path = os.path.join(ROOT, 'job-seekers.html')
    d = open(path, encoding='utf-8').read()
    start = d.find('<script type="__bundler/template">') + len('<script type="__bundler/template">')
    end = d.find('</script>', start)
    raw = d[start:end]
    # One-time upgrade of the job cards (summary line + View details link)
    if 'job.url' not in raw:
        for old, new in ((CARD_OLD, CARD_NEW), (MAP_OLD, MAP_NEW)):
            if raw.count(old) != 1:
                sys.exit('job-seekers.html: could not find the job card markup to upgrade')
            raw = raw.replace(old, new)
    APPLY_OLD = esc("onApply: () => this.apply(j.title, ")
    if raw.count(APPLY_OLD) == 1:
        raw = raw.replace(APPLY_OLD, esc("onApply: () => this.apply(j.applyAs || j.title, "))
    # Replace the job list
    rows = ',\n'.join(
        '    { ' + ', '.join(f'{k}: {json.dumps(v, ensure_ascii=False)}' for k, v in (
            ('slug', j['slug']), ('title', j['title']), ('sector', j['sector']),
            ('where', j['location']), ('type', card_meta(j)[len(j['location']) + 3:]), ('summary', j['summary']),
            ('applyAs', apply_as(j)))) + ' }'
        for j in jobs)
    m = re.search(r'jobsData = \[.*?\];', raw)
    if not m:
        sys.exit('job-seekers.html: could not find jobsData')
    raw = raw[:m.start()] + esc('jobsData = [\n' + rows + '\n  ];') + raw[m.end():]
    json.loads(raw)   # must still be valid
    open(path, 'w', encoding='utf-8').write(d[:start] + raw + d[end:])


def main():
    data = json.load(open(os.path.join(ROOT, 'jobs', 'jobs.json'), encoding='utf-8'))
    jobs = data['jobs']
    out = os.path.join(ROOT, 'jobs')
    keep = set()
    for job in jobs:
        name = job['slug'] + '.html'
        keep.add(name)
        open(os.path.join(out, name), 'w', encoding='utf-8').write(page(job, jobs))
        print('wrote jobs/' + name)
    for f in os.listdir(out):
        if f.endswith('.html') and f not in keep:
            os.remove(os.path.join(out, f))
            print('removed jobs/' + f)
    update_job_seekers(jobs)
    print('updated job-seekers.html')


if __name__ == '__main__':
    main()
