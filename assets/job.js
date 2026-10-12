// Job detail pages: mobile menu + application form (sent to Russell via FormSubmit, like the Job Seekers form).
(function () {
  document.addEventListener('click', function (e) {
    var header = document.querySelector('.kli-header');
    if (!header) return;
    var burger = e.target.closest('.kli-burger');
    if (burger) {
      var open = header.classList.toggle('kli-open');
      burger.setAttribute('aria-expanded', open ? 'true' : 'false');
      burger.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
    } else if (!e.target.closest('.kli-nav')) {
      header.classList.remove('kli-open');
    }
  });

  var form = document.querySelector('.apply-form');
  if (!form) return;
  var file = form.querySelector('input[type=file]');
  var fileBox = form.querySelector('.file');
  var fileLabel = form.querySelector('.file .fl b');
  var error = form.querySelector('.form-error');
  var button = form.querySelector('button[type=submit]');
  var MAX = 5 * 1024 * 1024;

  file.addEventListener('change', function () {
    var f = file.files[0];
    fileLabel.textContent = f ? f.name : 'Upload your CV';
    fileBox.classList.toggle('has', !!f);
  });

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    if (button.disabled) return;
    var f = file.files[0];
    if (f && f.size > MAX) {
      error.textContent = 'That file is over 5MB. Please attach a smaller PDF or Word document.';
      error.hidden = false;
      return;
    }
    var data = new FormData(form);
    data.append('_subject', 'Application: ' + form.dataset.role + ' (KLI website)');
    data.append('_template', 'table');
    data.append('_captcha', 'false');
    error.hidden = true;
    button.disabled = true;
    button.firstChild.textContent = 'Sending… ';
    fetch('https://formsubmit.co/ajax/russell@kli-recruitment.co.za', { method: 'POST', body: data, headers: { Accept: 'application/json' } })
      .then(function (r) { if (!r.ok) throw new Error(r.status); })
      .then(function () {
        form.hidden = true;
        document.querySelector('.sent').hidden = false;
      })
      .catch(function () {
        error.textContent = 'Sorry, that didn’t send. Please email your CV to russell@kli-recruitment.co.za.';
        error.hidden = false;
        button.disabled = false;
        button.firstChild.textContent = 'Send my application ';
      });
  });
})();
