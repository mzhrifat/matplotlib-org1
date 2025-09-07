# Create a minimal demo crypto exchange project structure and zip it for download

import os, json, textwrap, zipfile, pathlib

base = "/mnt/data/mini-crypto-exchange"
backend = os.path.join(base, "backend")
frontend = os.path.join(base, "frontend")
os.makedirs(backend, exist_ok=True)
os.makedirs(frontend, exist_ok=True)

# ---- Backend files ----
backend_pkg = {
  "name": "mini-crypto-exchange-backend",
  "version": "0.1.0",
  "private": True,
  "type": "module",
  "main": "server.js",
  "scripts": {
    "start": "node server.js",
    "dev": "NODE_ENV=development node server.js",
    "reset:db": "node scripts/reset-db.js"
  },
  "dependencies": {
    "bcryptjs": "^2.4.3",
    "cors": "^2.8.5",
    "express": "^4.19.2",
    "jsonwebtoken": "^9.0.2",
    "sqlite3": "^5.1.7",
    "uuid": "^9.0.1",
    "ws": "^8.18.0",
    "dotenv": "^16.4.5"
  }
}

server_js = r"""import express from 'express';
import cors from 'cors';
import jwt from 'jsonwebtoken';
import bcrypt from 'bcryptjs';
import { v4 as uuidv4 } from 'uuid';
import { WebSocketServer } from 'ws';
import dotenv from 'dotenv';
import { getDB, initDB } from './db.js';
import { MatchingEngine } from './engine.js';

dotenv.config();

const app = express();
app.use(cors());
app.use(express.json());

const PORT = process.env.PORT || 4000;
const JWT_SECRET = process.env.JWT_SECRET || 'dev_secret_change_me';

// Init DB & Engine
await initDB();
const db = getDB();
const engine = new MatchingEngine(db);

// --- WebSocket ---
const wss = new WebSocketServer({ noServer: true });
const clients = new Set();

wss.on('connection', (ws) => {
  clients.add(ws);
  ws.on('close', () => clients.delete(ws));
});

function broadcast(type, payload) {
  const message = JSON.stringify({ type, payload });
  for (const ws of clients) {
    if (ws.readyState === 1) ws.send(message);
  }
}

// Subscribe engine events
engine.on('orderbook', (symbol, snapshot) => {
  broadcast('orderbook', { symbol, snapshot });
});
engine.on('trade', (trade) => {
  broadcast('trade', trade);
});

// --- Auth helpers ---
function auth(req, res, next) {
  const hdr = req.headers.authorization || '';
  const token = hdr.startsWith('Bearer ') ? hdr.slice(7) : null;
  if (!token) return res.status(401).json({ error: 'No token' });
  try {
    req.user = jwt.verify(token, JWT_SECRET);
    next();
  } catch (e) {
    return res.status(401).json({ error: 'Invalid token' });
  }
}

// --- Routes ---
app.get('/', (_, res) => res.json({ ok: true, service: 'mini-exchange-backend' }));

// Auth
app.post('/api/auth/register', async (req, res) => {
  const { email, password } = req.body || {};
  if (!email || !password) return res.status(400).json({ error: 'email & password required' });
  const hash = await bcrypt.hash(password, 10);
  const id = uuidv4();
  try {
    await db.run(`INSERT INTO users(id,email,password_hash) VALUES (?,?,?)`, [id, email, hash]);
  } catch (e) {
    return res.status(400).json({ error: 'Email already exists?' });
  }
  const token = jwt.sign({ id, email }, JWT_SECRET, { expiresIn: '7d' });
  res.json({ token });
});

app.post('/api/auth/login', async (req, res) => {
  const { email, password } = req.body || {};
  const row = await db.get(`SELECT * FROM users WHERE email = ?`, [email]);
  if (!row) return res.status(400).json({ error: 'Invalid credentials' });
  const ok = await bcrypt.compare(password, row.password_hash);
  if (!ok) return res.status(400).json({ error: 'Invalid credentials' });
  const token = jwt.sign({ id: row.id, email: row.email }, JWT_SECRET, { expiresIn: '7d' });
  res.json({ token });
});

// Market data
app.get('/api/market/orderbook', (req, res) => {
  const symbol = (req.query.symbol || 'BTCUSDT').toString().toUpperCase();
  const snapshot = engine.getOrderBookSnapshot(symbol);
  res.json({ symbol, orderbook: snapshot });
});

app.get('/api/market/trades', async (req, res) => {
  const symbol = (req.query.symbol || 'BTCUSDT').toString().toUpperCase();
  const rows = await db.all(`SELECT * FROM trades WHERE symbol = ? ORDER BY ts DESC LIMIT 100`, [symbol]);
  res.json({ symbol, trades: rows });
});

// Orders
app.post('/api/orders', auth, async (req, res) => {
  const { symbol='BTCUSDT', side, type='LIMIT', price, quantity } = req.body || {};
  if (!['BUY','SELL'].includes((side||'').toUpperCase())) return res.status(400).json({ error: 'side must be BUY/SELL' });
  if (type !== 'LIMIT') return res.status(400).json({ error: 'Only LIMIT supported in demo' });
  if (!(price > 0 && quantity > 0)) return res.status(400).json({ error: 'price & quantity must be > 0' });
  const order = {
    id: uuidv4(),
    user_id: req.user.id,
    symbol: symbol.toUpperCase(),
    side: side.toUpperCase(),
    price: Number(price),
    quantity: Number(quantity),
    remaining: Number(quantity),
    status: 'OPEN',
    ts: Date.now()
  };
  await engine.placeOrder(order);
  res.json({ order });
});

app.get('/api/orders/mine', auth, async (req, res) => {
  const rows = await db.all(`SELECT * FROM orders WHERE user_id = ? ORDER BY ts DESC LIMIT 100`, [req.user.id]);
  res.json({ orders: rows });
});

// HTTP + WS upgrade
const server = app.listen(PORT, () => {
  console.log(`Backend listening on http://localhost:${PORT}`);
});

server.on('upgrade', (request, socket, head) => {
  wss.handleUpgrade(request, socket, head, (ws) => {
    wss.emit('connection', ws, request);
  });
});
"""

db_js = r"""import sqlite3 from 'sqlite3';
import { open } from 'sqlite';

let db;

export async function initDB() {
  db = await open({
    filename: './demo.db',
    driver: sqlite3.Database
  });
  await db.exec(`
  PRAGMA journal_mode = WAL;
  CREATE TABLE IF NOT EXISTS users(
    id TEXT PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL
  );
  CREATE TABLE IF NOT EXISTS orders(
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    symbol TEXT NOT NULL,
    side TEXT NOT NULL,
    price REAL NOT NULL,
    quantity REAL NOT NULL,
    remaining REAL NOT NULL,
    status TEXT NOT NULL,
    ts INTEGER NOT NULL
  );
  CREATE TABLE IF NOT EXISTS trades(
    id TEXT PRIMARY KEY,
    buy_order_id TEXT NOT NULL,
    sell_order_id TEXT NOT NULL,
    symbol TEXT NOT NULL,
    price REAL NOT NULL,
    quantity REAL NOT NULL,
    ts INTEGER NOT NULL
  );
  `);
}

export function getDB() {
  if (!db) throw new Error('DB not initialized');
  return db;
}
"""

engine_js = r"""import { EventEmitter } from 'events';
import { v4 as uuidv4 } from 'uuid';

export class MatchingEngine extends EventEmitter {
  constructor(db) {
    super();
    this.db = db;
    this.books = new Map(); // symbol -> { bids: [], asks: [] }
  }

  getBook(symbol) {
    symbol = symbol.toUpperCase();
    if (!this.books.has(symbol)) this.books.set(symbol, { bids: [], asks: [] });
    return this.books.get(symbol);
  }

  snapshot(book) {
    // return top 20 levels
    const agg = (side) => Object.entries(side.reduce((acc, o) => {
      acc[o.price] = (acc[o.price] || 0) + o.remaining;
      return acc;
    }, {})).map(([p, q]) => ({ price: Number(p), qty: q }));
    const bids = agg([...book.bids]).sort((a,b)=>b.price-a.price).slice(0,20);
    const asks = agg([...book.asks]).sort((a,b)=>a.price-b.price).slice(0,20);
    return { bids, asks };
  }

  getOrderBookSnapshot(symbol) {
    return this.snapshot(this.getBook(symbol));
  }

  async placeOrder(order) {
    const book = this.getBook(order.symbol);
    // Persist order
    await this.db.run(`INSERT INTO orders(id,user_id,symbol,side,price,quantity,remaining,status,ts)
      VALUES (?,?,?,?,?,?,?,?,?)`, [order.id, order.user_id, order.symbol, order.side, order.price, order.quantity, order.remaining, order.status, order.ts]);

    // Insert into book
    if (order.side === 'BUY') {
      book.bids.push(order);
      book.bids.sort((a,b)=>b.price-a.price || a.ts-b.ts);
    } else {
      book.asks.push(order);
      book.asks.sort((a,b)=>a.price-b.price || a.ts-b.ts);
    }
    // Try match
    await this.match(order.symbol);
    // Emit snapshot
    this.emit('orderbook', order.symbol, this.snapshot(book));
  }

  async match(symbol) {
    const book = this.getBook(symbol);
    while (book.bids.length && book.asks.length) {
      const buy = book.bids[0];
      const sell = book.asks[0];
      if (buy.price < sell.price) break; // no cross
      const qty = Math.min(buy.remaining, sell.remaining);
      const price = sell.ts <= buy.ts ? sell.price : buy.price; // simple price rule
      const trade = {
        id: uuidv4(),
        buy_order_id: buy.id,
        sell_order_id: sell.id,
        symbol,
        price,
        quantity: qty,
        ts: Date.now()
      };
      await this.db.run(`INSERT INTO trades(id,buy_order_id,sell_order_id,symbol,price,quantity,ts) VALUES (?,?,?,?,?,?,?)`,
        [trade.id, trade.buy_order_id, trade.sell_order_id, trade.symbol, trade.price, trade.quantity, trade.ts]);
      this.emit('trade', trade);

      buy.remaining -= qty;
      sell.remaining -= qty;
      if (buy.remaining <= 1e-12) {
        buy.status = 'FILLED';
        await this.db.run(`UPDATE orders SET remaining=?, status=? WHERE id=?`, [0, 'FILLED', buy.id]);
        book.bids.shift();
      } else {
        await this.db.run(`UPDATE orders SET remaining=? WHERE id=?`, [buy.remaining, buy.id]);
      }
      if (sell.remaining <= 1e-12) {
        sell.status = 'FILLED';
        await this.db.run(`UPDATE orders SET remaining=?, status=? WHERE id=?`, [0, 'FILLED', sell.id]);
        book.asks.shift();
      } else {
        await this.db.run(`UPDATE orders SET remaining=? WHERE id=?`, [sell.remaining, sell.id]);
      }
    }
  }
}
"""

env_example = "JWT_SECRET=change_me\nPORT=4000\n"

scripts_dir = os.path.join(backend, "scripts")
os.makedirs(scripts_dir, exist_ok=True)
reset_db_js = r"""import { initDB, getDB } from '../db.js';
await initDB();
const db = getDB();
await db.exec(`DROP TABLE IF EXISTS trades; DROP TABLE IF EXISTS orders; DROP TABLE IF EXISTS users;`);
console.log('Dropped tables.');
process.exit(0);
"""

with open(os.path.join(backend, "package.json"), "w") as f:
    json.dump(backend_pkg, f, indent=2)
open(os.path.join(backend, "server.js"), "w").write(server_js)
open(os.path.join(backend, "db.js"), "w").write(db_js)
open(os.path.join(backend, "engine.js"), "w").write(engine_js)
open(os.path.join(backend, ".env.example"), "w").write(env_example)
open(os.path.join(scripts_dir, "reset-db.js"), "w").write(reset_db_js)

# ---- Frontend (Next.js minimal with plain fetch + ws) ----
frontend_pkg = {
  "name": "mini-crypto-exchange-frontend",
  "version": "0.1.0",
  "private": True,
  "scripts": {
    "dev": "next dev -p 3000",
    "build": "next build",
    "start": "next start -p 3000"
  },
  "dependencies": {
    "next": "14.2.5",
    "react": "18.3.1",
    "react-dom": "18.3.1"
  }
}

next_config = r"""/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  experimental: { appDir: false }
};
export default nextConfig;
"""

api_ts = r"""export const API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:4000';
export async function api(path: string, opts: RequestInit = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...(opts.headers || {}) },
    ...opts,
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}
"""

index_tsx = r"""import { useEffect, useMemo, useRef, useState } from 'react';

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:4000';

type Level = { price: number; qty: number };
type Snapshot = { bids: Level[]; asks: Level[] };
type Trade = { id: string; symbol: string; price: number; quantity: number; ts: number };

export default function Home() {
  const [token, setToken] = useState<string>('');
  const [email, setEmail] = useState('demo@example.com');
  const [password, setPassword] = useState('demo1234');
  const [symbol, setSymbol] = useState('BTCUSDT');
  const [ob, setOb] = useState<Snapshot>({ bids: [], asks: [] });
  const [trades, setTrades] = useState<Trade[]>([]);
  const priceRef = useRef<HTMLInputElement>(null);
  const qtyRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    fetch(`${API_BASE}/api/market/orderbook?symbol=${symbol}`)
      .then(r=>r.json()).then(d=>setOb(d.orderbook)).catch(()=>{});
    fetch(`${API_BASE}/api/market/trades?symbol=${symbol}`)
      .then(r=>r.json()).then(d=>setTrades(d.trades)).catch(()=>{});
    const ws = new WebSocket(`${API_BASE.replace('http','ws')}`);
    ws.onmessage = (ev) => {
      const msg = JSON.parse(ev.data);
      if (msg.type === 'orderbook' && msg.payload.symbol === symbol) setOb(msg.payload.snapshot);
      if (msg.type === 'trade' && msg.symbol === symbol) setTrades((t)=>[msg, ...t].slice(0,100));
    };
    return () => ws.close();
  }, [symbol]);

  const login = async () => {
    const res = await fetch(`${API_BASE}/api/auth/login`, {
      method: 'POST', headers: {'Content-Type':'application/json'},
      body: JSON.stringify({ email, password })
    });
    if (!res.ok) {
      // auto register then login
      await fetch(`${API_BASE}/api/auth/register`, {
        method: 'POST', headers: {'Content-Type':'application/json'},
        body: JSON.stringify({ email, password })
      });
      const res2 = await fetch(`${API_BASE}/api/auth/login`, {
        method: 'POST', headers: {'Content-Type':'application/json'},
        body: JSON.stringify({ email, password })
      });
      const j2 = await res2.json(); setToken(j2.token); return;
    }
    const j = await res.json(); setToken(j.token);
  };

  const place = async (side: 'BUY'|'SELL') => {
    const price = Number(priceRef.current?.value || 0);
    const quantity = Number(qtyRef.current?.value || 0);
    const res = await fetch(`${API_BASE}/api/orders`, {
      method: 'POST',
      headers: {'Content-Type':'application/json', 'Authorization': `Bearer ${token}`},
      body: JSON.stringify({ symbol, side, type:'LIMIT', price, quantity })
    });
    const j = await res.json();
    alert(res.ok ? `Order placed: ${j.order.id}` : `Error: ${j.error}`);
  };

  return (
    <div style={{ maxWidth: 1000, margin: '24px auto', fontFamily: 'Inter, system-ui, Arial' }}>
      <h1>Mini Crypto Exchange (Demo)</h1>
      <div style={{ display:'flex', gap: 16, alignItems: 'center' }}>
        <input value={email} onChange={e=>setEmail(e.target.value)} placeholder="email" />
        <input type="password" value={password} onChange={e=>setPassword(e.target.value)} placeholder="password" />
        <button onClick={login}>{token ? 'Logged In' : 'Login / Register'}</button>
        <select value={symbol} onChange={e=>setSymbol(e.target.value)}>
          <option>BTCUSDT</option>
          <option>ETHUSDT</option>
        </select>
      </div>

      <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap: 16, marginTop: 16 }}>
        <div>
          <h3>Order Book</h3>
          <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap: 8 }}>
            <div>
              <strong>Bids</strong>
              <table><thead><tr><th>Price</th><th>Qty</th></tr></thead>
                <tbody>
                  {ob.bids.map((l,i)=>(<tr key={'b'+i}><td>{l.price.toFixed(2)}</td><td>{l.qty.toFixed(6)}</td></tr>))}
                </tbody>
              </table>
            </div>
            <div>
              <strong>Asks</strong>
              <table><thead><tr><th>Price</th><th>Qty</th></tr></thead>
                <tbody>
                  {ob.asks.map((l,i)=>(<tr key={'a'+i}><td>{l.price.toFixed(2)}</td><td>{l.qty.toFixed(6)}</td></tr>))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
        <div>
          <h3>Place Order</h3>
          <div style={{ display:'flex', gap: 8, alignItems: 'center' }}>
            <input ref={priceRef} type="number" placeholder="Price" step="0.01" />
            <input ref={qtyRef} type="number" placeholder="Quantity" step="0.000001" />
            <button onClick={()=>place('BUY')} disabled={!token}>Buy</button>
            <button onClick={()=>place('SELL')} disabled={!token}>Sell</button>
          </div>
          {!token && <p style={{color:'#666'}}>Login first to place orders (demo auto-registers).</p>}
          <h3 style={{marginTop:16}}>Recent Trades</h3>
          <ul>
            {trades.map(t=>(<li key={t.id}>{new Date(t.ts).toLocaleTimeString()} — {t.quantity} @ {t.price}</li>))}
          </ul>
        </div>
      </div>
      <p style={{marginTop:24, color:'#666'}}>Demo only: local matching, no real funds, no KYC, no blockchain.</p>
    </div>
  );
}
"""

tsconfig = r"""{
  "compilerOptions": {
    "target": "ES6",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": false,
    "forceConsistentCasingInFileNames": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true
  },
  "include": ["**/*.ts", "**/*.tsx"]
}
"""

env_front = "NEXT_PUBLIC_API_BASE=http://localhost:4000\n"

os.makedirs(os.path.join(frontend, "pages"), exist_ok=True)
os.makedirs(os.path.join(frontend, "lib"), exist_ok=True)

open(os.path.join(frontend, "package.json"), "w").write(json.dumps(frontend_pkg, indent=2))
open(os.path.join(frontend, "next.config.mjs"), "w").write(next_config)
open(os.path.join(frontend, "tsconfig.json"), "w").write(tsconfig)
open(os.path.join(frontend, "pages", "index.tsx"), "w").write(index_tsx)
open(os.path.join(frontend, "lib", "api.ts"), "w").write(api_ts)
open(os.path.join(frontend, ".env.local.example"), "w").write(env_front)

# Root README
readme = """# Mini Crypto Exchange (Demo)

> Educational project: **local order matching**, **no real money**, **no blockchain/banks/KYC**.

## Features
- Register/Login (JWT)
- Place LIMIT Buy/Sell orders (BTCUSDT/ETHUSDT)
- In-memory order book + persisted orders & trades (SQLite)
- Simple matching engine
- WebSocket updates for order book & trades
- Next.js frontend

## Tech
- Backend: Node.js, Express, SQLite, ws, JWT, bcrypt
- Frontend: Next.js (React 18)
- Single-machine demo (runs in two terminals)

## Quick Start

### 1) Backend
```bash
cd backend
cp .env.example .env   # optional, edit JWT_SECRET/PORT
npm install
npm run dev            # starts http://localhost:4000
