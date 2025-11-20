# YFITG Scout Portal

Next.js consent portal for authorizing network security scans.

## Setup

1. Install dependencies:
```bash
npm install
```

2. Copy `.env.example` to `.env.local` and configure:
- MQTT broker credentials
- Database URL (if using database for consent storage)

3. Run development server:
```bash
npm run dev
```

## Deployment to Vercel

1. Connect your repository to Vercel
2. Set environment variables in Vercel dashboard
3. Deploy

## Environment Variables

- `MQTT_BROKER` - MQTT broker hostname
- `MQTT_PORT` - MQTT broker port (default: 8883)
- `MQTT_USERNAME` - MQTT username
- `MQTT_PASSWORD` - MQTT password
- `MQTT_USE_TLS` - Use TLS (true/false)
- `DATABASE_URL` - Database connection string (optional)
- `NEXT_PUBLIC_APP_URL` - Public URL of the portal

## Features

- Prefill support via query parameters (?name=&email=&company=&device=&cidr=)
- Consent form with validation
- MQTT integration for scan triggering
- Branded UI with YFITG colors

