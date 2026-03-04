# Algeria Music Backend (Fly.io)

## Deploy Steps

1. Install Fly CLI:
   curl -L https://fly.io/install.sh | sh

2. Login:
   fly auth login

3. Inside this folder:
   fly launch

4. Deploy:
   fly deploy

## Endpoints

Search:
GET /search?q=cheb hasni

Get Audio:
GET /audio/VIDEO_ID
