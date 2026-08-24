// Minimal WebDriver BiDi client, so the spike can drive a REAL browser build
// (retail Firefox, or safaridriver --bidi) headed, with a real compositor.
// Playwright's own Firefox/WebKit builds no-op backdrop-filter (see engine-check),
// so this is the only path to trustworthy pixels for those engines.
import { spawn } from 'node:child_process';
import { writeFileSync, mkdirSync } from 'node:fs';

export class Bidi {
  constructor(ws) { this.ws = ws; this.id = 0; this.pending = new Map(); }

  static async connect(url, tries = 60) {
    for (let i = 0; i < tries; i++) {
      try {
        const ws = new WebSocket(url);
        await new Promise((res, rej) => {
          ws.addEventListener('open', res, { once: true });
          ws.addEventListener('error', rej, { once: true });
        });
        const c = new Bidi(ws);
        ws.addEventListener('message', (e) => {
          const m = JSON.parse(e.data);
          if (m.id !== undefined && c.pending.has(m.id)) {
            const { res, rej } = c.pending.get(m.id);
            c.pending.delete(m.id);
            m.type === 'error' ? rej(new Error(m.error + ': ' + m.message)) : res(m.result);
          }
        });
        return c;
      } catch {
        await new Promise((r) => setTimeout(r, 500));
      }
    }
    throw new Error('BiDi connect failed: ' + url);
  }

  send(method, params = {}) {
    const id = ++this.id;
    return new Promise((res, rej) => {
      this.pending.set(id, { res, rej });
      this.ws.send(JSON.stringify({ id, method, params }));
      setTimeout(() => {
        if (this.pending.has(id)) { this.pending.delete(id); rej(new Error('timeout ' + method)); }
      }, 40000);
    });
  }

  async start(caps = {}) {
    await this.send('session.new', { capabilities: { alwaysMatch: caps } });
    const tree = await this.send('browsingContext.getTree', {});
    this.ctx = tree.contexts[0].context;
    return this.ctx;
  }

  viewport(width, height, devicePixelRatio = 1) {
    return this.send('browsingContext.setViewport', {
      context: this.ctx, viewport: { width, height }, devicePixelRatio,
    });
  }

  goto(url) {
    return this.send('browsingContext.navigate', { context: this.ctx, url, wait: 'complete' });
  }

  // Wraps the BiDi `script.evaluate` command (a remote-automation call to the
  // browser under test), not JS eval. Every expression passed here is a literal
  // written in this spike's own harness.
  eval(expr, awaitPromise = true) {
    return this.send('script.evaluate', {
      expression: expr, target: { context: this.ctx },
      awaitPromise, resultOwnership: 'none',
    });
  }

  async shot(path, clip) {
    const r = await this.send('browsingContext.captureScreenshot', {
      context: this.ctx,
      origin: 'document',
      ...(clip ? { clip: { type: 'box', ...clip } } : {}),
    });
    writeFileSync(path, Buffer.from(r.data, 'base64'));
    return path;
  }

  close() { try { this.ws.close(); } catch { /* already gone */ } }
}

/** Launch retail Firefox headed with BiDi enabled. */
export async function launchFirefox(binary, profile, port = 9333) {
  mkdirSync(profile, { recursive: true });
  const proc = spawn(binary, [
    '--profile', profile,
    '--remote-debugging-port', String(port),
    '--new-window', 'about:blank',
  ], { stdio: ['ignore', 'pipe', 'pipe'] });
  proc.stderr.on('data', () => {});
  proc.stdout.on('data', () => {});
  const c = await Bidi.connect(`ws://127.0.0.1:${port}/session`);
  await c.start({ acceptInsecureCerts: true });
  return { client: c, proc };
}
