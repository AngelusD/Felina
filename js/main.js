document.documentElement.classList.add('js');
document.addEventListener('DOMContentLoaded',function(){
  // Subtle reveal on scroll (CSS only hides content when motion is allowed)
  const reveals = document.querySelectorAll('.reveal, .arch-wrap');
  if('IntersectionObserver' in window && reveals.length){
    const io = new IntersectionObserver((entries)=>{
      entries.forEach(en=>{ if(en.isIntersecting){ en.target.classList.add('in'); io.unobserve(en.target); } });
    },{threshold:0.12});
    reveals.forEach(el=>io.observe(el));
  } else { reveals.forEach(el=>el.classList.add('in')); }

  const nav = document.getElementById('mainNav');
  const btn = document.getElementById('navToggle');
  if(nav && btn){
    btn.addEventListener('click', ()=>{
      const open = nav.classList.toggle('open');
      btn.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  }

  function showStatus(msg){
    const el = document.getElementById('formStatus');
    if(el){ el.textContent = msg; el.classList.add('err'); }
  }
  const contactForm = document.getElementById('contactForm');
  if(contactForm){
    contactForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const data = new FormData(contactForm);
      // disable button
      const submitBtn = contactForm.querySelector('button[type="submit"]');
      if(submitBtn){
        submitBtn.disabled = true;
        submitBtn.textContent = 'Αποστολή...';
      }
      try{
        const resp = await fetch(contactForm.action, {
          method: 'POST',
          body: data,
          headers: { 'Accept': 'application/json' }
        });
        if(resp.ok){
          // redirect locally to show a success state (Formspree does not allow free redirect)
          // preserve pathname and add query param ?sent=1
          const redirectTo = window.location.pathname.split('/').pop() || 'epikoinonia.html';
          window.location.href = redirectTo + '?sent=1';
        } else {
          const json = await resp.json();
          console.error(json);
          showStatus('Σφάλμα στην αποστολή. Δοκιμάστε ξανά.');
          if(submitBtn){ submitBtn.disabled=false; submitBtn.textContent='Αποστολή'; }
        }
      }catch(err){
        console.error(err);
        showStatus('Σφάλμα δικτύου. Δοκιμάστε ξανά.');
        if(submitBtn){ submitBtn.disabled=false; submitBtn.textContent='Αποστολή'; }
      }
    });
  }


  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // Header shadow/shrink and gentle photo parallax
  const header = document.querySelector('.site-header');
  let ticking = false;
  function onScroll(){
    if(ticking) return; ticking = true;
    requestAnimationFrame(()=>{
      header?.classList.toggle('scrolled', window.scrollY > 40);
      if(!reduce){
        document.querySelectorAll('.arch-wrap').forEach(w=>{
          const r = w.getBoundingClientRect();
          if(r.bottom < 0 || r.top > window.innerHeight) return;
          const py = (r.top + r.height/2 - window.innerHeight/2) * -0.06;
          w.style.setProperty('--py', Math.max(-20, Math.min(20, py)).toFixed(1));
        });
      }
      ticking = false;
    });
  }
  window.addEventListener('scroll', onScroll, {passive:true}); onScroll();

  // Service icons: strokes draw themselves
  document.querySelectorAll('.service svg *').forEach(el=>el.setAttribute('pathLength','1'));

  // Smooth scroll for in-page links (if any)
  document.querySelectorAll('a[href^="#"]').forEach(a=>{
    a.addEventListener('click', e=>{
      const target = a.getAttribute('href');
      if(!target || target === '#') return;
      const el = document.querySelector(target);
      if(!el) return;
      e.preventDefault();
      el.scrollIntoView({behavior:'smooth'});
    })
  })

  // Close nav on Escape and add active class to current nav link
  document.addEventListener('keydown', (e)=>{
    if(e.key === 'Escape' && nav && btn){
      if(nav.classList.contains('open')){nav.classList.remove('open');btn.setAttribute('aria-expanded','false')}
    }
  });

  // Mark active nav link based on pathname
  const links = Array.from(document.querySelectorAll('.main-nav a'));
  const path = window.location.pathname.split('/').pop() || 'index.html';
  links.forEach(a=>{
    const href = a.getAttribute('href');
    if(href === path || (href === 'index.html' && (path === '' || path === 'index.html'))){
      a.classList.add('active');
      a.setAttribute('aria-current','page');
    }
  });

  // Improve keyboard focus visibility for skip link: focus main when clicked
  const skip = document.querySelector('.skip-link');
  skip?.addEventListener('click', ()=>{
    setTimeout(()=>document.getElementById('main')?.focus(),100);
  });

  // If redirected back with ?sent=1 show a local success banner
  (function showContactSuccess(){
    try{
      const params = new URLSearchParams(window.location.search);
      if(params.get('sent') === '1'){
        const box = document.createElement('div');
        box.className = 'contact-success-banner';
        box.innerHTML = '<strong>Το μήνυμά σας στάλθηκε.</strong> Θα επικοινωνήσουμε σύντομα.';
        const main = document.getElementById('main');
        main?.insertAdjacentElement('afterbegin', box);
        // remove query param to avoid showing repeatedly when refreshing
        if(window.history && window.history.replaceState){
          const url = new URL(window.location.href);
          url.searchParams.delete('sent');
          window.history.replaceState({}, document.title, url.toString());
        }
      }
    }catch(e){/* ignore */}
  })();

  /* Lightbox with prev/next and keyboard navigation */
  function openLightbox(src, alt, startIndex = 0){
    const items = Array.from(document.querySelectorAll('.gallery-item'));
    if(!items.length) return;
    let index = typeof startIndex === 'number' && !isNaN(startIndex) ? startIndex : 0;

    const opener = document.activeElement;
    const overlay = document.createElement('div');
    overlay.className = 'lb-overlay';
    overlay.setAttribute('role','dialog'); overlay.setAttribute('aria-modal','true'); overlay.setAttribute('aria-label','Φωτογραφίες του χώρου');
    overlay.tabIndex = -1;
    overlay.innerHTML = `
      <div class="lb-inner">
        <button class="lb-close" aria-label="Κλείσιμο">×</button>
        <button class="lb-prev" aria-label="Προηγούμενη εικόνα">‹</button>
        <figure class="lb-figure"><img src="${src}" alt="${alt}"><figcaption class="lb-caption"></figcaption></figure>
        <button class="lb-next" aria-label="Επόμενη εικόνα">›</button>
      </div>
    `;

    document.body.appendChild(overlay);

    const imgEl = overlay.querySelector('img');
    const close = overlay.querySelector('.lb-close');
    const prev = overlay.querySelector('.lb-prev');
    const next = overlay.querySelector('.lb-next');
    const captionEl = overlay.querySelector('.lb-caption');

    function update(){
      const g = items[index];
      const gimg = g ? g.querySelector('img') : null;
      if(!gimg) return;
      const cap = g.querySelector('.caption')?.textContent || gimg.alt || '';
      imgEl.src = gimg.src;
      imgEl.alt = gimg.alt || '';
      captionEl.textContent = cap;
      // hide prev/next if single or at ends
      prev.style.display = items.length > 1 ? 'block' : 'none';
      next.style.display = items.length > 1 ? 'block' : 'none';
    }

    function remove(){
      overlay.remove();
      document.removeEventListener('keydown', onKey);
      if(opener && opener.focus) opener.focus();
    }

    function onKey(e){
      if(e.key === 'Escape') return remove();
      if(e.key === 'ArrowRight') return go(1);
      if(e.key === 'ArrowLeft') return go(-1);
    }

    function go(delta){
      if(items.length < 2) return;
      index = (index + delta + items.length) % items.length;
      update();
    }

    close.addEventListener('click', remove);
    prev.addEventListener('click', (e)=>{ e.stopPropagation(); go(-1); });
    next.addEventListener('click', (e)=>{ e.stopPropagation(); go(1); });
    overlay.addEventListener('click', (e)=>{ if(e.target===overlay) remove(); });
    document.addEventListener('keydown', onKey);

    update();
    // focus close for accessibility
    close.focus();
  }

  document.body.addEventListener('click', (e)=>{
      const gimg = e.target.closest('.gallery-item');
      if (gimg) {
        const img = gimg.querySelector('img');
        if(!img) return;
        const idx = gimg.getAttribute('data-index');
        openLightbox(img.src, img.alt, Number(idx));
    }
  });
});
