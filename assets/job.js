// Job pages and thank-you page: mobile menu + application form checks.
// Applications are ordinary form posts to FormSubmit: its /ajax/ address drops attached files.
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
    var f = file.files[0];
    if (f && f.size > MAX) {
      e.preventDefault();
      error.textContent = 'That file is over 5MB. Please attach a smaller PDF or Word document.';
      error.hidden = false;
      return;
    }
    error.hidden = true;
    button.disabled = true;
    button.firstChild.textContent = 'Sending… ';
  });

  // If someone comes back with the browser's Back button, let them send again
  window.addEventListener('pageshow', function (e) {
    if (e.persisted) {
      button.disabled = false;
      button.firstChild.textContent = 'Send my application ';
    }
  });
})();
