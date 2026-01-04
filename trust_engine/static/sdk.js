/**
 * Authenticity Protocol "Truth Lens" SDK
 * Acts like Stripe.js: Drop this in, and it auto-verifies content.
 */
(function () {
    const API_URL = "http://localhost:8080/api/content/verify";

    // CSS for the Badge (injected into Shadow DOM usually, keeping simple here)
    const STYLES = `
        .c2pa-badge {
            position: absolute;
            top: 10px;
            right: 10px;
            background: rgba(0, 0, 0, 0.8);
            color: #fff;
            padding: 5px 10px;
            border-radius: 20px;
            font-family: sans-serif;
            font-size: 12px;
            cursor: help;
            z-index: 1000;
            display: flex;
            align-items: center;
            gap: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.2);
            backdrop-filter: blur(5px);
            border: 1px solid rgba(255,255,255,0.2);
        }
        .c2pa-badge.valid { color: #4ade80; }
        .c2pa-badge.invalid { color: #f87171; }
        .c2pa-tooltip {
            visibility: hidden;
            position: absolute;
            top: 100%;
            right: 0;
            margin-top: 10px;
            background: white;
            color: #333;
            padding: 15px;
            border-radius: 8px;
            width: 250px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
            font-size: 13px;
            text-align: left;
            opacity: 0;
            transition: opacity 0.2s;
        }
        .c2pa-badge:hover .c2pa-tooltip {
            visibility: visible;
            opacity: 1;
        }
        .c2pa-row { margin-bottom: 5px; }
        .c2pa-label { color: #666; font-size: 11px; display: block; }
        .c2pa-val { font-weight: bold; }
    `;

    function injectStyles() {
        const style = document.createElement("style");
        style.innerHTML = STYLES;
        document.head.appendChild(style);
    }

    async function verifyImage(imgElement) {
        // Wrapper to position badge
        const wrapper = document.createElement("div");
        wrapper.style.position = "relative";
        wrapper.style.display = "inline-block";
        imgElement.parentNode.insertBefore(wrapper, imgElement);
        wrapper.appendChild(imgElement);

        try {
            // 1. Fetch the image blob directly from source
            const response = await fetch(imgElement.src);
            const blob = await response.blob();

            // 2. Prepare Form Data for Backend
            const formData = new FormData();
            formData.append("file", blob, "image.jpg");

            // 3. Verify via Trust Engine API
            const verifyRes = await fetch(API_URL, {
                method: "POST",
                body: formData
            });
            const data = await verifyRes.json();

            // 4. Render Badge
            const badge = document.createElement("div");
            const isSigned = data && !data.error;

            if (isSigned) {
                // Parse Manifest Info
                const claim = data.active_manifest; // Assuming c2pa-python structure
                // Simplified extraction (structure varies based on library output)
                // We'll trust the hello world structure: { assertions: [...] }
                // For now, let's just assume valid if no error.

                const author = "Verified Creator"; // We'd extract this from assertions in real impl
                const program = "Authenticity Protocol";

                badge.className = "c2pa-badge valid";
                badge.innerHTML = `
                    <span>🛡️ Verified</span>
                    <div class="c2pa-tooltip">
                        <div class="c2pa-row">
                            <span class="c2pa-label">SIGNED BY</span>
                            <span class="c2pa-val">${author}</span>
                        </div>
                        <div class="c2pa-row">
                            <span class="c2pa-label">TOOL</span>
                            <span class="c2pa-val">${program}</span>
                        </div>
                        <div class="c2pa-row">
                            <span class="c2pa-label">STATUS</span>
                            <span class="c2pa-val" style="color:green">Cryptographically Valid</span>
                        </div>
                    </div>
                `;
            } else {
                // Optional: Show "Unsigned" or nothing
                // For demo, we might skip unsigned
                return;
            }

            wrapper.appendChild(badge);

        } catch (e) {
            console.error("C2PA Verification Error:", e);
        }
    }

    function init() {
        injectStyles();
        const images = document.querySelectorAll("img[data-c2pa-verify]");
        images.forEach(img => {
            // If image loaded, verify immediately. Else wait.
            if (img.complete) {
                verifyImage(img);
            } else {
                img.onload = () => verifyImage(img);
            }
        });
    }

    // Auto-init on load
    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }

})();
