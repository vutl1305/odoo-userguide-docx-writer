/* Load in the browser page before capturing a real Odoo screenshot. */
(() => {
  const id = 'odoo-userguide-annotation';
  const clear = () => document.getElementById(id)?.remove();
  function annotate(target, {step = '', context = null} = {}) {
    clear();
    if (!(target instanceof Element)) throw new Error('A real target element is required');
    target.scrollIntoView({block: 'nearest', inline: 'nearest'});
    const b = target.getBoundingClientRect();
    if (!b.width || !b.height || getComputedStyle(target).visibility === 'hidden') {
      throw new Error('Screenshot target must be visible');
    }
    const W = innerWidth, H = innerHeight;
    const x = Math.max(2, b.x - 3), y = Math.max(2, b.y - 3);
    const w = Math.min(b.width + 6, W - x - 2), h = Math.min(b.height + 6, H - y - 2);
    if (w <= 0 || h <= 0 || b.bottom <= 0 || b.right <= 0) {
      throw new Error('Screenshot target is outside the viewport');
    }
    const right = x + w + 80 < W;
    const ex = right ? x + w + 5 : x > 80 ? x - 5 : Math.min(x + w - 12, W - 20);
    const ey = Math.min(H - 8, y + Math.min(h / 2, 25));
    const sx = Math.min(W - 8, Math.max(8, ex + (right ? 60 : -60)));
    const sy = Math.min(H - 8, Math.max(8, ey + 32));
    const overlay = document.createElement('div');
    overlay.id = id;
    overlay.style = 'position:fixed;inset:0;z-index:2147483647;pointer-events:none';
    overlay.innerHTML = `<svg width="${W}" height="${H}" xmlns="http://www.w3.org/2000/svg">
      <defs><marker id="ug-arrow" markerUnits="userSpaceOnUse" markerWidth="10" markerHeight="8"
        refX="9" refY="4" orient="auto"><path d="M0,0 L10,4 L0,8 Z" fill="#d92d20"/></marker></defs>
      <rect x="${x}" y="${y}" width="${w}" height="${h}" rx="3" fill="none" stroke="#d92d20" stroke-width="1.5"/>
      <path d="M${sx},${sy} L${ex},${ey}" fill="none" stroke="white" stroke-width="4"/>
      <path d="M${sx},${sy} L${ex},${ey}" fill="none" stroke="#d92d20" stroke-width="2" marker-end="url(#ug-arrow)"/>
    </svg>`;
    document.body.appendChild(overlay);
    const c = context instanceof Element ? context.getBoundingClientRect() : b;
    const left = Math.max(0, Math.min(x, sx, c.x) - 20);
    const top = Math.max(0, Math.min(y, sy, c.y) - 20);
    const width = Math.min(W, Math.max(400, Math.min(W, Math.max(x + w, sx, c.right) + 20) - left));
    const height = Math.min(H, Math.max(200, Math.min(H, Math.max(y + h, sy, c.bottom) + 20) - top));
    const clipLeft = Math.min(left, W - width), clipTop = Math.min(top, H - height);
    return {step, target: {x: b.x, y: b.y, width: b.width, height: b.height},
      clip: {x: clipLeft, y: clipTop, width, height, scale: 1},
      arrow: {stroke: 2, headWidth: 10, headHeight: 8, markerUnits: 'userSpaceOnUse'}};
  }
  window.OdooUserGuide = {annotate, clear};
})();
