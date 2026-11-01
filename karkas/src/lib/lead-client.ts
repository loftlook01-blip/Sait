/**
 * Клиентская логика заявок: маска телефона, отправка JSON, цели Метрики, запасной сценарий.
 * Любая форма с атрибутом data-lead-form подключается автоматически.
 */
declare global { interface Window { ym?: (...a: unknown[]) => void; __ym?: string } }

export function goal(name: string, params?: Record<string, unknown>) {
  try { if (window.ym && window.__ym) window.ym(window.__ym, 'reachGoal', name, params); } catch {}
}

function maskPhone(input: HTMLInputElement) {
  input.addEventListener('input', () => {
    let d = input.value.replace(/\D/g, '');
    if (d.startsWith('8')) d = '7' + d.slice(1);
    if (!d.startsWith('7')) d = '7' + d;
    d = d.slice(0, 11);
    const p = ['+7'];
    if (d.length > 1) p.push(' (' + d.slice(1, 4));
    if (d.length >= 4) p.push(') ' + d.slice(4, 7));
    if (d.length >= 7) p.push('-' + d.slice(7, 9));
    if (d.length >= 9) p.push('-' + d.slice(9, 11));
    input.value = d.length <= 1 ? '+7 ' : p.join('');
  });
  input.addEventListener('focus', () => { if (!input.value) input.value = '+7 '; });
}

export function bindForms(root: ParentNode = document) {
  root.querySelectorAll<HTMLFormElement>('form[data-lead-form]:not([data-bound])').forEach((form) => {
    form.dataset.bound = '1';
    form.querySelectorAll<HTMLInputElement>('input[type=tel]').forEach(maskPhone);
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const status = form.querySelector<HTMLElement>('[data-status]');
      const btn = form.querySelector<HTMLButtonElement>('button[type=submit]');
      const data = Object.fromEntries(new FormData(form).entries()) as Record<string, string>;
      if ((data.phone || '').replace(/\D/g, '').length < 11) {
        status && (status.textContent = 'Проверьте номер телефона — нужно 11 цифр.');
        form.querySelector<HTMLInputElement>('input[type=tel]')?.focus();
        return;
      }
      data.page = location.pathname;
      data.consent = data.consent ? '1' : '';
      btn && (btn.disabled = true);
      status && (status.textContent = 'Отправляем…');
      try {
        const res = await fetch(form.action, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) });
        if (!res.ok) throw new Error(String(res.status));
        goal('lead', { source: data.source });
        form.classList.add('is-sent');
        form.dispatchEvent(new CustomEvent('lead:sent', { bubbles: true }));
      } catch {
        status && (status.innerHTML = 'Не удалось отправить. Позвоните нам или напишите в мессенджер — ответим сразу.');
        form.classList.add('is-failed');
      } finally {
        btn && (btn.disabled = false);
      }
    });
  });
}
