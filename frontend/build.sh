
npm run build:ssr
docker build -t exhome12 .
docker tag exhome12:latest nguyenthean269/exhome:t.1.35
docker push nguyenthean269/exhome:t.1.35