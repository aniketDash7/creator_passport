# Authenticity Protocol: Trust Engine

The **Trust Engine** is an API-first platform for establishing content provenance and authenticity using the [C2PA Standard](https://c2pa.org/). It acts as a "Content Firewall" and identity provider for creators.

## 🌟 Features
*   **Identity Management**: Issues X.509 certificates to creators (`/identity/register`).
*   **Content Signing**: Cryptographically binds identity and provenance data to media (`/content/sign`).
*   **Verification**: Validates C2PA manifests and chains of trust (`/content/verify`).
*   **Creator Passport**: A built-in dashboard for managing identity and assets.
*   **Truth Lens SDK**: A JavaScript widget for third-party integrations.

## 🚀 Quick Start (Docker)
The easiest way to run the engine is via Docker.

```bash
# 1. Build the image
docker build -t trust-engine .

# 2. Run the container (Port 8080)
docker run -p 8080:8080 -v $(pwd)/storage:/app/storage trust-engine
```

Visit the Dashboard: [http://localhost:8080/passport/](http://localhost:8080/passport/)

## 🛠 Manual Setup (Python)
If you prefer running locally without Docker:

```bash
# 1. Install Dependencies
pip install -r requirements.txt

# 2. Run Server
python -m uvicorn trust_engine.main:app --host 127.0.0.1 --port 8080
```

## 📚 API Documentation
Full interactive API docs (Swagger UI) are available at:
[http://localhost:8080/docs](http://localhost:8080/docs)

### Key Endpoints
| Method | Endpoint | Description |
|:---|:---|:---|
| `POST` | `/api/identity/register` | Create a new signing identity (Keys + Certs). |
| `POST` | `/api/content/sign` | Sign an image file with your identity. |
| `POST` | `/api/content/verify` | Upload an image to check its C2PA manifest. |

## 📦 Project Structure
*   `trust_engine/`: Main application package.
    *   `services/`: Core logic (`CryptoService`, `C2PAService`).
    *   `routers/`: API route definitions.
    *   `static/`: Frontend assets (Dashboard & SDK).
*   `storage/`: (Volume) Stores generated keys and certificates.

## 🛡️ Integration (SDK)
To add verification to your own website, include the SDK:

```html
<script src="http://localhost:8080/passport/sdk.js"></script>
<img src="my-secure-image.jpg" data-c2pa-verify>
```
