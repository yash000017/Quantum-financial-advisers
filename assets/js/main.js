import { initChrome } from './modules/chrome.js';
import { initReveal } from './modules/reveal.js';
import { initCounters } from './modules/counters.js';
import { initFaq } from './modules/faq.js';
import { initEnquiryForm, initFooterYear } from './modules/form.js';
import { initPointerEffects } from './modules/effects.js';
import { markCurrentNav } from './modules/nav-current.js';

document.documentElement.classList.add('js');

markCurrentNav();
initChrome();
initReveal();
initCounters();
initFaq();
initEnquiryForm();
initFooterYear();
initPointerEffects();
