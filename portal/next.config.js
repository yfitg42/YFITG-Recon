/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  env: {
    MQTT_BROKER: process.env.MQTT_BROKER,
    MQTT_PORT: process.env.MQTT_PORT,
    MQTT_USERNAME: process.env.MQTT_USERNAME,
    MQTT_PASSWORD: process.env.MQTT_PASSWORD,
    MQTT_USE_TLS: process.env.MQTT_USE_TLS === 'true',
  },
}

module.exports = nextConfig

